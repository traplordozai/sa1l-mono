import uuid
from datetime import timedelta
from typing import Any, Dict, List, Optional

from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.db import transaction
from django.utils import timezone

from .models import PasswordReset, Role, User, UserRole, UserSession


class UserRepository:
    """
    Repository for user-related operations
    """

    @classmethod
    def get_user_by_id(cls, user_id: str) -> Optional[User]:
        """
        Get a user by their ID
        """
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    @classmethod
    def get_user_by_email(cls, email: str) -> Optional[User]:
        """
        Get a user by their email
        """
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None

    @classmethod
    def create_user(cls, email: str, password: str, **extra_fields) -> User:
        """
        Create a new user with the given email and password
        """
        user = User.objects.create_user(email=email, password=password, **extra_fields)
        return user

    @classmethod
    def update_user(cls, user_id: str, **fields) -> Optional[User]:
        """
        Update a user's fields
        """
        try:
            user = User.objects.get(id=user_id)

            # Handle password separately if provided
            if "password" in fields:
                user.set_password(fields.pop("password"))

            # Update other fields
            for field, value in fields.items():
                setattr(user, field, value)

            user.save()
            return user
        except User.DoesNotExist:
            return None

    @classmethod
    def delete_user(cls, user_id: str) -> bool:
        """
        Delete a user by ID
        """
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            return True
        except User.DoesNotExist:
            return False

    @classmethod
    def check_credentials(cls, email: str, password: str) -> Optional[User]:
        """
        Check user credentials and return the user if valid
        """
        user = cls.get_user_by_email(email)

        if not user:
            return None

        # Check if account is locked
        if user.is_locked:
            return None

        # Check password
        if check_password(password, user.password):
            # Reset login attempts on successful login
            user.reset_login_attempts()
            return user
        else:
            # Increment login attempts on failed login
            user.increment_login_attempts()
            return None

    @classmethod
    def get_all_users(cls) -> List[User]:
        """
        Get all users
        """
        return list(User.objects.all())

    @classmethod
    def search_users(cls, query: str) -> List[User]:
        """
        Search for users by name or email
        """
        return list(
            User.objects.filter(
                models.Q(email__icontains=query)
                | models.Q(first_name__icontains=query)
                | models.Q(last_name__icontains=query)
            )
        )

    @classmethod
    def get_active_users(cls) -> List[User]:
        """
        Get all active users
        """
        return list(User.objects.filter(is_active=True))

    @classmethod
    def count_users_by_role(cls) -> Dict[str, int]:
        """
        Count users by role
        """
        counts = {}
        for role in Role.objects.all():
            counts[role.name] = UserRole.objects.filter(role=role).count()
        return counts


