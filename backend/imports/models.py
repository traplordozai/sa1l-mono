from django.contrib.auth import get_user_model
from django.db import models

from backend.core.models import BaseModel

User = get_user_model()


class ImportType(models.TextChoices):
    STUDENT_CSV = "student_csv", "Student CSV Import"
    ORGANIZATION_CSV = "organization_csv", "Organization CSV Import"
    GRADES_PDF = "grades_pdf", "Student Grades PDF Import"
    STATEMENT_CSV = "statement_csv", "Student Statements CSV Import"


class ImportStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PROCESSING = "processing", "Processing"
    COMPLETED = "completed", "Completed"
    FAILED = "failed", "Failed"
    PARTIALLY_COMPLETED = "partially_completed", "Partially Completed"


class ImportLog(BaseModel):
    """
    Tracks all data import operations with detailed results
    """

    import_type = models.CharField(max_length=50, choices=ImportType.choices)
    file_name = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(help_text="File size in bytes")
    original_file_name = models.CharField(
        max_length=255, help_text="Original name of uploaded file"
    )
    status = models.CharField(
        max_length=50, choices=ImportStatus.choices, default=ImportStatus.PENDING
    )

    # Import statistics
    processed_count = models.PositiveIntegerField(
        default=0, help_text="Number of records processed"
    )
    success_count = models.PositiveIntegerField(
        default=0, help_text="Number of records successfully imported"
    )
    error_count = models.PositiveIntegerField(
        default=0, help_text="Number of records with errors"
    )
    warnings_count = models.PositiveIntegerField(
        default=0, help_text="Number of warnings during import"
    )

    # Execution tracking
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    execution_time = models.PositiveIntegerField(
        null=True, blank=True, help_text="Execution time in seconds"
    )

    # Error details
    errors = models.JSONField(
        default=dict, blank=True, help_text="Detailed errors during import"
    )
    warnings = models.JSONField(
        default=dict, blank=True, help_text="Warnings generated during import"
    )

    # User tracking
    imported_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="imports",
        help_text="User who initiated the import",
    )

    # For async task tracking
    task_id = models.CharField(
        max_length=255, null=True, blank=True, help_text="Celery task ID"
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Import Log"
        verbose_name_plural = "Import Logs"
        indexes = [
            models.Index(fields=["import_type"]),
            models.Index(fields=["status"]),
            models.Index(fields=["imported_by"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.get_import_type_display()} - {self.file_name} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"

    @property
    def is_completed(self):
        return self.status in [ImportStatus.COMPLETED, ImportStatus.PARTIALLY_COMPLETED]

    @property
    def is_failed(self):
        return self.status == ImportStatus.FAILED

    @property
    def success_rate(self):
        if self.processed_count == 0:
            return 0
        return round((self.success_count / self.processed_count) * 100, 2)


class ImportDetail(BaseModel):
    """
    Detailed record for each imported entity
    """

    import_log = models.ForeignKey(
        ImportLog, on_delete=models.CASCADE, related_name="details"
    )
    entity_type = models.CharField(
        max_length=50, help_text="Type of entity imported (student, organization, etc.)"
    )
    entity_id = models.CharField(
        max_length=100, null=True, blank=True, help_text="ID of the imported entity"
    )

    row_number = models.PositiveIntegerField(
        null=True, blank=True, help_text="Row number in CSV import"
    )
    original_data = models.JSONField(help_text="Original data from import source")
    processed_data = models.JSONField(
        null=True, blank=True, help_text="Data after processing"
    )

    status = models.CharField(
        max_length=50,
        choices=[
            ("success", "Success"),
            ("error", "Error"),
            ("warning", "Warning"),
        ],
    )
    message = models.TextField(
        null=True, blank=True, help_text="Status message or error details"
    )

    class Meta:
        ordering = ["import_log", "row_number"]
        verbose_name = "Import Detail"
        verbose_name_plural = "Import Details"
        indexes = [
            models.Index(fields=["import_log", "status"]),
            models.Index(fields=["entity_type", "entity_id"]),
        ]

    def __str__(self):
        return f"Record {self.row_number or '?'} - {self.entity_type} ({self.status})"
