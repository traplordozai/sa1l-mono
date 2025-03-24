from django.db import models
from students.models import Student

class StatementGrade(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    score = models.PositiveIntegerField()
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)