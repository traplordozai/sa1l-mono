from dataclasses import dataclass
from typing import Any, Dict, Optional

from django.db import transaction
from organizations.models import Organization, OrganizationContact
from organizations.repositories import (OrganizationContactRepository,
                                        OrganizationRepository)

from backend.core.cqrs import Command, CommandHandler


@dataclass
class CreateOrganizationCommand(Command):
    """Command to create a new organization"""

    organization_data: Dict[str, Any]


class CreateOrganizationCommandHandler(CommandHandler[CreateOrganizationCommand]):
    """Handler for CreateOrganizationCommand"""

    def __init__(
        self,
        organization_repository: OrganizationRepository,
        contact_repository: OrganizationContactRepository,
    ):
        self.organization_repository = organization_repository
        self.contact_repository = contact_repository

    @transaction.atomic
    async def handle(self, command: CreateOrganizationCommand) -> Organization:
        """Handle the create organization command"""
        data = command.organization_data.copy()

        # Extract contact data if present
        contact_data = data.pop("contact", None)

        # Create organization
        organization = self.organization_repository.create(data)

        # Create primary contact if provided
        if contact_data:
            contact_data["organization"] = organization
            contact_data["is_primary"] = True
            self.contact_repository.create(contact_data)

        return organization


@dataclass
class UpdateOrganizationCommand(Command):
    """Command to update an organization"""

    organization_id: str
    organization_data: Dict[str, Any]


class UpdateOrganizationCommandHandler(CommandHandler[UpdateOrganizationCommand]):
    """Handler for UpdateOrganizationCommand"""

    def __init__(self, organization_repository: OrganizationRepository):
        self.organization_repository = organization_repository

    @transaction.atomic
    async def handle(
        self, command: UpdateOrganizationCommand
    ) -> Optional[Organization]:
        """Handle the update organization command"""
        return self.organization_repository.update(
            command.organization_id, command.organization_data
        )


@dataclass
class DeactivateOrganizationCommand(Command):
    """Command to deactivate an organization"""

    organization_id: str


class DeactivateOrganizationCommandHandler(
    CommandHandler[DeactivateOrganizationCommand]
):
    """Handler for DeactivateOrganizationCommand"""

    def __init__(self, organization_repository: OrganizationRepository):
        self.organization_repository = organization_repository

    async def handle(self, command: DeactivateOrganizationCommand) -> bool:
        """Handle the deactivate organization command"""
        return self.organization_repository.delete(command.organization_id)


@dataclass
class AddOrganizationContactCommand(Command):
    """Command to add a contact to an organization"""

    contact_data: Dict[str, Any]


class AddOrganizationContactCommandHandler(
    CommandHandler[AddOrganizationContactCommand]
):
    """Handler for AddOrganizationContactCommand"""

    def __init__(self, contact_repository: OrganizationContactRepository):
        self.contact_repository = contact_repository

    @transaction.atomic
    async def handle(
        self, command: AddOrganizationContactCommand
    ) -> OrganizationContact:
        """Handle the add organization contact command"""
        return self.contact_repository.create(command.contact_data)


@dataclass
class UpdateContactCommand(Command):
    """Command to update a contact"""

    contact_id: str
    contact_data: Dict[str, Any]


class UpdateContactCommandHandler(CommandHandler[UpdateContactCommand]):
    """Handler for UpdateContactCommand"""

    def __init__(self, contact_repository: OrganizationContactRepository):
        self.contact_repository = contact_repository

    @transaction.atomic
    async def handle(
        self, command: UpdateContactCommand
    ) -> Optional[OrganizationContact]:
        """Handle the update contact command"""
        return self.contact_repository.update(command.contact_id, command.contact_data)


@dataclass
class DeleteContactCommand(Command):
    """Command to delete a contact"""

    contact_id: str


class DeleteContactCommandHandler(CommandHandler[DeleteContactCommand]):
    """Handler for DeleteContactCommand"""

    def __init__(self, contact_repository: OrganizationContactRepository):
        self.contact_repository = contact_repository

    async def handle(self, command: DeleteContactCommand) -> bool:
        """Handle the delete contact command"""
        return self.contact_repository.delete(command.contact_id)


@dataclass
class SetPrimaryContactCommand(Command):
    """Command to set a contact as primary"""

    organization_id: str
    contact_id: str


class SetPrimaryContactCommandHandler(CommandHandler[SetPrimaryContactCommand]):
    """Handler for SetPrimaryContactCommand"""

    def __init__(self, contact_repository: OrganizationContactRepository):
        self.contact_repository = contact_repository

    @transaction.atomic
    async def handle(self, command: SetPrimaryContactCommand) -> bool:
        """Handle the set primary contact command"""
        try:
            # First, unset any existing primary contacts
            OrganizationContact.objects.filter(
                organization_id=command.organization_id, is_primary=True
            ).update(is_primary=False)

            # Then set the specified contact as primary
            contact = OrganizationContact.objects.get(
                id=command.contact_id, organization_id=command.organization_id
            )
            contact.is_primary = True
            contact.save()
            return True
        except OrganizationContact.DoesNotExist:
            return False
