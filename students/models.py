from django.db import models
from users.models import CustomUser

class Student(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    major = models.CharField(max_length=100)
    gpa = models.DecimalField(max_digits=4, decimal_places=2)
    matched = models.BooleanField(default=False)
    survey_data = models.JSONField(default=dict)