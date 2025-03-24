from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils.timezone import now
from django.shortcuts import get_object_or_404
from .utils.conflicts import detect_conflicts, get_conflict_details, get_user_conflicts_summary
from .models import InternshipApplication

class ConflictCheckView(APIView):
    """
    API endpoint to check for conflicts in user's internships and applications.
    GET: Returns list of conflicts
    POST: Resolve specific conflict
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get all conflicts for the current user"""
        user = request.user
        format_type = request.query_params.get('format', 'basic')
        
        if format_type == 'summary':
            return Response(get_user_conflicts_summary(user))
        elif format_type == 'detailed':
            conflicts = detect_conflicts(user)
            return Response([get_conflict_details(conflict) for conflict in conflicts])
        else:
            return Response(detect_conflicts(user))

    def post(self, request):
        """Resolve a specific conflict"""
        conflict_type = request.data.get('type')
        action = request.data.get('action')
        
        if conflict_type == 'competing_offers':
            accepted_offer_id = request.data.get('accepted_offer_id')
            if not accepted_offer_id:
                return Response(
                    {"error": "accepted_offer_id is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            application = get_object_or_404(
                InternshipApplication,
                id=accepted_offer_id,
                candidate=request.user
            )
            
            # Update other offers to rejected
            InternshipApplication.objects.filter(
                candidate=request.user,
                status='offered'
            ).exclude(
                id=accepted_offer_id
            ).update(status='rejected')
            
            # Update accepted offer
            application.status = 'hired'
            application.save()
            
            return Response({"message": "Conflict resolved successfully"})
            
        elif conflict_type == 'expired_offer':
            offer_id = request.data.get('offer_id')
            if not offer_id:
                return Response(
                    {"error": "offer_id is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            application = get_object_or_404(
                InternshipApplication,
                id=offer_id,
                candidate=request.user
            )
            
            application.status = 'stale'
            application.save()
            
            return Response({"message": "Offer marked as stale"})
            
        return Response(
            {"error": "Invalid conflict type or action"},
            status=status.HTTP_400_BAD_REQUEST
        )

class ConflictDetailView(APIView):
    """
    API endpoint to get detailed information about a specific conflict
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, conflict_id):
        conflicts = detect_conflicts(request.user)
        try:
            conflict = next(c for c in conflicts if c.get('id') == conflict_id)
            return Response(get_conflict_details(conflict))
        except StopIteration:
            return Response(
                {"error": "Conflict not found"},
                status=status.HTTP_404_NOT_FOUND
            )

class ConflictSummaryView(APIView):
    """
    API endpoint to get a summary of all conflicts
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(get_user_conflicts_summary(request.user))

class OfferCountdownView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, application_id):
        app = InternshipApplication.objects.get(id=application_id, candidate=request.user)

        if app.status != "offered" or not app.expires_at:
            return Response({"message": "No active offer"}, status=400)

        seconds_left = int((app.expires_at - now()).total_seconds())
        return Response({
            "expires_at": app.expires_at,
            "seconds_remaining": seconds_left,
            "urgent": seconds_left <= 86400
        })
