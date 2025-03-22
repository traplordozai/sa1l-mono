from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import PasswordReset, Role, User, UserRole, UserSession


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "date_joined",
    )
    search_fields = ("email", "first_name", "last_name")
    list_filter = ("is_staff", "is_active", "date_joined")
    ordering = ("-date_joined",)
    readonly_fields = ("date_joined", "last_login")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "phone_number")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            _("Login info"),
            {
                "fields": (
                    "last_login",
                    "last_login_ip",
                    "login_attempts",
                    "account_locked_until",
                )
            },
        ),
        (_("Important dates"), {"fields": ("date_joined",)}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "first_name",
                    "last_name",
                ),
            },
        ),
    )


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name", "description")
    list_filter = ("name",)
    fieldsets = (
        (None, {"fields": ("name", "description")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "can_view_all_students",
                    "can_edit_all_students",
                    "can_view_all_organizations",
                    "can_edit_all_organizations",
                    "can_run_matching",
                    "can_approve_matches",
                    "can_grade_statements",
                    "can_import_data",
                ),
            },
        ),
    )


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "is_primary", "assigned_by", "assigned_at")
    search_fields = ("user__email", "role__name")
    list_filter = ("role", "is_primary", "assigned_at")
    date_hierarchy = "assigned_at"
    raw_id_fields = ("user", "role", "assigned_by")


@admin.register(PasswordReset)
class PasswordResetAdmin(admin.ModelAdmin):
    list_display = ("user", "is_used", "expires_at", "created_at")
    search_fields = ("user__email",)
    list_filter = ("is_used", "expires_at", "created_at")
    date_hierarchy = "created_at"
    raw_id_fields = ("user",)
    readonly_fields = ("token", "ip_requested", "user_agent", "is_used", "used_at")


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "is_active",
        "device_type",
        "ip_address",
        "last_active",
        "created_at",
    )
    search_fields = ("user__email", "ip_address", "device_type")
    list_filter = ("is_active", "device_type", "created_at")
    date_hierarchy = "created_at"
    raw_id_fields = ("user",)
    readonly_fields = (
        "session_id",
        "ip_address",
        "user_agent",
        "device_type",
        "location",
    )
