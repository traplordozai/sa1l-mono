from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from organizations.models import Organization, OrganizationContact
from organizations.repositories import (OrganizationContactRepository,
                                        OrganizationRepository)

from backend.core.cqrs import Query, QueryHandler


@dataclass
class GetOrganizationByIdQuery(Query):
    """Query to get an organization by ID"""

    organization_id: str


class GetOrganizationByIdQueryHandler(
    QueryHandler[GetOrganizationByIdQuery, Optional[Organization]]
):
    """Handler for GetOrganizationByIdQuery"""

    def __init__(self, organization_repository: OrganizationRepository):
        self.organization_repository = organization_repository

    async def handle(self, query: GetOrganizationByIdQuery) -> Optional[Organization]:
        """Handle the get organization by ID query"""
        return self.organization_repository.get_by_id(query.organization_id)


@dataclass
class GetAllActiveOrganizationsQuery(Query):
    """Query to get all active organizations"""

    pass


class GetAllActiveOrganizationsQueryHandler(
    QueryHandler[GetAllActiveOrganizationsQuery, List[Organization]]
):
    """Handler for GetAllActiveOrganizationsQuery"""

    def __init__(self, organization_repository: OrganizationRepository):
        self.organization_repository = organization_repository

    async def handle(self, query: GetAllActiveOrganizationsQuery) -> List[Organization]:
        """Handle the get all active organizations query"""
        return self.organization_repository.get_all_active()


@dataclass
class GetOrganizationsByAreasQuery(Query):
    """Query to get organizations by areas of law"""

    area_ids: List[str]


class GetOrganizationsByAreasQueryHandler(
    QueryHandler[GetOrganizationsByAreasQuery, List[Organization]]
):
    """Handler for GetOrganizationsByAreasQuery"""

    def __init__(self, organization_repository: OrganizationRepository):
        self.organization_repository = organization_repository

    async def handle(self, query: GetOrganizationsByAreasQuery) -> List[Organization]:
        """Handle the get organizations by areas query"""
        return self.organization_repository.get_by_areas(query.area_ids)


@dataclass
class GetOrganizationsWithPositionsQuery(Query):
    """Query to get organizations with available positions"""

    pass


class GetOrganizationsWithPositionsQueryHandler(
    QueryHandler[GetOrganizationsWithPositionsQuery, List[Organization]]
):
    """Handler for GetOrganizationsWithPositionsQuery"""

    def __init__(self, organization_repository: OrganizationRepository):
        self.organization_repository = organization_repository

    async def handle(
        self, query: GetOrganizationsWithPositionsQuery
    ) -> List[Organization]:
        """Handle the get organizations with positions query"""
        return self.organization_repository.get_with_available_positions()


@dataclass
class SearchOrganizationsQuery(Query):
    """Query to search organizations"""

    query: str


class SearchOrganizationsQueryHandler(
    QueryHandler[SearchOrganizationsQuery, List[Organization]]
):
    """Handler for SearchOrganizationsQuery"""

    def __init__(self, organization_repository: OrganizationRepository):
        self.organization_repository = organization_repository

    async def handle(self, query: SearchOrganizationsQuery) -> List[Organization]:
        """Handle the search organizations query"""
        return self.organization_repository.search(query.query)


@dataclass
class GetOrganizationStatisticsQuery(Query):
    """Query to get organization statistics"""

    pass


class GetOrganizationStatisticsQueryHandler(
    QueryHandler[GetOrganizationStatisticsQuery, Dict[str, Any]]
):
    """Handler for GetOrganizationStatisticsQuery"""

    def __init__(self, organization_repository: OrganizationRepository):
        self.organization_repository = organization_repository

    async def handle(self, query: GetOrganizationStatisticsQuery) -> Dict[str, Any]:
        """Handle the get organization statistics query"""
        return self.organization_repository.get_statistics()


@dataclass
class GetOrganizationContactsQuery(Query):
    """Query to get contacts for an organization"""

    organization_id: str


class GetOrganizationContactsQueryHandler(
    QueryHandler[GetOrganizationContactsQuery, List[OrganizationContact]]
):
    """Handler for GetOrganizationContactsQuery"""

    def __init__(self, contact_repository: OrganizationContactRepository):
        self.contact_repository = contact_repository

    async def handle(
        self, query: GetOrganizationContactsQuery
    ) -> List[OrganizationContact]:
        """Handle the get organization contacts query"""
        return self.contact_repository.get_by_organization(query.organization_id)


@dataclass
class GetPrimaryContactQuery(Query):
    """Query to get the primary contact for an organization"""

    organization_id: str


class GetPrimaryContactQueryHandler(
    QueryHandler[GetPrimaryContactQuery, Optional[OrganizationContact]]
):
    """Handler for GetPrimaryContactQuery"""

    def __init__(self, contact_repository: OrganizationContactRepository):
        self.contact_repository = contact_repository

    async def handle(
        self, query: GetPrimaryContactQuery
    ) -> Optional[OrganizationContact]:
        """Handle the get primary contact query"""
        return self.contact_repository.get_primary_contact(query.organization_id)
