from rest_framework import serializers
from statements.models import AreaOfLaw
from statements.serializers import AreaOfLawSerializer

from .models import Organization, OrganizationContact


class OrganizationContactSerializer(serializers.ModelSerializer):
    """Serializer for organization contacts"""

    class Meta:
        model = OrganizationContact
        fields = [
            "id",
            "name",
            "title",
            "email",
            "phone",
            "is_primary",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class OrganizationSerializer(serializers.ModelSerializer):
    """Serializer for organizations"""

    areas_of_law = AreaOfLawSerializer(many=True, read_only=True)
    area_ids = serializers.PrimaryKeyRelatedField(
        source="areas_of_law",
        queryset=AreaOfLaw.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )
    primary_contact = serializers.SerializerMethodField()
    remaining_positions = serializers.IntegerField(read_only=True)

    class Meta:
        model = Organization
        fields = [
            "id",
            "name",
            "description",
            "areas_of_law",
            "area_ids",
            "location",
            "contact_email",
            "contact_phone",
            "website",
            "requirements",
            "available_positions",
            "filled_positions",
            "remaining_positions",
            "is_active",
            "primary_contact",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "filled_positions", "created_at", "updated_at"]

    def get_primary_contact(self, obj):
        """Get the primary contact for the organization"""
        try:
            contact = obj.contacts.get(is_primary=True)
            return OrganizationContactSerializer(contact).data
        except OrganizationContact.DoesNotExist:
            return None

    def create(self, validated_data):
        """Handle creation with nested areas of law"""
        areas = validated_data.pop("areas_of_law", [])
        organization = Organization.objects.create(**validated_data)

        if areas:
            organization.areas_of_law.set(areas)

        return organization

    def update(self, instance, validated_data):
        """Handle updates with nested areas of law"""
        areas = validated_data.pop("areas_of_law", None)

        # Update standard fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Update areas of law if provided
        if areas is not None:
            instance.areas_of_law.set(areas)

        instance.save()
        return instance


class OrganizationDetailSerializer(OrganizationSerializer):
    """Extended serializer for organization details"""

    contacts = OrganizationContactSerializer(many=True, read_only=True)

    class Meta(OrganizationSerializer.Meta):
        fields = OrganizationSerializer.Meta.fields + ["contacts"]


class OrganizationListSerializer(serializers.ModelSerializer):
    """Simplified serializer for organization listings"""

    areas_of_law = serializers.StringRelatedField(many=True)
    remaining_positions = serializers.IntegerField(read_only=True)

    class Meta:
        model = Organization
        fields = [
            "id",
            "name",
            "location",
            "areas_of_law",
            "available_positions",
            "filled_positions",
            "remaining_positions",
            "is_active",
        ]
