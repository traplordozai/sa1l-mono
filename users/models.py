from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import uuid
import random

class UserRole(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class UserInvite(models.Model):
    email = models.EmailField(unique=True)
    role = models.ForeignKey(UserRole, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class OTP(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=5)

class User(AbstractUser):
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("mentor", "Mentor"),
        ("intern", "Intern"),
        ("staff", "Staff"),
    ]

    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("suspended", "Suspended"),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="intern")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    avatar = models.URLField(blank=True, null=True)

class EmailVerificationToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return self.created_at < timezone.now() - timezone.timedelta(hours=24)

class UserActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)