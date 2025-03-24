from django.db import models
from django.template import Template as DjangoTemplate, Context

class Template(models.Model):
    TYPE_CHOICES = [("pdf", "PDF"), ("html", "HTML")]

    title = models.CharField(max_length=255)
    content = models.TextField(help_text="Use {{intern.name}}, {{start_date}} etc.")
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default="html")
    allowed_roles = models.ManyToManyField("users.UserRole")
    created_at = models.DateTimeField(auto_now_add=True)

    def render(self, context_data):
        template = DjangoTemplate(self.content)
        context = Context(context_data)
        return template.render(context)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Document Template"
        verbose_name_plural = "Document Templates"
