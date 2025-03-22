import uuid
from typing import List

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    """
    Base model class that provides common fields for all domain models.

    Attributes:
        id (UUIDField): Primary key using UUID instead of sequential IDs for better security and distribution
        created_at (DateTimeField): Timestamp when the record was created
        updated_at (DateTimeField): Timestamp when the record was last updated
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def validate(self) -> List[str]:
        """
        Validate the model according to business rules.
        Returns a list of validation error messages or empty list if valid.
        """
        return []

    def validate_and_raise(self) -> None:
        """
        Validate the model and raise ValidationError if invalid.
        """
        errors = self.validate()
        if errors:
            raise ValidationError(errors)


class BaseActiveModel(BaseModel):
    """
    Extension of BaseModel that includes an is_active flag.

    Attributes:
        is_active (BooleanField): Flag indicating if this record is active
        deactivated_at (DateTimeField): When this record was deactivated, if applicable
    """

    is_active = models.BooleanField(default=True)
    deactivated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def deactivate(self):
        """Deactivate this record and record the timestamp."""
        self.is_active = False
        self.deactivated_at = timezone.now()
        self.save(update_fields=["is_active", "deactivated_at", "updated_at"])

    def activate(self):
        """Activate this record and clear the deactivation timestamp."""
        self.is_active = True
        self.deactivated_at = None
        self.save(update_fields=["is_active", "deactivated_at", "updated_at"])
