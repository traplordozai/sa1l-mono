from django.db import models
from users.models import User

class Organization(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    area_of_law = models.CharField(max_length=255, blank=True)
    work_mode = models.CharField(max_length=50, choices=[("remote", "Remote"), ("in_person", "In Person"), ("hybrid", "Hybrid")], default="hybrid")
    position_requirements = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name or f"Organization {self.pk}"
