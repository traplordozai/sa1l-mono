from typing import List

from core.models import BaseModel
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, MinValueValidator
from django.db import models
from statements.models import AreaOfLaw


class Organization(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    areas_of_law = models.ManyToManyField(AreaOfLaw, related_name="organizations")
    location = models.CharField(max_length=255)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    website = models.URLField(blank=True, null=True)
    requirements = models.TextField(blank=True, null=True)
    available_positions = models.IntegerField(
        default=1, validators=[MinValueValidator(0)]
    )
    filled_positions = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Organization"
        verbose_name_plural = "Organizations"

    def __str__(self):
        return self.name

    @property
    def remaining_positions(self):
        """Return the number of unfilled positions"""
        return max(0, self.available_positions - self.filled_positions)

    @property
    def is_accepting_applications(self):
        """Check if the organization is accepting applications"""
        return self.is_active and self.remaining_positions > 0

    def validate(self) -> List[str]:
        """
        Validate the organization according to business rules.
        Returns a list of validation error messages or empty list if valid.
        """
        errors = super().validate()

        # Validate required fields
        if not self.name:
            errors.append("Organization name is required")

        if not self.description:
            errors.append("Organization description is required")

        if not self.location:
            errors.append("Organization location is required")

        # Validate positions
        if self.available_positions < 0:
            errors.append("Available positions cannot be negative")

        if self.filled_positions < 0:
            errors.append("Filled positions cannot be negative")

        if self.filled_positions > self.available_positions:
            errors.append("Filled positions cannot exceed available positions")

        return errors

    def add_position(self, count: int = 1) -> None:
        """Add available positions with validation"""
        if count <= 0:
            raise ValidationError("Position count must be positive")

        self.available_positions += count
        self.save(update_fields=["available_positions", "updated_at"])

    def fill_position(self) -> None:
        """Mark a position as filled with validation"""
        if self.filled_positions >= self.available_positions:
            raise ValidationError("All positions are already filled")

        self.filled_positions += 1
        self.save(update_fields=["filled_positions", "updated_at"])


class OrganizationContact(BaseModel):
    """Contact person for an organization"""

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="contacts"
    )
    name = models.CharField(max_length=255)
    title = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_primary = models.BooleanField(default=False)

    class Meta:
        ordering = ["-is_primary", "name"]
        verbose_name = "Organization Contact"
        verbose_name_plural = "Organization Contacts"

    def __str__(self):
        return f"{self.name} ({self.organization.name})"

    def save(self, *args, **kwargs):
        """Ensure only one primary contact per organization"""
        if self.is_primary:
            # Set all other contacts for this organization to not primary
            OrganizationContact.objects.filter(
                organization=self.organization, is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)