class RoleRepository:
    """
    Repository for role-related operations
    """

    @classmethod
    def get_role_by_name(cls, name: str) -> Optional[Role]:
        """
        Get a role by name
        """
        try:
            return Role.objects.get(name=name)
        except Role.DoesNotExist:
            return None

    @classmethod
    def get_role_by_id(cls, role_id: str) -> Optional[Role]:
        """
        Get a role by ID
        """
        try:
            return Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            return None

    @classmethod
    def get_all_roles(cls) -> List[Role]:
        """
        Get all roles
        """
        return list(Role.objects.all())

    @classmethod
    def create_default_roles(cls) -> List[Role]:
        """
        Create default roles if they don't exist
        """
        roles = []

        # Administrator role
        admin_role, created = Role.objects.get_or_create(
            name="admin",
            defaults={
                "description": "Full system administrator with all permissions",
                "can_view_all_students": True,
                "can_edit_all_students": True,
                "can_view_all_organizations": True,
                "can_edit_all_organizations": True,
                "can_run_matching": True,
                "can_approve_matches": True,
                "can_grade_statements": True,
                "can_import_data": True,
            },
        )
        roles.append(admin_role)

        # Faculty role
        faculty_role, created = Role.objects.get_or_create(
            name="faculty",
            defaults={
                "description": "Faculty member with permissions to grade and approve matches",
                "can_view_all_students": True,
                "can_edit_all_students": False,
                "can_view_all_organizations": True,
                "can_edit_all_organizations": False,
                "can_run_matching": False,
                "can_approve_matches": True,
                "can_grade_statements": True,
                "can_import_data": False,
            },
        )
        roles.append(faculty_role)

        # Student role
        student_role, created = Role.objects.get_or_create(
            name="student",
            defaults={
                "description": "Student with limited permissions",
                "can_view_all_students": False,
                "can_edit_all_students": False,
                "can_view_all_organizations": True,
                "can_edit_all_organizations": False,
                "can_run_matching": False,
                "can_approve_matches": False,
                "can_grade_statements": False,
                "can_import_data": False,
            },
        )
        roles.append(student_role)

        # Organization role
        org_role, created = Role.objects.get_or_create(
            name="organization",
            defaults={
                "description": "Organization with permissions to view and manage their profile",
                "can_view_all_students": False,
                "can_edit_all_students": False,
                "can_view_all_organizations": False,
                "can_edit_all_organizations": False,
                "can_run_matching": False,
                "can_approve_matches": False,
                "can_grade_statements": False,
                "can_import_data": False,
            },
        )
        roles.append(org_role)

        return roles


class UserRoleRepository:
    """
    Repository for user role operations
    """

    @classmethod
    def assign_role(
        cls,
        user_id: str,
        role_name: str,
        is_primary: bool = False,
        assigned_by_id: Optional[str] = None,
    ) -> Optional[UserRole]:
        """
        Assign a role to a user
        """
        try:
            user = User.objects.get(id=user_id)
            role = Role.objects.get(name=role_name)

            assigned_by = None
            if assigned_by_id:
                try:
                    assigned_by = User.objects.get(id=assigned_by_id)
                except User.DoesNotExist:
                    pass

            user_role, created = UserRole.objects.get_or_create(
                user=user,
                role=role,
                defaults={"is_primary": is_primary, "assigned_by": assigned_by},
            )

            if not created and user_role.is_primary != is_primary:
                user_role.is_primary = is_primary
                user_role.save(update_fields=["is_primary"])

            return user_role
        except (User.DoesNotExist, Role.DoesNotExist):
            return None

    @classmethod
    def remove_role(cls, user_id: str, role_name: str) -> bool:
        """
        Remove a role from a user
        """
        try:
            user = User.objects.get(id=user_id)
            role = Role.objects.get(name=role_name)

            result = UserRole.objects.filter(user=user, role=role).delete()
            return result[0] > 0
        except (User.DoesNotExist, Role.DoesNotExist):
            return False

    @classmethod
    def get_user_roles(cls, user_id: str) -> List[Role]:
        """
        Get all roles for a user
        """
        try:
            user = User.objects.get(id=user_id)
            return [user_role.role for user_role in UserRole.objects.filter(user=user)]
        except User.DoesNotExist:
            return []

    @classmethod
    def get_users_by_role(cls, role_name: str) -> List[User]:
        """
        Get all users with a specific role
        """
        try:
            role = Role.objects.get(name=role_name)
            return [user_role.user for user_role in UserRole.objects.filter(role=role)]
        except Role.DoesNotExist:
            return []

    @classmethod
    def get_primary_role(cls, user_id: str) -> Optional[Role]:
        """
        Get a user's primary role
        """
        try:
            user = User.objects.get(id=user_id)
            user_role = UserRole.objects.filter(user=user, is_primary=True).first()
            return user_role.role if user_role else None
        except User.DoesNotExist:
            return None

    @classmethod
    def has_role(cls, user_id: str, role_name: str) -> bool:
        """
        Check if a user has a specific role
        """
        try:
            user = User.objects.get(id=user_id)
            role = Role.objects.get(name=role_name)
            return UserRole.objects.filter(user=user, role=role).exists()
        except (User.DoesNotExist, Role.DoesNotExist):
            return False


