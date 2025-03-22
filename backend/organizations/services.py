import logging
from typing import Any, Dict, List, Optional

from core.handlers import EventBus
from django.db import transaction

from backend.core.cqrs import CommandDispatcher, QueryDispatcher

from .commands.organization_commands import (AddOrganizationContactCommand,
                                             CreateOrganizationCommand,
                                             DeactivateOrganizationCommand,
                                             DeleteContactCommand,
                                             SetPrimaryContactCommand,
                                             UpdateContactCommand,
                                             UpdateOrganizationCommand)
from .models import Organization, OrganizationContact
from .queries.organization_queries import (GetAllActiveOrganizationsQuery,
                                           GetOrganizationByIdQuery,
                                           GetOrganizationContactsQuery,
                                           GetOrganizationsByAreasQuery,
                                           GetOrganizationStatisticsQuery,
                                           GetOrganizationsWithPositionsQuery,
                                           GetPrimaryContactQuery,
                                           SearchOrganizationsQuery)
from .repositories import OrganizationContactRepository, OrganizationRepository

logger = logging.getLogger(__name__)


class OrganizationService:
    """Service class for organization-related business logic"""

    def __init__(self):
        # Repositories
        self.organization_repository = OrganizationRepository()
        self.contact_repository = OrganizationContactRepository()
        self.event_bus = EventBus()
        
        # Command dispatcher
        self.command_dispatcher = CommandDispatcher()
        self.command_dispatcher.register(
            CreateOrganizationCommand,
            CreateOrganizationCommandHandler(
                self.organization_repository, self.contact_repository
            )
        )
        self.command_dispatcher.register(
            UpdateOrganizationCommand,
            UpdateOrganizationCommandHandler(self.organization_repository)
        )
        self.command_dispatcher.register(
            DeactivateOrganizationCommand,
            DeactivateOrganizationCommandHandler(self.organization_repository)
        )
        self.command_dispatcher.register(
            AddOrganizationContactCommand,
            AddOrganizationContactCommandHandler(self.contact_repository)
        )
        self.command_dispatcher.register(
            UpdateContactCommand,
            UpdateContactCommandHandler(self.contact_repository)
        )
        self.command_dispatcher.register(
            DeleteContactCommand,
            DeleteContactCommandHandler(self.contact_repository)
        )
        self.command_dispatcher.register(
            SetPrimaryContactCommand,
            SetPrimaryContactCommandHandler(self.contact_repository)
        )
        
        # Query dispatcher
        self.query_dispatcher = QueryDispatcher()
        self.query_dispatcher.register(
            GetOrganizationByIdQuery,
            GetOrganizationByIdQueryHandler(self.organization_repository)
        )
        self.query_dispatcher.register(
            GetAllActiveOrganizationsQuery,
            GetAllActiveOrganizationsQueryHandler(self.organization_repository)
        )
        self.query_dispatcher.register(
            GetOrganizationsByAreasQuery,
            GetOrganizationsByAreasQueryHandler(self.organization_repository)
        )
        self.query_dispatcher.register(
            GetOrganizationsWithPositionsQuery,
            GetOrganizationsWithPositionsQueryHandler(self.organization_repository)
        )
        self.query_dispatcher.register(
            SearchOrganizationsQuery,
            SearchOrganizationsQueryHandler(self.organization_repository)
        )
        self.query_dispatcher.register(
            GetOrganizationStatisticsQuery,
            GetOrganizationStatisticsQueryHandler(self.organization_repository)
        )
        self.query_dispatcher.register(
            GetOrganizationContactsQuery,
            GetOrganizationContactsQueryHandler(self.contact_repository)
        )
        self.query_dispatcher.register(
            GetPrimaryContactQuery,
            GetPrimaryContactQueryHandler(self.contact_repository)
        )

    async def get_organization_by_id(self, organization_id: str) -> Optional[Organization]:
        """Get organization by ID"""
        query = GetOrganizationByIdQuery(organization_id=organization_id)
        return await self.query_dispatcher.dispatch(query)

    async def get_all_active_organizations(self) -> List[Organization]:
        """Get all active organizations"""
        query = GetAllActiveOrganizationsQuery()
        return await self.query_dispatcher.dispatch(query)

    async def get_organizations_by_areas(self, area_ids: List[str]) -> List<Organization]:
        """Get organizations matching specified areas of law"""
        query = GetOrganizationsByAreasQuery(area_ids=area_ids)
        return await self.query_dispatcher.dispatch(query)

    async def get_organizations_with_positions(self) -> List<Organization]:
        """Get organizations with available positions"""
        query = GetOrganizationsWithPositionsQuery()
        return await self.query_dispatcher.dispatch(query)

    async def search_organizations(self, query_str: str) -> List<Organization]:
        """Search organizations by name, description or location"""
        query = SearchOrganizationsQuery(query=query_str)
        return await self.query_dispatcher.dispatch(query)

    async def create_organization(self, organization_data: Dict[str, Any]) -> Organization:
        """Create a new organization"""
        command = CreateOrganizationCommand(organization_data=organization_data)
        return await self.command_dispatcher.dispatch(command)

    async def update_organization(self, organization_id: str, organization_data: Dict[str, Any]) -> Optional<Organization]:
        """Update an existing organization"""
        command = UpdateOrganizationCommand(
            organization_id=organization_id,
            organization_data=organization_data
        )
        return await self.command_dispatcher.dispatch(command)

    async def deactivate_organization(self, organization_id: str) -> bool:
        """Deactivate an organization"""
        command = DeactivateOrganizationCommand(organization_id=organization_id)
        return await self.command_dispatcher.dispatch(command)

    async def get_organization_statistics(self) -> Dict[str, Any]:
        """Get statistics about organizations"""
        query = GetOrganizationStatisticsQuery()
        return await self.query_dispatcher.dispatch(query)

    # Contact-related methods

    async def get_organization_contacts(self, organization_id: str) -> List<OrganizationContact]:
        """Get all contacts for an organization"""
        query = GetOrganizationContactsQuery(organization_id=organization_id)
        return await self.query_dispatcher.dispatch(query)

    async def get_primary_contact(self, organization_id: str) -> Optional<OrganizationContact]:
        """Get primary contact for an organization"""
        query = GetPrimaryContactQuery(organization_id=organization_id)
        return await self.query_dispatcher.dispatch(query)

    async def add_organization_contact(self, contact_data: Dict[str, Any]) -> OrganizationContact:
        """Add a new contact to an organization"""
        command = AddOrganizationContactCommand(contact_data=contact_data)
        return await self.command_dispatcher.dispatch(command)

    async def update_contact(self, contact_id: str, contact_data: Dict[str, Any]) -> Optional<OrganizationContact]:
        """Update an existing contact"""
        command = UpdateContactCommand(contact_id=contact_id, contact_data=contact_data)
        return await self.command_dispatcher.dispatch(command)

    async def delete_contact(self, contact_id: str) -> bool:
        """Delete a contact"""
        command = DeleteContactCommand(contact_id=contact_id)
        return await self.command_dispatcher.dispatch(command)

    async def set_primary_contact(self, organization_id: str, contact_id: str) -> bool:
        """Set a contact as the primary contact for an organization"""
        command = SetPrimaryContactCommand(
            organization_id=organization_id,
            contact_id=contact_id
        )
        return await self.command_dispatcher.dispatch(command)