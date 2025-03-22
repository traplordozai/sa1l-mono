from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import PasswordReset, Role, UserRole, UserSession

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model
    """

    full_name = serializers.SerializerMethodField()
    primary_role = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "is_active",
            "date_joined",
            "phone_number",
            "primary_role",
            "roles",
        ]
        read_only_fields = ["id", "date_joined"]

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_primary_role(self, obj):
        try:
            primary_role = UserRole.objects.filter(user=obj, is_primary=True).first()
            if primary_role:
                return {
                    "id": str(primary_role.role.id),
                    "name": primary_role.role.name,
                    "display_name": primary_role.role.get_name_display(),
                }
        except Exception:
            pass
        return None

    def get_roles(self, obj):
        try:
            roles = []
            for user_role in UserRole.objects.filter(user=obj):
                roles.append(
                    {
                        "id": str(user_role.role.id),
                        "name": user_role.role.name,
                        "display_name": user_role.role.get_name_display(),
                        "is_primary": user_role.is_primary,
                    }
                )
            return roles
        except Exception:
            return []


class UserDetailSerializer(UserSerializer):
    """
    Detailed serializer for User model with additional fields
    """

    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = UserSerializer.Meta.fields + [
            "last_login",
            "permissions",
            "login_attempts",
            "is_locked",
        ]
        read_only_fields = UserSerializer.Meta.read_only_fields + [
            "last_login",
            "login_attempts",
            "is_locked",
        ]

    def get_permissions(self, obj):
        from .services import RoleService

        try:
            return RoleService.get_user_permissions(str(obj.id))
        except Exception:
            return {}


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating User model
    """

    class Meta:
        model = User
        fields = ["first_name", "last_name", "phone_number"]


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new user
    """

    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)
    role = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "confirm_password",
            "first_name",
            "last_name",
            "role",
            "phone_number",
        ]

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match")

        # Remove confirm_password from the data
        data.pop("confirm_password")
        return data


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing password
    """

    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError("New passwords do not match")
        return data


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for requesting a password reset
    """

    email = serializers.EmailField(required=True)


class PasswordResetSerializer(serializers.Serializer):
    """
    Serializer for resetting a password
    """

    token = serializers.UUIDField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match")
        return data


class RoleSerializer(serializers.ModelSerializer):
    """
    Serializer for Role model
    """

    display_name = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = [
            "id",
            "name",
            "display_name",
            "description",
            "can_view_all_students",
            "can_edit_all_students",
            "can_view_all_organizations",
            "can_edit_all_organizations",
            "can_run_matching",
            "can_approve_matches",
            "can_grade_statements",
            "can_import_data",
        ]

    def get_display_name(self, obj):
        return obj.get_name_display()


class UserRoleSerializer(serializers.ModelSerializer):
    """
    Serializer for UserRole model
    """

    user = UserSerializer(read_only=True)
    role = RoleSerializer(read_only=True)
    assigned_by = UserSerializer(read_only=True)

    class Meta:
        model = UserRole
        fields = ["id", "user", "role", "is_primary", "assigned_by", "assigned_at"]
        read_only_fields = ["id", "assigned_at"]


class UserSessionSerializer(serializers.ModelSerializer):
    """
    Serializer for UserSession model
    """

    user = UserSerializer(read_only=True)

    class Meta:
        model = UserSession
        fields = [
            "id",
            "session_id",
            "user",
            "ip_address",
            "device_type",
            "location",
            "user_agent",
            "last_active",
            "is_active",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "session_id",
            "user",
            "ip_address",
            "device_type",
            "location",
            "user_agent",
            "last_active",
            "created_at",
        ]


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login
    """

    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)


class TokenResponseSerializer(serializers.Serializer):
    """
    Serializer for token response
    """

    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
    token_type = serializers.CharField()
    expires_in = serializers.IntegerField()
    user = serializers.DictField()


class RefreshTokenSerializer(serializers.Serializer):
    """
    Serializer for refresh token
    """

    refresh_token = serializers.CharField(required=True)
