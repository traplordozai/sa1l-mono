from django.db import models

class Thread(models.Model):
    CONTEXT_CHOICES = [
        ("internship", "Internship"),
        ("application", "InternshipApplication"),
    ]

    context_type = models.CharField(max_length=20, choices=CONTEXT_CHOICES)
    context_id = models.IntegerField()  # FK-like, store internship/app ID
    created_by = models.ForeignKey("users.User", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey("users.User", on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class Announcement(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()
    target_roles = models.ManyToManyField("users.UserRole", blank=True)
    target_statuses = models.JSONField(default=list, blank=True)  # ["active", "intern"]
    created_at = models.DateTimeField(auto_now_add=True)

class AnnouncementRead(models.Model):
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    read_at = models.DateTimeField(auto_now_add=True)
