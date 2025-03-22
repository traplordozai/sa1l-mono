from django.utils.timezone import now

from .models import UserSession
from .repositories import UserSessionRepository


class UserSessionMiddleware:
    """
    Middleware to track and update user sessions
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Call the next middleware/view
        response = self.get_response(request)

        # Update last active timestamp for the current session
        if (
            request.user.is_authenticated
            and hasattr(request, "session")
            and "session_id" in request.session
        ):
            try:
                session_id = request.session["session_id"]
                UserSessionRepository.update_session_activity(session_id)
            except Exception:
                pass

        return response


class JWTAuthMiddleware:
    """
    Middleware to authenticate users using JWT tokens from Authorization header
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get token from Authorization header
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")

        if auth_header.startswith("Bearer "):
            token = auth_header[7:]

            # Authenticate user with token
            # This would typically be handled by DRF's authentication classes,
            # but we could add additional logic here if needed

            # For example, we could update the user's last active timestamp
            # or create a session record

            pass

        response = self.get_response(request)
        return response
