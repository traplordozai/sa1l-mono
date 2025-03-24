from django.db import models

class ImportJob(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

class CandidateProfile(models.Model):
    user = models.OneToOneField("users.User", on_delete=models.CASCADE)
    resume_text = models.TextField(blank=True)
    interests = models.JSONField(default=list)
    skills = models.JSONField(default=list)

    def __str__(self):
        return f"Profile for {self.user.username}"

    class Meta:
        verbose_name = "Candidate Profile"
        verbose_name_plural = "Candidate Profiles"

class InternshipRole(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    required_skills = models.JSONField(default=list)
    ideal_traits = models.JSONField(default=list)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Internship Role"
        verbose_name_plural = "Internship Roles"
