# backend/dashboard/views.py
from core.permissions import IsAdminUser
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import DashboardService


class DashboardStatsView(APIView):
    """
    API endpoint for retrieving dashboard statistics
    """

    permission_classes = [IsAdminUser]

    def get(self, request):
        """
        Get dashboard statistics
        """
        stats = DashboardService.get_dashboard_stats()
        return Response(stats)


class DashboardActivityView(APIView):
    """
    API endpoint for retrieving recent activity
    """

    permission_classes = [IsAdminUser]

    def get(self, request):
        """
        Get recent activity
        """
        # Get limit parameter from query string (default to 10)
        limit = int(request.query_params.get("limit", 10))
        # Restrict limit to reasonable range
        limit = max(1, min(limit, 50))

        activities = DashboardService.get_recent_activity(limit=limit)
        return Response(activities)


class PublicDashboardStatsView(APIView):
    """
    Public API endpoint for basic dashboard statistics
    Accessible without authentication
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        """
        Get limited public dashboard statistics
        """
        full_stats = DashboardService.get_dashboard_stats()

        # Return only a subset of stats that are safe to expose publicly
        public_stats = {
            "total_students": full_stats["total_students"],
            "matched_students": full_stats["matched_students"],
            "match_rate": full_stats["match_rate"]["percentage"],
            "total_organizations": full_stats["total_organizations"],
        }

        return Response(public_stats)
