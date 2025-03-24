from django.db import models
from django.utils import timezone

class Milestone(models.Model):
    TYPE_CHOICES = [
        ("check-in", "Check-in"),
        ("deliverable", "Deliverable"),
        ("feedback", "Feedback"),
        ("event", "Event"),
    ]

    internship = models.ForeignKey("internships.Internship", on_delete=models.CASCADE, related_name="milestones")
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    scheduled_at = models.DateTimeField()
    notes = models.TextField(blank=True)
    has_issue = models.BooleanField(default=False)

    @property
    def status(self):
        now = timezone.now()
        if self.scheduled_at < now:
            return "past"
        elif (self.scheduled_at - now).days <= 1:
            return "current"
        return "upcoming"

    def __str__(self):
        return f"{self.title} ({self.get_type_display()})"

    class Meta:
        ordering = ['scheduled_at']
        verbose_name = "Milestone"
        verbose_name_plural = "Milestones"