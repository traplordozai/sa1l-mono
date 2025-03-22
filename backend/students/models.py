import re
from typing import List

from django.core.exceptions import ValidationError
from django.core.validators import (EmailValidator, MaxValueValidator,
                                    MinValueValidator, RegexValidator)
from django.db import models
from django.utils import timezone

from backend.core.models import BaseActiveModel, BaseModel


class Student(BaseActiveModel):
    """
    Student entity that represents a law student in the system.
    """

    # Personal Information
    given_names = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    backup_email = models.EmailField(blank=True, null=True)
    student_id = models.CharField(max_length=50, unique=True)

    # Program Information
    PROGRAM_CHOICES = [
        ("1L", "First Year"),
        ("2L", "Second Year"),
        ("3L", "Third Year"),
        ("LLM", "Master of Laws"),
        ("JD", "Juris Doctor"),
    ]
    program = models.CharField(max_length=50, choices=PROGRAM_CHOICES)

    # Preferences
    location_preferences = models.JSONField(
        default=list, help_text="List of preferred locations"
    )
    work_preferences = models.JSONField(
        default=list, help_text="List of work preferences (remote, hybrid, in-person)"
    )

    # Matching Status
    is_matched = models.BooleanField(default=False)
    needs_approval = models.BooleanField(default=False)
    last_active = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"
        indexes = [
            models.Index(fields=["last_name", "given_names"]),
            models.Index(fields=["student_id"]),
            models.Index(fields=["is_matched"]),
        ]

    def __str__(self):
        return f"{self.given_names} {self.last_name} ({self.student_id})"

    @property
    def full_name(self) -> str:
        """Return the student's full name"""
        return f"{self.given_names} {self.last_name}"

    def save(self, *args, **kwargs):
        """Override save to update last_active."""
        if not self.pk:  # Only on creation
            self.last_active = timezone.now()
        super().save(*args, **kwargs)

    @property
    def profile_completion(self):
        """Calculate profile completion percentage."""
        required_fields = [
            self.given_names,
            self.last_name,
            self.email,
            self.student_id,
            self.program,
            bool(self.location_preferences),
            bool(self.work_preferences),
        ]
        completed = sum(1 for field in required_fields if field)
        return int((completed / len(required_fields)) * 100)

    def validate(self) -> List[str]:
        """
        Validate the student according to business rules.
        Returns a list of validation error messages or empty list if valid.
        """
        errors = []

        # Validate student_id format (assuming it should be numeric)
        if not self.student_id or not re.match(r"^\d+$", self.student_id):
            errors.append("Student ID must be a numeric value")

        # Validate email format
        try:
            EmailValidator()(self.email)
        except ValidationError:
            errors.append("Please provide a valid email address")

        # Validate required fields
        if not self.given_names:
            errors.append("First name is required")

        if not self.last_name:
            errors.append("Last name is required")

        # Check for duplicate student IDs
        if (
            Student.objects.exclude(id=self.id)
            .filter(student_id=self.student_id)
            .exists()
        ):
            errors.append(f"Student with ID {self.student_id} already exists")

        return errors

    def mark_as_matched(self) -> None:
        """Mark the student as matched"""
        self.is_matched = True
        self.last_active = timezone.now()
        self.save(update_fields=["is_matched", "last_active", "updated_at"])

    def update_program(self, new_program: str) -> None:
        """Update the student's program with validation"""
        if not new_program:
            raise ValidationError("Program cannot be empty")

        self.program = new_program
        self.save(update_fields=["program", "updated_at"])


class AreaOfLaw(BaseModel):
    """
    Area of Law entity that represents a legal practice area.
    """

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class StudentAreaRanking(BaseModel):
    """
    StudentAreaRanking entity that represents a student's preference for an area of law.
    """

    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="area_rankings"
    )
    area = models.ForeignKey(AreaOfLaw, on_delete=models.CASCADE)
    rank = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    comments = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ("student", "area")
        ordering = ["student", "rank"]

    def __str__(self):
        return f"{self.student} - {self.area} (Rank: {self.rank})"


class Statement(BaseModel):
    """
    Statement entity that represents a student's statement of interest.
    """

    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="statements"
    )
    area_of_law = models.ForeignKey(AreaOfLaw, on_delete=models.CASCADE)
    content = models.TextField()
    statement_grade = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(25)], null=True, blank=True
    )
    graded_by = models.ForeignKey(
        "auth.User", on_delete=models.SET_NULL, null=True, blank=True
    )
    graded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("student", "area_of_law")
        ordering = ["student", "area_of_law"]

    def __str__(self):
        return f"Statement by {self.student} for {self.area_of_law}"

    def grade(self, score, grader):
        """Grade the statement."""
        self.statement_grade = score
        self.graded_by = grader
        self.graded_at = timezone.now()
        self.save(update_fields=["statement_grade", "graded_by", "graded_at"])


class StudentGrade(BaseModel):
    """
    StudentGrade entity that represents a student's grades.
    """

    student = models.OneToOneField(
        Student, on_delete=models.CASCADE, related_name="grades"
    )

    # Course Grades
    constitutional_law = models.CharField(max_length=2, blank=True, null=True)
    contracts = models.CharField(max_length=2, blank=True, null=True)
    criminal_law = models.CharField(max_length=2, blank=True, null=True)
    property_law = models.CharField(max_length=2, blank=True, null=True)
    torts = models.CharField(max_length=2, blank=True, null=True)

    # LRW Grades
    lrw_case_brief = models.CharField(max_length=5, blank=True, null=True)
    lrw_multiple_case = models.CharField(max_length=5, blank=True, null=True)
    lrw_short_memo = models.CharField(max_length=5, blank=True, null=True)

    # Metadata
    grade_pdf = models.FileField(upload_to="grades/", blank=True, null=True)

    def __str__(self):
        return f"Grades for {self.student}"

    def validate_grade(self, grade):
        """Validate a grade string."""
        valid_grades = [
            "A+",
            "A",
            "A-",
            "B+",
            "B",
            "B-",
            "C+",
            "C",
            "C-",
            "D+",
            "D",
            "D-",
            "F",
        ]
        return grade in valid_grades

    def clean(self):
        """Validate grades before saving."""
        from django.core.exceptions import ValidationError

        course_grades = [
            self.constitutional_law,
            self.contracts,
            self.criminal_law,
            self.property_law,
            self.torts,
        ]

        for grade in course_grades:
            if grade and not self.validate_grade(grade):
                raise ValidationError(f"Invalid grade format: {grade}")


class SelfProposedExternship(BaseModel):
    """
    SelfProposedExternship entity that represents a student's self-proposed externship.
    """

    student = models.OneToOneField(
        Student, on_delete=models.CASCADE, related_name="self_proposed"
    )
    organization = models.CharField(max_length=255)
    supervisor = models.CharField(max_length=100)
    supervisor_email = models.EmailField()
    address = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    description = models.TextField()

    def __str__(self):
        return f"Self-proposed externship for {self.student}"
