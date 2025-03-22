from core.permissions import IsAdminUser
from django.db.models import Avg, Count
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Match, MatchingPreference, MatchingRound
from .serializers import (MatchingPreferenceSerializer,
                          MatchingRoundDetailSerializer,
                          MatchingRoundSerializer,
                          MatchingStatisticsSerializer, MatchSerializer,
                          RunMatchingSerializer, UpdateMatchStatusSerializer)
from .services import MatchingService
from .commands.matching_commands import run_matching_command


class MatchingRoundViewSet(viewsets.ModelViewSet):
    """API endpoints for matching rounds."""

    queryset = MatchingRound.objects.all().order_by("-created_at")
    serializer_class = MatchingRoundSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return MatchingRoundDetailSerializer
        return MatchingRoundSerializer

    @action(detail=True, methods=["post"])
    def run_algorithm(self, request, pk=None):
        """Run the matching algorithm for this round."""
        serializer = RunMatchingSerializer(data={"round_id": pk})
        serializer.is_valid(raise_exception=True)

        service = MatchingService()
        try:
            round = service.run_matching(pk, request.user)
            return Response(
                {
                    "message": f"Matching algorithm completed successfully. Matched {round.matched_students} students.",
                    "round": MatchingRoundSerializer(round).data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": f"Error running matching algorithm: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=True, methods=["get"])
    def matches(self, request, pk=None):
        """Get all matches for this round."""
        round = self.get_object()
        matches = Match.objects.filter(round=round)
        serializer = MatchSerializer(matches, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def statistics(self, request, pk=None):
        """Get statistics for this matching round."""
        service = MatchingService()
        stats = service.get_matching_statistics(pk)
        serializer = MatchingStatisticsSerializer(stats)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def statistics(self, request):
        """Get overall matching statistics."""
        service = MatchingService()
        stats = service.get_matching_statistics()
        serializer = MatchingStatisticsSerializer(stats)
        return Response(serializer.data)


class MatchViewSet(viewsets.ModelViewSet):
    """API endpoints for matches."""

    queryset = Match.objects.all()
    serializer_class = MatchSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter matches based on query parameters."""
        queryset = Match.objects.all()

        # Filter by round_id if provided
        round_id = self.request.query_params.get("round_id")
        if round_id:
            queryset = queryset.filter(round_id=round_id)

        # Filter by student_id if provided
        student_id = self.request.query_params.get("student_id")
        if student_id:
            queryset = queryset.filter(student_id=student_id)

        # Filter by organization_id if provided
        organization_id = self.request.query_params.get("organization_id")
        if organization_id:
            queryset = queryset.filter(organization_id=organization_id)

        # Filter by status if provided
        status_param = self.request.query_params.get("status")
        if status_param:
            queryset = queryset.filter(status=status_param)

        return queryset

    @action(detail=True, methods=["post"])
    def update_status(self, request, pk=None):
        """Update the status of a match."""
        match = self.get_object()
        serializer = UpdateMatchStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_status = serializer.validated_data["status"]
        notes = serializer.validated_data.get("notes")

        service = MatchingService()
        try:
            updated_match = service.update_match_status(
                match.id, new_status, request.user, notes
            )
            return Response(
                {
                    "message": f"Match status updated to {new_status}",
                    "match": MatchSerializer(updated_match).data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": f"Error updating match status: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class MatchingPreferenceViewSet(viewsets.ModelViewSet):
    """API endpoints for matching preferences."""

    queryset = MatchingPreference.objects.all()
    serializer_class = MatchingPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter preferences based on query parameters."""
        queryset = MatchingPreference.objects.all()

        # Filter by preference_type if provided
        preference_type = self.request.query_params.get("preference_type")
        if preference_type:
            queryset = queryset.filter(preference_type=preference_type)

        # Filter by student_id if provided
        student_id = self.request.query_params.get("student_id")
        if student_id:
            queryset = queryset.filter(student_id=student_id)

        # Filter by organization_id if provided
        organization_id = self.request.query_params.get("organization_id")
        if organization_id:
            queryset = queryset.filter(organization_id=organization_id)

        # Filter by area_of_law if provided
        area_of_law = self.request.query_params.get("area_of_law")
        if area_of_law:
            queryset = queryset.filter(area_of_law=area_of_law)

        return queryset


class MatchingTriggerView(APIView):
    def post(self, request):
        student_ids = request.data.get("student_ids", [])
        round_id = request.data.get("round_id")

        if not student_ids or not round_id:
            return Response({"error": "Missing parameters"}, status=400)

        result = run_matching_command(student_ids, round_id)

        if "error" in result:
            return Response(result, status=502)

        return Response(result, status=200)
