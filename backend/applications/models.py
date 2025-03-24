from django.db import models
from django.utils import timezone

class ApplicationNote(models.Model):
    application = models.ForeignKey("applications.Application", on_delete=models.CASCADE, related_name="notes")
    author = models.ForeignKey("users.User", on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

class ApplicationStatusHistory(models.Model):
    application = models.ForeignKey("applications.Application", on_delete=models.CASCADE, related_name="status_history")
    old_status = models.CharField(max_length=20, choices=Application.STATUS_CHOICES)
    new_status = models.CharField(max_length=20, choices=Application.STATUS_CHOICES)
    changed_by = models.ForeignKey("users.User", on_delete=models.CASCADE)
    changed_at = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(blank=True)

    class Meta:
        ordering = ['-changed_at']
        verbose_name_plural = "Application status histories"

class Application(models.Model):
    STATUS_CHOICES = [
        ("applied", "Applied"),
        ("interviewing", "Interviewing"),
        ("offered", "Offered"),
        ("hired", "Hired"),
        ("rejected", "Rejected"),
        ("stale", "Stale"),
    ]

    candidate = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="applications")
    position = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="applied")
    offer_sent_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def mark_stale_if_expired(self):
        if self.expires_at and timezone.now() > self.expires_at:
            self.status = "stale"
            self.save()

    def __str__(self):
        return f"{self.candidate.username} - {self.position} ({self.status})"

    class Meta:
        ordering = ['-updated_at']
        verbose_name = "Application"
        verbose_name_plural = "Applications"

    def save(self, *args, **kwargs):
        # Track status changes
        if self.pk:
            old_instance = Application.objects.get(pk=self.pk)
            if old_instance.status != self.status:
                ApplicationStatusHistory.objects.create(
                    application=self,
                    old_status=old_instance.status,
                    new_status=self.status,
                    changed_by=kwargs.pop('changed_by', None)
                )
        
        # Set expires_at when offer is sent
        if self.status == "offered" and self.offer_sent_at and not self.expires_at:
            self.expires_at = self.offer_sent_at + timezone.timedelta(days=7)
        
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        return self.status not in ["rejected", "hired", "stale"]

    @classmethod
    def mark_all_stale(cls):
        """Utility method to mark all expired applications as stale"""
        now = timezone.now()
        expired = cls.objects.filter(
            expires_at__lt=now,
            status="offered"
        )
        expired.update(status="stale")
        return expired.count()