from core.permissions import IsAdminUser, IsOrganizationOwner
from django.db.models import F
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Organization, OrganizationContact
from .serializers import (OrganizationContactSerializer,
                          OrganizationDetailSerializer,
                          OrganizationListSerializer, OrganizationSerializer)
from .services import OrganizationService


class OrganizationViewSet(viewsets.ModelViewSet):
    """ViewSet for Organization operations"""

    queryset = Organization.objects.all()
    service = OrganizationService()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description", "location"]
    ordering_fields = ["name", "location", "available_positions", "created_at"]
    ordering = ["name"]

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == "list":
            return OrganizationListSerializer
        elif self.action in ["retrieve", "contacts"]:
            return OrganizationDetailSerializer
        return OrganizationSerializer

    def get_permissions(self):
        """
        Return appropriate permissions based on action:
        - List and retrieve are accessible to authenticated users
        - Create, update, destroy are restricted to admins
        """
        if self.action in ["list", "retrieve", "with_available_positions"]:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Return the appropriate queryset based on the action and filters.
        Annotate with remaining_positions for serializers that need it.
        """
        queryset = Organization.objects.all().annotate(
            remaining_positions=F("available_positions") - F("filled_positions")
        )

        # Apply is_active filter if specified
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            is_active = is_active.lower() == "true"
            queryset = queryset.filter(is_active=is_active)

        # Apply area_of_law filter if specified
        area_of_law = self.request.query_params.get("area_of_law")
        if area_of_law:
            queryset = queryset.filter(areas_of_law__id=area_of_law)

        return queryset

    @action(detail=False, methods=["get"])
    def with_available_positions(self, request):
        """List organizations with available positions"""
        organizations = self.service.get_organizations_with_positions()
        serializer = OrganizationListSerializer(organizations, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def contacts(self, request, pk=None):
        """Get all contacts for an organization"""
        organization = self.get_object()
        contacts = organization.contacts.all()
        serializer = OrganizationContactSerializer(contacts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def statistics(self, request):
        """Get statistics about organizations"""
        statistics = self.service.get_organization_statistics()
        return Response(statistics)


class OrganizationContactViewSet(viewsets.ModelViewSet):
    """ViewSet for OrganizationContact operations"""

    queryset = OrganizationContact.objects.all()
    serializer_class = OrganizationContactSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        """
        Return appropriate permissions based on action:
        - List and retrieve are accessible to authenticated users
        - Create, update, destroy are restricted to admins or organization owners
        """
        if self.action in ["list", "retrieve"]:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsAdminUser | IsOrganizationOwner]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """Filter contacts by organization if specified"""
        queryset = OrganizationContact.objects.all()

        organization_id = self.request.query_params.get("organization_id")
        if organization_id:
            queryset = queryset.filter(organization_id=organization_id)

        return queryset

    @action(detail=True, methods=["post"])
    def set_as_primary(self, request, pk=None):
        """Set a contact as the primary contact for its organization"""
        contact = self.get_object()
        service = OrganizationService()

        if service.set_primary_contact(contact.organization.id, contact.id):
            return Response({"message": "Contact set as primary"})
        else:
            return Response(
                {"error": "Failed to set contact as primary"},
                status=status.HTTP_400_BAD_REQUEST,
            )
