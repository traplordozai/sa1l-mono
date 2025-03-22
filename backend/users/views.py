from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Role, User, UserRole, UserSession
from .permissions import IsAdmin, IsFaculty, IsOwnerOrAdmin
from .repositories import (RoleRepository, UserRepository, UserRoleRepository,
                           UserSessionRepository)
from .serializers import (ChangePasswordSerializer, LoginSerializer,
                          PasswordResetRequestSerializer,
                          PasswordResetSerializer, RefreshTokenSerializer,
                          RoleSerializer, TokenResponseSerializer,
                          UserCreateSerializer, UserDetailSerializer,
                          UserRoleSerializer, UserSerializer,
                          UserSessionSerializer, UserUpdateSerializer)
from .services import (AuthenticationService, RoleService, UserService,
                       UserSessionService)

User = get_user_model()


class AuthViewSet(viewsets.ViewSet):
    """
    Authentication API endpoints
    """

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def login(self, request):
        """
        Login a user and return authentication tokens
        """
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        # Get IP and user agent
        ip_address = self._get_client_ip(request)
        user_agent = request.META.get("HTTP_USER_AGENT")

        # Authenticate user
        user, error = AuthenticationService.authenticate(
            email=email, password=password, ip_address=ip_address, user_agent=user_agent
        )

        if not user:
            return Response(
                {"error": error or "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Generate tokens
        tokens = AuthenticationService.generate_token(user)

        # Return token response
        token_serializer = TokenResponseSerializer(tokens)
        return Response(token_serializer.data)

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def refresh_token(self, request):
        """
        Refresh an access token using a refresh token
        """
        serializer = RefreshTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh_token = serializer.validated_data["refresh_token"]

        # Refresh token
        tokens, error = AuthenticationService.refresh_token(refresh_token)

        if not tokens:
            return Response(
                {"error": error or "Invalid refresh token"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Return token response
        token_serializer = TokenResponseSerializer(tokens)
        return Response(token_serializer.data)

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def logout(self, request):
        """
        Logout a user
        """
        user_id = str(request.user.id)

        # Extract session ID if available
        session_id = request.data.get("session_id")

        # Log out user
        AuthenticationService.logout(user_id, session_id)

        return Response({"message": "Logged out successfully"})

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def register(self, request):
        """
        Register a new user
        """
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Extract role
        role_name = serializer.validated_data.pop("role")

        # Register user
        user, error = UserService.register_user(
            email=serializer.validated_data.pop("email"),
            password=serializer.validated_data.pop("password"),
            role_name=role_name,
            **serializer.validated_data,
        )

        if not user:
            return Response(
                {"error": error or "Registration failed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Return user data
        user_serializer = UserSerializer(user)
        return Response(user_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def request_reset(self, request):
        """
        Request a password reset
        """
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        # Get IP and user agent
        ip_address = self._get_client_ip(request)
        user_agent = request.META.get("HTTP_USER_AGENT")

        # Request password reset
        success, error = UserService.request_password_reset(
            email=email, ip_address=ip_address, user_agent=user_agent
        )

        # Always return success to prevent email enumeration
        return Response(
            {
                "message": "If your email is registered, you will receive a password reset link"
            }
        )

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def reset_password(self, request):
        """
        Reset a password using a reset token
        """
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["new_password"]

        # Reset password
        success, error = UserService.reset_password(
            token=str(token), new_password=new_password
        )

        if not success:
            return Response(
                {"error": error or "Password reset failed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"message": "Password reset successful"})

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def me(self, request):
        """
        Get current user's profile
        """
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=["put"], permission_classes=[IsAuthenticated])
    def update_profile(self, request):
        """
        Update current user's profile
        """
        serializer = UserUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        # Update user profile
        user, error = UserService.update_user_profile(
            user_id=str(request.user.id), **serializer.validated_data
        )

        if not user:
            return Response(
                {"error": error or "Profile update failed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Return updated user data
        user_serializer = UserSerializer(user)
        return Response(user_serializer.data)

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        """
        Change current user's password
        """
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        current_password = serializer.validated_data["current_password"]
        new_password = serializer.validated_data["new_password"]

        # Change password
        success, error = UserService.change_password(
            user_id=str(request.user.id),
            current_password=current_password,
            new_password=new_password,
        )

        if not success:
            return Response(
                {"error": error or "Password change failed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"message": "Password changed successfully"})

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def sessions(self, request):
        """
        Get user's active sessions
        """
        sessions, error = UserSessionService.get_active_sessions(str(request.user.id))

        if error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserSessionSerializer(sessions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def end_session(self, request):
        """
        End a specific session
        """
        session_id = request.data.get("session_id")
        if not session_id:
            return Response(
                {"error": "Session ID is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Check session ownership
        session = UserSessionRepository.get_session_by_id(session_id)
        if not session or str(session.user.id) != str(request.user.id):
            return Response(
                {"error": "Session not found or not owned by user"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # End session
        success, error = UserSessionService.end_session(session_id)

        if not success:
            return Response(
                {"error": error or "Failed to end session"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"message": "Session ended successfully"})

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def end_all_sessions(self, request):
        """
        End all user sessions except current one
        """
        # Get current session ID
        current_session_id = request.data.get("current_session_id")

        # End all other sessions
        count, error = UserSessionService.end_all_sessions(
            user_id=str(request.user.id), exclude_session_id=current_session_id
        )

        if error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": f"Ended {count} sessions successfully"})

    def _get_client_ip(self, request):
        """
        Get client IP address from request
        """
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            # X-Forwarded-For can be a comma-separated list of proxies
            # The client's IP is the first one in the list
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


class UserViewSet(viewsets.ModelViewSet):
    """
    User management API endpoints
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return UserUpdateSerializer
        elif self.action == "retrieve":
            return UserDetailSerializer
        return UserSerializer

    def create(self, request, *args, **kwargs):
        """
        Create a new user
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Extract role
        role_name = serializer.validated_data.pop("role")

        # Register user
        user, error = UserService.register_user(
            email=serializer.validated_data.pop("email"),
            password=serializer.validated_data.pop("password"),
            role_name=role_name,
            **serializer.validated_data,
        )

        if not user:
            return Response(
                {"error": error or "User creation failed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Return user data
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """
        Update a user
        """
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # Update user
        user, error = UserService.update_user_profile(
            user_id=str(instance.id), **serializer.validated_data
        )

        if not user:
            return Response(
                {"error": error or "User update failed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Return updated user data
        serializer = UserSerializer(user)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def assign_role(self, request, pk=None):
        """
        Assign a role to a user
        """
        role_name = request.data.get("role")
        is_primary = request.data.get("is_primary", False)

        if not role_name:
            return Response(
                {"error": "Role name is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Assign role
        user_role, error = RoleService.assign_role_to_user(
            user_id=pk,
            role_name=role_name,
            is_primary=is_primary,
            assigned_by_id=str(request.user.id),
        )

        if not user_role:
            return Response(
                {"error": error or "Role assignment failed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Return user role data
        serializer = UserRoleSerializer(user_role)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def remove_role(self, request, pk=None):
        """
        Remove a role from a user
        """
        role_name = request.data.get("role")

        if not role_name:
            return Response(
                {"error": "Role name is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Remove role
        success, error = RoleService.remove_role_from_user(
            user_id=pk, role_name=role_name
        )

        if not success:
            return Response(
                {"error": error or "Role removal failed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"message": "Role removed successfully"})

    @action(detail=True, methods=["get"])
    def roles(self, request, pk=None):
        """
        Get all roles for a user
        """
        roles = UserRoleRepository.get_user_roles(pk)
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def set_active(self, request, pk=None):
        """
        Set a user's active status
        """
        is_active = request.data.get("is_active")

        if is_active is None:
            return Response(
                {"error": "is_active field is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update user
        user, error = UserService.update_user_profile(user_id=pk, is_active=is_active)

        if not user:
            return Response(
                {"error": error or "Status update failed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Return user data
        serializer = UserSerializer(user)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def reset_login_attempts(self, request, pk=None):
        """
        Reset a user's login attempts counter
        """
        user = self.get_object()
        user.reset_login_attempts()

        serializer = UserDetailSerializer(user)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def sessions(self, request, pk=None):
        """
        Get all active sessions for a user
        """
        sessions, error = UserSessionService.get_active_sessions(pk)

        if error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserSessionSerializer(sessions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def end_all_sessions(self, request, pk=None):
        """
        End all sessions for a user
        """
        count, error = UserSessionService.end_all_sessions(pk)

        if error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": f"Ended {count} sessions successfully"})


class RoleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Role API endpoints
    """

    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]

    @action(
        detail=False, methods=["post"], permission_classes=[IsAuthenticated, IsAdmin]
    )
    def initialize(self, request):
        """
        Initialize default roles
        """
        roles = RoleService.initialize_roles()
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def users(self, request, pk=None):
        """
        Get all users with a specific role
        """
        role = self.get_object()
        users = UserRoleRepository.get_users_by_role(role.name)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
