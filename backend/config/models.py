from django.db import models

class EnvironmentSetting(models.Model):
    MODE_CHOICES = [
        ("dev", "Development"),
        ("prod", "Production"),
        ("maint", "Maintenance")
    ]
    mode = models.CharField(max_length=10, choices=MODE_CHOICES, default="dev")

    def __str__(self):
        return self.mode

    @classmethod
    def current(cls):
        obj, _ = cls.objects.get_or_create(id=1)
        return obj.mode