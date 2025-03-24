from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import FeedbackEntry
from .serializers import FeedbackEntrySerializer

class SubmitFeedbackView(APIView):
    """
    API endpoint for submitting feedback.
    POST: Create a new feedback entry
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = FeedbackEntrySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(reviewer=request.user)
        return Response(serializer.data)

class GetFeedbackView(APIView):
    """
    API endpoint for retrieving feedback for a specific user.
    GET: Returns list of feedback entries
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        entries = FeedbackEntry.objects.filter(target_id=user_id)
        return Response(FeedbackEntrySerializer(entries, many=True).data)