from typing import Any, Dict, List, Optional

from django.db.models import Count, F, Q, Sum
from statements.models import AreaOfLaw

from .models import Organization, OrganizationContact


class OrganizationRepository:
    """
    Repository for Organization-related database operations
    """

    @staticmethod
    def get_by_id(organization_id: str) -> Optional[Organization]:
        """Get organization by ID"""
        try:
            return Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
            return None

    @staticmethod
    def get_all_active() -> List[Organization]:
        """Get all active organizations"""
        return Organization.objects.filter(is_active=True)

    @staticmethod
    def get_by_areas(area_ids: List[str]) -> List[Organization]:
        """Get organizations by areas of law"""
        return Organization.objects.filter(
            areas_of_law__id__in=area_ids, is_active=True
        ).distinct()

    @staticmethod
    def get_with_available_positions() -> List[Organization]:
        """Get organizations with available positions"""
        return Organization.objects.filter(
            is_active=True, available_positions__gt=F("filled_positions")
        )

    @staticmethod
    def search(query: str) -> List[Organization]:
        """Search organizations by name, description, or location"""
        return Organization.objects.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(location__icontains=query),
            is_active=True,
        )

    @staticmethod
    def create(organization_data: Dict[str, Any]) -> Organization:
        """Create a new organization"""
        area_ids = organization_data.pop("areas_of_law", [])
        organization = Organization.objects.create(**organization_data)

        # Add areas of law
        if area_ids:
            areas = AreaOfLaw.objects.filter(id__in=area_ids)
            organization.areas_of_law.add(*areas)

        return organization

    @staticmethod
    def update(
        organization_id: str, organization_data: Dict[str, Any]
    ) -> Optional[Organization]:
        """Update an existing organization"""
        try:
            organization = Organization.objects.get(id=organization_id)

            # Handle areas of law separately
            if "areas_of_law" in organization_data:
                area_ids = organization_data.pop("areas_of_law")
                organization.areas_of_law.clear()
                areas = AreaOfLaw.objects.filter(id__in=area_ids)
                organization.areas_of_law.add(*areas)

            # Update other fields
            for key, value in organization_data.items():
                setattr(organization, key, value)

            organization.save()
            return organization
        except Organization.DoesNotExist:
            return None

    @staticmethod
    def delete(organization_id: str) -> bool:
        """Delete an organization (soft delete by setting is_active=False)"""
        try:
            organization = Organization.objects.get(id=organization_id)
            organization.is_active = False
            organization.save()
            return True
        except Organization.DoesNotExist:
            return False

    @staticmethod
    def get_statistics() -> Dict[str, Any]:
        """Get statistics about organizations"""
        all_orgs = Organization.objects.all()
        active_orgs = all_orgs.filter(is_active=True)

        return {
            "total_count": all_orgs.count(),
            "active_count": active_orgs.count(),
            "total_positions": all_orgs.aggregate(Sum("available_positions"))[
                "available_positions__sum"
            ]
            or 0,
            "filled_positions": all_orgs.aggregate(Sum("filled_positions"))[
                "filled_positions__sum"
            ]
            or 0,
            "available_positions": (
                all_orgs.aggregate(available=Sum("available_positions"))["available"]
                or 0
            )
            - (all_orgs.aggregate(filled=Sum("filled_positions"))["filled"] or 0),
            "organizations_by_area": list(
                AreaOfLaw.objects.annotate(
                    organization_count=Count("organizations")
                ).values("id", "name", "organization_count")
            ),
        }


class OrganizationContactRepository:
    """
    Repository for OrganizationContact-related database operations
    """

    @staticmethod
    def get_by_id(contact_id: str) -> Optional[OrganizationContact]:
        """Get contact by ID"""
        try:
            return OrganizationContact.objects.get(id=contact_id)
        except OrganizationContact.DoesNotExist:
            return None

    @staticmethod
    def get_by_organization(organization_id: str) -> List[OrganizationContact]:
        """Get all contacts for an organization"""
        return OrganizationContact.objects.filter(organization_id=organization_id)

    @staticmethod
    def get_primary_contact(organization_id: str) -> Optional[OrganizationContact]:
        """Get primary contact for an organization"""
        try:
            return OrganizationContact.objects.get(
                organization_id=organization_id, is_primary=True
            )
        except OrganizationContact.DoesNotExist:
            return None

    @staticmethod
    def create(contact_data: Dict[str, Any]) -> OrganizationContact:
        """Create a new organization contact"""
        return OrganizationContact.objects.create(**contact_data)

    @staticmethod
    def update(
        contact_id: str, contact_data: Dict[str, Any]
    ) -> Optional[OrganizationContact]:
        """Update an existing organization contact"""
        try:
            contact = OrganizationContact.objects.get(id=contact_id)
            for key, value in contact_data.items():
                setattr(contact, key, value)
            contact.save()
            return contact
        except OrganizationContact.DoesNotExist:
            return None

    @staticmethod
    def delete(contact_id: str) -> bool:
        """Delete an organization contact"""
        try:
            contact = OrganizationContact.objects.get(id=contact_id)
            contact.delete()
            return True
        except OrganizationContact.DoesNotExist:
            return False
