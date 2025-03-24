from django.db import models
from django.utils import timezone

class Document(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("approved", "Approved"),
        ("expired", "Expired"),
    ]

    internship = models.ForeignKey("internships.Internship", on_delete=models.CASCADE, related_name="documents")
    label = models.CharField(max_length=255)
    file = models.FileField(upload_to="documents/%Y/%m/")
    uploaded_by = models.ForeignKey("users.User", on_delete=models.CASCADE)
    type = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    expires_at = models.DateTimeField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return self.expires_at and timezone.now() > self.expires_at