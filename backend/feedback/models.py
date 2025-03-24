from django.db import models

class FeedbackForm(models.Model):
    name = models.CharField(max_length=255)
    schema = models.JSONField()  # structure: questions, types, etc.
    anonymous = models.BooleanField(default=False)
    created_by = models.ForeignKey("users.User", on_delete=models.CASCADE)

class FeedbackResponse(models.Model):
    form = models.ForeignKey(FeedbackForm, on_delete=models.CASCADE)
    user = models.ForeignKey("users.User", null=True, blank=True, on_delete=models.SET_NULL)
    answers = models.JSONField()
    submitted_at = models.DateTimeField(auto_now_add=True)

class FeedbackEntry(models.Model):
    FEEDBACK_TYPES = [
        ("peer", "Peer"),
        ("mentor", "Mentor"),
        ("self", "Self"),
        ("manager", "Manager"),
    ]

    reviewer = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="feedback_given")
    target = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="feedback_received")
    type = models.CharField(max_length=20, choices=FEEDBACK_TYPES)
    score = models.IntegerField()
    comments = models.TextField()
    anonymous = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_type_display()} feedback from {self.reviewer} to {self.target}"

    class Meta:
        verbose_name = "Feedback Entry"
        verbose_name_plural = "Feedback Entries"
        ordering = ['-submitted_at']
