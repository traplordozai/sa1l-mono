import datetime
import re
from typing import Any, Dict, List, Optional, Tuple

import jwt
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone

from .models import PasswordReset, Role, User, UserRole, UserSession
from .repositories import (PasswordResetRepository, RoleRepository,
                           UserRepository, UserRoleRepository,
                           UserSessionRepository)


class AuthenticationService:
    """
    Service for authentication-related operations
    """

    @classmethod
    def authenticate(
        cls,
        email: str,
        password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Tuple[Optional[User], Optional[str]]:
        """
        Authenticate a user with email and password

        Returns:
            Tuple containing:
                - Authenticated user or None if authentication failed
                - Error message if authentication failed, None otherwise
        """
        if not email or not password:
            return None, "Email and password are required"

        # Check credentials
        user = UserRepository.check_credentials(email, password)

        if not user:
            return None, "Invalid email or password"

        if not user.is_active:
            return None, "Account is inactive"

        if user.is_locked:
            return None, f"Account is locked. Please try again later."

        # Update user's last login IP
        if ip_address:
            user.update_last_login_ip(ip_address)

        # Create session
        if ip_address:
            UserSessionRepository.create_session(
                user_id=str(user.id), ip_address=ip_address, user_agent=user_agent
            )

        return user, None

    @classmethod
    def generate_token(cls, user: User) -> Dict[str, Any]:
        """
        Generate JWT token for a user

        Returns:
            Dict containing:
                - access_token: JWT token for API authentication
                - refresh_token: Token to refresh the access token
                - token_type: Token type (Bearer)
                - expires_in: Token expiration time in seconds
        """
        # Set token expiration (e.g., 1 hour for access token)
        access_token_expiry = timezone.now() + datetime.timedelta(
            minutes=getattr(settings, "ACCESS_TOKEN_LIFETIME_MINUTES", 60)
        )

        # Set refresh token expiration (e.g., 7 days)
        refresh_token_expiry = timezone.now() + datetime.timedelta(
            days=getattr(settings, "REFRESH_TOKEN_LIFETIME_DAYS", 7)
        )

        # Get user's primary role
        primary_role = UserRoleRepository.get_primary_role(str(user.id))
        role_name = primary_role.name if primary_role else None

        # Get all user roles
        user_roles = UserRoleRepository.get_user_roles(str(user.id))
        role_names = [role.name for role in user_roles]

        # Set up token payload
        payload = {
            "user_id": str(user.id),
            "email": user.email,
            "name": user.get_full_name(),
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
            "primary_role": role_name,
            "roles": role_names,
            "exp": int(access_token_expiry.timestamp()),
        }

        # Create refresh token payload
        refresh_payload = {
            "user_id": str(user.id),
            "exp": int(refresh_token_expiry.timestamp()),
            "type": "refresh",
        }

        # Generate tokens
        access_token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

        refresh_token = jwt.encode(
            refresh_payload, settings.SECRET_KEY, algorithm="HS256"
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": getattr(settings, "ACCESS_TOKEN_LIFETIME_MINUTES", 60) * 60,
            "user": {
                "id": str(user.id),
                "email": user.email,
                "name": user.get_full_name(),
                "primary_role": role_name,
                "roles": role_names,
            },
        }

    @classmethod
    def refresh_token(
        cls, refresh_token: str
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Refresh an access token using a refresh token

        Returns:
            Tuple containing:
                - Dictionary with new tokens if successful, None otherwise
                - Error message if unsuccessful, None otherwise
        """
        try:
            # Decode and validate refresh token
            payload = jwt.decode(
                refresh_token, settings.SECRET_KEY, algorithms=["HS256"]
            )

            # Check token type
            if payload.get("type") != "refresh":
                return None, "Invalid token type"

            # Get user from token
            user_id = payload.get("user_id")
            if not user_id:
                return None, "Invalid token payload"

            user = UserRepository.get_user_by_id(user_id)
            if not user:
                return None, "User not found"

            if not user.is_active:
                return None, "User is inactive"

            # Generate new tokens
            tokens = cls.generate_token(user)
            return tokens, None

        except jwt.ExpiredSignatureError:
            return None, "Refresh token expired"
        except jwt.InvalidTokenError:
            return None, "Invalid refresh token"
        except Exception as e:
            return None, str(e)

    @classmethod
    def logout(cls, user_id: str, session_id: Optional[str] = None) -> bool:
        """
        Logout a user by ending their sessions

        Args:
            user_id: ID of the user to logout
            session_id: Optional ID of the current session to end

        Returns:
            True if logout was successful, False otherwise
        """
        if session_id:
            # End specific session
            return UserSessionRepository.end_session(session_id)
        else:
            # End all sessions
            return UserSessionRepository.end_all_sessions(user_id) > 0

    @classmethod
    def verify_token(cls, token: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Verify and decode a JWT token

        Returns:
            Tuple containing:
                - Decoded token payload if valid, None otherwise
                - Error message if invalid, None otherwise
        """
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            return payload, None
        except jwt.ExpiredSignatureError:
            return None, "Token expired"
        except jwt.InvalidTokenError:
            return None, "Invalid token"
        except Exception as e:
            return None, str(e)


class UserService:
    """
    Service for user-related operations
    """

    @classmethod
    def register_user(
        cls,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        role_name: str,
        **extra_fields,
    ) -> Tuple[Optional[User], Optional[str]]:
        """
        Register a new user with the given details

        Returns:
            Tuple containing:
                - Created user if successful, None otherwise
                - Error message if unsuccessful, None otherwise
        """
        # Validate email
        if not cls._validate_email(email):
            return None, "Invalid email format"

        # Check if email already exists
        if UserRepository.get_user_by_email(email):
            return None, "Email already registered"

        # Validate password
        password_validation = cls._validate_password(password)
        if password_validation:
            return None, password_validation

        # Validate role
        if not RoleRepository.get_role_by_name(role_name):
            return None, f"Invalid role: {role_name}"

        try:
            # Create user
            user = UserRepository.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                **extra_fields,
            )

            # Assign role
            UserRoleRepository.assign_role(
                user_id=str(user.id), role_name=role_name, is_primary=True
            )

            return user, None
        except Exception as e:
            return None, str(e)

    @classmethod
    def update_user_profile(
        cls, user_id: str, **fields
    ) -> Tuple[Optional[User], Optional[str]]:
        """
        Update a user's profile

        Returns:
            Tuple containing:
                - Updated user if successful, None otherwise
                - Error message if unsuccessful, None otherwise
        """
        # Validate input fields
        if "email" in fields and not cls._validate_email(fields["email"]):
            return None, "Invalid email format"

        if "password" in fields:
            password_validation = cls._validate_password(fields["password"])
            if password_validation:
                return None, password_validation

        try:
            # Update user
            user = UserRepository.update_user(user_id, **fields)
            if not user:
                return None, "User not found"

            return user, None
        except Exception as e:
            return None, str(e)

    @classmethod
    def change_password(
        cls, user_id: str, current_password: str, new_password: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Change a user's password

        Returns:
            Tuple containing:
                - True if successful, False otherwise
                - Error message if unsuccessful, None otherwise
        """
        # Get user
        user = UserRepository.get_user_by_id(user_id)
        if not user:
            return False, "User not found"

        # Verify current password
        if not user.check_password(current_password):
            return False, "Current password is incorrect"

        # Validate new password
        password_validation = cls._validate_password(new_password)
        if password_validation:
            return False, password_validation

        try:
            # Update password
            user.set_password(new_password)
            user.save()

            # End all other sessions
            UserSessionRepository.end_all_sessions(user_id)

            return True, None
        except Exception as e:
            return False, str(e)

    @classmethod
    def request_password_reset(
        cls,
        email: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        Request a password reset

        Returns:
            Tuple containing:
                - True if reset token was created, False otherwise
                - Error message if unsuccessful, None otherwise
        """
        # Get user by email
        user = UserRepository.get_user_by_email(email)
        if not user:
            # Don't reveal that the email doesn't exist
            return True, None

        if not user.is_active:
            # Don't reveal that the account is inactive
            return True, None

        try:
            # Create reset token
            reset = PasswordResetRepository.create_reset_token(
                user_id=str(user.id), ip_address=ip_address, user_agent=user_agent
            )

            if not reset:
                return False, "Failed to create reset token"

            # Send reset email
            cls._send_password_reset_email(user, reset)

            return True, None
        except Exception as e:
            return False, str(e)

    @classmethod
    def reset_password(
        cls, token: str, new_password: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Reset a password using a reset token

        Returns:
            Tuple containing:
                - True if password was reset, False otherwise
                - Error message if unsuccessful, None otherwise
        """
        # Validate token
        reset = PasswordResetRepository.validate_token(token)
        if not reset:
            return False, "Invalid or expired token"

        # Validate new password
        password_validation = cls._validate_password(new_password)
        if password_validation:
            return False, password_validation

        try:
            # Update password
            user = reset.user
            user.set_password(new_password)
            user.save()

            # Mark token as used
            PasswordResetRepository.use_token(token)

            # End all sessions
            UserSessionRepository.end_all_sessions(str(user.id))

            return True, None
        except Exception as e:
            return False, str(e)

    @classmethod
    def _validate_email(cls, email: str) -> bool:
        """
        Validate email format
        """
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(email_regex, email))

    @classmethod
    def _validate_password(cls, password: str) -> Optional[str]:
        """
        Validate password strength

        Returns:
            Error message if password is invalid, None otherwise
        """
        if len(password) < 8:
            return "Password must be at least 8 characters long"

        if not any(char.isdigit() for char in password):
            return "Password must contain at least one digit"

        if not any(char.isalpha() for char in password):
            return "Password must contain at least one letter"

        return None

    @classmethod
    def _send_password_reset_email(cls, user: User, reset: PasswordReset) -> None:
        """
        Send a password reset email
        """
        subject = "Password Reset Request"

        # Create reset URL
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{reset.token}"

        # Render email template
        context = {
            "user": user,
            "reset_url": reset_url,
            "expires_at": reset.expires_at,
        }

        text_content = f"""
        Hello {user.get_full_name()},

        You recently requested to reset your password. Click the link below to reset it:

        {reset_url}

        This link will expire on {reset.expires_at.strftime('%Y-%m-%d %H:%M:%S')}.

        If you did not request a password reset, please ignore this email.

        Best regards,
        The Team
        """

        # Send email
        send_mail(
            subject=subject,
            message=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )


class RoleService:
    """
    Service for role-related operations
    """

    @classmethod
    def initialize_roles(cls) -> List[Role]:
        """
        Initialize default roles
        """
        return RoleRepository.create_default_roles()

    @classmethod
    def assign_role_to_user(
        cls,
        user_id: str,
        role_name: str,
        is_primary: bool = False,
        assigned_by_id: Optional[str] = None,
    ) -> Tuple[Optional[UserRole], Optional[str]]:
        """
        Assign a role to a user

        Returns:
            Tuple containing:
                - UserRole if successful, None otherwise
                - Error message if unsuccessful, None otherwise
        """
        # Check user
        user = UserRepository.get_user_by_id(user_id)
        if not user:
            return None, "User not found"

        # Check role
        role = RoleRepository.get_role_by_name(role_name)
        if not role:
            return None, "Role not found"

        try:
            # Assign role
            user_role = UserRoleRepository.assign_role(
                user_id=user_id,
                role_name=role_name,
                is_primary=is_primary,
                assigned_by_id=assigned_by_id,
            )

            if not user_role:
                return None, "Failed to assign role"

            return user_role, None
        except Exception as e:
            return None, str(e)

    @classmethod
    def remove_role_from_user(
        cls, user_id: str, role_name: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Remove a role from a user

        Returns:
            Tuple containing:
                - True if successful, False otherwise
                - Error message if unsuccessful, None otherwise
        """
        # Check user
        user = UserRepository.get_user_by_id(user_id)
        if not user:
            return False, "User not found"

        # Check role
        role = RoleRepository.get_role_by_name(role_name)
        if not role:
            return False, "Role not found"

        try:
            # Remove role
            success = UserRoleRepository.remove_role(user_id, role_name)

            if not success:
                return False, "Failed to remove role"

            return True, None
        except Exception as e:
            return False, str(e)

    @classmethod
    def get_user_permissions(cls, user_id: str) -> Dict[str, bool]:
        """
        Get a user's permissions based on their roles

        Returns:
            Dictionary of permission names to boolean values
        """
        # Initialize default permissions
        permissions = {
            "can_view_all_students": False,
            "can_edit_all_students": False,
            "can_view_all_organizations": False,
            "can_edit_all_organizations": False,
            "can_run_matching": False,
            "can_approve_matches": False,
            "can_grade_statements": False,
            "can_import_data": False,
        }

        # Get user
        user = UserRepository.get_user_by_id(user_id)
        if not user:
            return permissions

        # Superusers have all permissions
        if user.is_superuser:
            return {key: True for key in permissions}

        # Get user roles
        roles = UserRoleRepository.get_user_roles(user_id)

        # Combine permissions from all roles
        for role in roles:
            for permission in permissions:
                if hasattr(role, permission) and getattr(role, permission):
                    permissions[permission] = True

        return permissions


class UserSessionService:
    """
    Service for user session operations
    """

    @classmethod
    def create_session(
        cls, user_id: str, ip_address: str, user_agent: Optional[str] = None
    ) -> Tuple[Optional[UserSession], Optional[str]]:
        """
        Create a session for a user

        Returns:
            Tuple containing:
                - UserSession if successful, None otherwise
                - Error message if unsuccessful, None otherwise
        """
        # Check user
        user = UserRepository.get_user_by_id(user_id)
        if not user:
            return None, "User not found"

        try:
            # Detect device type
            device_type = cls._detect_device_type(user_agent) if user_agent else None

            # Create session
            session = UserSessionRepository.create_session(
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                device_type=device_type,
            )

            if not session:
                return None, "Failed to create session"

            return session, None
        except Exception as e:
            return None, str(e)

    @classmethod
    def end_session(cls, session_id: str) -> Tuple[bool, Optional[str]]:
        """
        End a session

        Returns:
            Tuple containing:
                - True if successful, False otherwise
                - Error message if unsuccessful, None otherwise
        """
        try:
            # End session
            success = UserSessionRepository.end_session(session_id)

            if not success:
                return False, "Failed to end session"

            return True, None
        except Exception as e:
            return False, str(e)

    @classmethod
    def get_active_sessions(
        cls, user_id: str
    ) -> Tuple[List[UserSession], Optional[str]]:
        """
        Get all active sessions for a user

        Returns:
            Tuple containing:
                - List of active sessions if successful
                - Error message if unsuccessful, None otherwise
        """
        # Check user
        user = UserRepository.get_user_by_id(user_id)
        if not user:
            return [], "User not found"

        try:
            # Get sessions
            sessions = UserSessionRepository.get_active_sessions(user_id)
            return sessions, None
        except Exception as e:
            return [], str(e)

    @classmethod
    def end_all_sessions(
        cls, user_id: str, exclude_session_id: Optional[str] = None
    ) -> Tuple[int, Optional[str]]:
        """
        End all sessions for a user, optionally excluding one

        Returns:
            Tuple containing:
                - Number of sessions ended if successful
                - Error message if unsuccessful, None otherwise
        """
        # Check user
        user = UserRepository.get_user_by_id(user_id)
        if not user:
            return 0, "User not found"

        try:
            # End sessions
            count = UserSessionRepository.end_all_sessions(user_id, exclude_session_id)
            return count, None
        except Exception as e:
            return 0, str(e)

    @classmethod
    def _detect_device_type(cls, user_agent: str) -> str:
        """
        Detect device type from user agent
        """
        user_agent = user_agent.lower()

        if "mobile" in user_agent or "android" in user_agent or "iphone" in user_agent:
            return "mobile"
        elif "tablet" in user_agent or "ipad" in user_agent:
            return "tablet"
        else:
            return "desktop"
