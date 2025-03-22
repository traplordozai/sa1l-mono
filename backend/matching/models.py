from core.models import BaseModel
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from organizations.models import Organization
from statements.models import Statement
from students.models import Student

User = get_user_model()


class MatchingRound(BaseModel):
    """
    Represents a distinct execution of the matching algorithm.
    """

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("IN_PROGRESS", "In Progress"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    initiated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="initiated_rounds"
    )

    # Algorithm configuration
    algorithm_type = models.CharField(max_length=50, default="weighted_preference")
    algorithm_settings = models.JSONField(default=dict)

    # Results summary
    total_students = models.IntegerField(default=0)
    matched_students = models.IntegerField(default=0)
    total_organizations = models.IntegerField(default=0)
    average_match_score = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"

    def start(self, user=None):
        """Start the matching round"""
        self.status = "IN_PROGRESS"
        self.started_at = timezone.now()
        self.initiated_by = user
        self.save(update_fields=["status", "started_at", "initiated_by", "updated_at"])

    def complete(self, matched_count, avg_score=None):
        """Mark the matching round as completed with results"""
        self.status = "COMPLETED"
        self.completed_at = timezone.now()
        self.matched_students = matched_count
        self.average_match_score = avg_score
        self.save(
            update_fields=[
                "status",
                "completed_at",
                "matched_students",
                "average_match_score",
                "updated_at",
            ]
        )

    def fail(self):
        """Mark the matching round as failed"""
        self.status = "FAILED"
        self.completed_at = timezone.now()
        self.save(update_fields=["status", "completed_at", "updated_at"])


class MatchingPreference(BaseModel):
    """
    Represents student or organization preferences for matching.
    """

    PREFERENCE_TYPE_CHOICES = [
        ("STUDENT", "Student"),
        ("ORGANIZATION", "Organization"),
    ]

    preference_type = models.CharField(max_length=20, choices=PREFERENCE_TYPE_CHOICES)
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="matching_preferences",
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="matching_preferences",
    )
    area_of_law = models.CharField(max_length=100)
    weight = models.FloatField(default=1.0)
    rank = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = [("student", "area_of_law"), ("organization", "area_of_law")]

    def __str__(self):
        if self.preference_type == "STUDENT":
            return f"Student: {self.student} - {self.area_of_law} (Rank: {self.rank})"
        return f"Organization: {self.organization} - {self.area_of_law} (Weight: {self.weight})"

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.preference_type == "STUDENT" and not self.student:
            raise ValidationError("Student preference must have a student specified.")

        if self.preference_type == "ORGANIZATION" and not self.organization:
            raise ValidationError(
                "Organization preference must have an organization specified."
            )


class Match(BaseModel):
    """
    Represents a match between a student and an organization.
    """

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("ACCEPTED", "Accepted"),
        ("REJECTED", "Rejected"),
        ("CONFIRMED", "Confirmed"),
    ]

    round = models.ForeignKey(
        MatchingRound, on_delete=models.CASCADE, related_name="matches"
    )
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="matches"
    )
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="matches"
    )
    area_of_law = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")

    # Match quality metrics
    match_score = models.FloatField()
    student_rank = models.IntegerField(null=True, blank=True)
    organization_rank = models.IntegerField(null=True, blank=True)
    statement_score = models.FloatField(null=True, blank=True)

    # Tracking
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_matches",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Matches"
        ordering = ["-match_score"]
        unique_together = ["round", "student", "organization"]

    def __str__(self):
        return f"{self.student} ↔ {self.organization} ({self.match_score:.2f})"

    def approve(self, user):
        """Approve the match"""
        self.status = "ACCEPTED"
        self.approved_by = user
        self.approved_at = timezone.now()
        self.save(update_fields=["status", "approved_by", "approved_at", "updated_at"])

        # Update student status
        self.student.is_matched = True
        self.student.save(update_fields=["is_matched", "updated_at"])

        # Update organization filled positions
        self.organization.filled_positions += 1
        self.organization.save(update_fields=["filled_positions", "updated_at"])

        return self

    def reject(self, user, notes=None):
        """Reject the match"""
        self.status = "REJECTED"
        self.approved_by = user
        self.rejected_at = timezone.now()
        if notes:
            self.notes = notes
        self.save(
            update_fields=[
                "status",
                "approved_by",
                "rejected_at",
                "notes",
                "updated_at",
            ]
        )
        return self

    def confirm(self):
        """Confirm the match (final step)"""
        self.status = "CONFIRMED"
        self.save(update_fields=["status", "updated_at"])
        return self


class MatchingScore(BaseModel):
    """
    Detailed breakdown of how a match score was calculated.
    Used for transparency and auditing of the matching algorithm.
    """

    match = models.OneToOneField(
        Match, on_delete=models.CASCADE, related_name="score_details"
    )

    # Score components with their individual weights
    area_of_law_score = models.FloatField()
    area_of_law_weight = models.FloatField()

    statement_score = models.FloatField(null=True, blank=True)
    statement_weight = models.FloatField(null=True, blank=True)

    location_score = models.FloatField(null=True, blank=True)
    location_weight = models.FloatField(null=True, blank=True)

    work_preference_score = models.FloatField(null=True, blank=True)
    work_preference_weight = models.FloatField(null=True, blank=True)

    grade_score = models.FloatField(null=True, blank=True)
    grade_weight = models.FloatField(null=True, blank=True)

    # Additional factors
    additional_factors = models.JSONField(default=dict)

    def __str__(self):
        return f"Score details for {self.match}"