class PasswordResetRepository:
    """
    Repository for password reset operations
    """

    @classmethod
    def create_reset_token(
        cls,
        user_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Optional[PasswordReset]:
        """
        Create a password reset token for a user
        """
        try:
            user = User.objects.get(id=user_id)

            # Expire any existing unused tokens
            PasswordReset.objects.filter(
                user=user, is_used=False, expires_at__gt=timezone.now()
            ).update(expires_at=timezone.now(), is_used=False)

            # Create new token valid for 24 hours
            expires_at = timezone.now() + timedelta(hours=24)
            reset = PasswordReset.objects.create(
                user=user,
                expires_at=expires_at,
                ip_requested=ip_address,
                user_agent=user_agent,
            )

            return reset
        except User.DoesNotExist:
            return None

    @classmethod
    def validate_token(cls, token: str) -> Optional[PasswordReset]:
        """
        Validate a password reset token
        """
        try:
            reset = PasswordReset.objects.get(
                token=token, is_used=False, expires_at__gt=timezone.now()
            )
            return reset
        except PasswordReset.DoesNotExist:
            return None

    @classmethod
    def use_token(cls, token: str) -> bool:
        """
        Mark a token as used
        """
        try:
            reset = PasswordReset.objects.get(token=token, is_used=False)
            reset.mark_as_used()
            return True
        except PasswordReset.DoesNotExist:
            return False


class UserSessionRepository:
    """
    Repository for user session operations
    """

    @classmethod
    def create_session(
        cls,
        user_id: str,
        ip_address: str,
        user_agent: Optional[str] = None,
        device_type: Optional[str] = None,
        location: Optional[str] = None,
    ) -> Optional[UserSession]:
        """
        Create a session for a user
        """
        try:
            user = User.objects.get(id=user_id)

            session = UserSession.objects.create(
                user=user,
                ip_address=ip_address,
                user_agent=user_agent,
                device_type=device_type,
                location=location,
            )

            return session
        except User.DoesNotExist:
            return None

    @classmethod
    def end_session(cls, session_id: str) -> bool:
        """
        End a session
        """
        try:
            session = UserSession.objects.get(session_id=session_id, is_active=True)
            session.end_session()
            return True
        except UserSession.DoesNotExist:
            return False

    @classmethod
    def end_all_sessions(
        cls, user_id: str, exclude_session_id: Optional[str] = None
    ) -> int:
        """
        End all sessions for a user, optionally excluding one
        """
        try:
            user = User.objects.get(id=user_id)

            query = UserSession.objects.filter(user=user, is_active=True)
            if exclude_session_id:
                query = query.exclude(session_id=exclude_session_id)

            count = query.count()
            query.update(is_active=False, ended_at=timezone.now())

            return count
        except User.DoesNotExist:
            return 0

    @classmethod
    def get_active_sessions(cls, user_id: str) -> List[UserSession]:
        """
        Get all active sessions for a user
        """
        try:
            user = User.objects.get(id=user_id)
            return list(UserSession.objects.filter(user=user, is_active=True))
        except User.DoesNotExist:
            return []

    @classmethod
    def get_session_by_id(cls, session_id: str) -> Optional[UserSession]:
        """
        Get a session by ID
        """
        try:
            return UserSession.objects.get(session_id=session_id)
        except UserSession.DoesNotExist:
            return None

    @classmethod
    def update_session_activity(cls, session_id: str) -> bool:
        """
        Update a session's last activity timestamp
        """
        try:
            session = UserSession.objects.get(session_id=session_id, is_active=True)
            session.last_active = timezone.now()
            session.save(update_fields=["last_active"])
            return True
        except UserSession.DoesNotExist:
            return False
