from django.contrib.auth import get_user_model
from rest_framework import permissions

from .models import Role, UserRole

User = get_user_model()


class IsAdmin(permissions.BasePermission):
    """
    Permission to allow only admin users.
    """

    def has_permission(self, request, view):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return False

        # Django superusers always have permission
        if request.user.is_superuser:
            return True

        # Check if user has admin role
        try:
            return UserRole.objects.filter(
                user=request.user, role__name="admin"
            ).exists()
        except:
            return False


class IsFaculty(permissions.BasePermission):
    """
    Permission to allow only faculty members.
    """

    def has_permission(self, request, view):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return False

        # Django superusers always have permission
        if request.user.is_superuser:
            return True

        # Check if user has faculty role
        try:
            return UserRole.objects.filter(
                user=request.user, role__name="faculty"
            ).exists()
        except:
            return False


class IsStudent(permissions.BasePermission):
    """
    Permission to allow only students.
    """

    def has_permission(self, request, view):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return False

        # Check if user has student role
        try:
            return UserRole.objects.filter(
                user=request.user, role__name="student"
            ).exists()
        except:
            return False


class IsOrganization(permissions.BasePermission):
    """
    Permission to allow only organizations.
    """

    def has_permission(self, request, view):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return False

        # Check if user has organization role
        try:
            return UserRole.objects.filter(
                user=request.user, role__name="organization"
            ).exists()
        except:
            return False


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission to allow only the owner of an object or an admin user.
    """

    def has_object_permission(self, request, view, obj):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return False

        # Django superusers always have permission
        if request.user.is_superuser:
            return True

        # Check if user has admin role
        try:
            is_admin = UserRole.objects.filter(
                user=request.user, role__name="admin"
            ).exists()

            if is_admin:
                return True
        except:
            pass

        # Check if user is the owner
        if hasattr(obj, "user"):
            return obj.user == request.user

        return obj == request.user


class HasPermission(permissions.BasePermission):
    """
    Permission to allow users with a specific permission.
    """

    def __init__(self, required_permission):
        self.required_permission = required_permission

    def has_permission(self, request, view):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return False

        # Django superusers always have permission
        if request.user.is_superuser:
            return True

        # Get user's roles
        user_roles = UserRole.objects.filter(user=request.user)

        # Check if any of the user's roles has the required permission
        for user_role in user_roles:
            if hasattr(user_role.role, self.required_permission) and getattr(
                user_role.role, self.required_permission
            ):
                return True

        return False


class CanViewAllStudents(HasPermission):
    """
    Permission to allow users who can view all students.
    """

    def __init__(self):
        super().__init__("can_view_all_students")


class CanEditAllStudents(HasPermission):
    """
    Permission to allow users who can edit all students.
    """

    def __init__(self):
        super().__init__("can_edit_all_students")


class CanViewAllOrganizations(HasPermission):
    """
    Permission to allow users who can view all organizations.
    """

    def __init__(self):
        super().__init__("can_view_all_organizations")


class CanEditAllOrganizations(HasPermission):
    """
    Permission to allow users who can edit all organizations.
    """

    def __init__(self):
        super().__init__("can_edit_all_organizations")


class CanRunMatching(HasPermission):
    """
    Permission to allow users who can run the matching algorithm.
    """

    def __init__(self):
        super().__init__("can_run_matching")


class CanApproveMatches(HasPermission):
    """
    Permission to allow users who can approve matches.
    """

    def __init__(self):
        super().__init__("can_approve_matches")


class CanGradeStatements(HasPermission):
    """
    Permission to allow users who can grade statements.
    """

    def __init__(self):
        super().__init__("can_grade_statements")


class CanImportData(HasPermission):
    """
    Permission to allow users who can import data.
    """

    def __init__(self):
        super().__init__("can_import_data")
