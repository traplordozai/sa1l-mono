from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

class InternshipPhase(models.Model):
    internship = models.ForeignKey("internships.Internship", on_delete=models.CASCADE, related_name="phases")
    name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    sla_hours = models.IntegerField(null=True, blank=True, help_text="Service Level Agreement in hours")

    def is_late(self):
        if self.sla_hours:
            due = self.start_date + timezone.timedelta(hours=self.sla_hours)
            return timezone.now().date() > due
        return False

    def clean(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError("Start date cannot be after end date")

    def __str__(self):
        return f"{self.internship.name} - {self.name}"

    @property
    def duration_days(self):
        return (self.end_date - self.start_date).days

    @property
    def is_active(self):
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date

    @property
    def progress_percentage(self):
        today = timezone.now().date()
        if today < self.start_date:
            return 0
        if today > self.end_date:
            return 100
        total_days = self.duration_days
        days_passed = (today - self.start_date).days
        return min(100, round((days_passed / total_days) * 100))

    class Meta:
        ordering = ['start_date']
        verbose_name = "Internship Phase"
        verbose_name_plural = "Internship Phases"
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_date__gte=models.F('start_date')),
                name='phase_end_date_after_start_date'
            )
        ]

class PhaseTask(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("blocked", "Blocked")
    ]

    phase = models.ForeignKey(InternshipPhase, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    assigned_to = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def complete(self, user):
        self.status = "completed"
        self.completed_at = timezone.now()
        self.save()
        
        PhaseTaskHistory.objects.create(
            task=self,
            action="completed",
            performed_by=user
        )

    class Meta:
        ordering = ['due_date', 'title']

class PhaseTaskHistory(models.Model):
    task = models.ForeignKey(PhaseTask, on_delete=models.CASCADE, related_name="history")
    action = models.CharField(max_length=50)
    performed_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = "Phase task histories"
