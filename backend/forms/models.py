"""
Schema JSON structure example:
{
  "fields": [
    {
      "id": "full_name",
      "label": "Full Name",
      "type": "text",
      "required": true
    },
    {
      "id": "experience",
      "label": "Years of Experience",
      "type": "number",
      "required": false,
      "visible_if": {
        "field": "role",
        "equals": "mentor"
      }
    }
  ]
}
"""

from django.db import models
from django.core.exceptions import ValidationError
import jsonschema

class DynamicForm(models.Model):
    name = models.CharField(max_length=255)
    schema = models.JSONField()  # JSONSchema-like

    def clean(self):
        try:
            jsonschema.Draft7Validator.check_schema(self.schema)
        except jsonschema.exceptions.SchemaError as e:
            raise ValidationError(f"Invalid JSON schema: {str(e)}")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-id']
        verbose_name = "Dynamic Form"
        verbose_name_plural = "Dynamic Forms"

class DynamicSubmission(models.Model):
    form = models.ForeignKey(DynamicForm, on_delete=models.CASCADE, related_name='submissions')
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name='form_submissions')
    answers = models.JSONField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        try:
            jsonschema.validate(self.answers, self.form.schema)
        except jsonschema.exceptions.ValidationError as e:
            raise ValidationError(f"Invalid answers format: {str(e)}")

    def __str__(self):
        return f"Submission by {self.user} for {self.form.name}"

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = "Form Submission"
        verbose_name_plural = "Form Submissions"
