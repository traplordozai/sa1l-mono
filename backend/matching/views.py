from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
import requests
from django.conf import settings
from .models import ImportJob
from .serializers import ImportJobSerializer
from applications.models import Application
from internships.models import Internship
from django.contrib.auth import get_user_model

User = get_user_model()

@api_view(["GET"])
def detect_user_conflicts(request):
    """
    Detect scheduling conflicts and multiple offers for a user.
    
    Query Parameters:
        user: User ID to check for conflicts
        
    Returns:
        List of conflicts found:
        - date_overlap: Internships with overlapping dates
        - multiple_offers: User has multiple active offers
    """
    user_id = request.query_params.get("user")
    user = User.objects.get(id=user_id)
    results = []

    internships = Internship.objects.filter(user=user)
    for a in internships:
        overlaps = internships.exclude(id=a.id).filter(
            start_date__lte=a.end_date,
            end_date__gte=a.start_date
        )
        if overlaps.exists():
            results.append({"type": "date_overlap", "internship": a.id})

    offers = Application.objects.filter(candidate=user, status="offered")
    if offers.count() > 1:
        results.append({"type": "multiple_offers", "count": offers.count()})

    return Response(results)

class MatchControlView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        # Perform matching logic here
        return Response({"message": "Matching triggered"}, status=status.HTTP_200_OK)

    def delete(self, request):
        # Perform matching delete logic here
        return Response({"message": "Matching data cleared"}, status=status.HTTP_200_OK)

class ImportJobViewSet(viewsets.ModelViewSet):
    queryset = ImportJob.objects.all()
    serializer_class = ImportJobSerializer

class AIPoweredMatchView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        resume = request.data.get("resume", "")
        interests = request.data.get("interests", [])
        role_description = request.data.get("role", "")

        prompt = f"""
Match candidate resume and interests with this role:
--- Resume ---
{resume}
--- Interests ---
{', '.join(interests)}
--- Role ---
{role_description}
Return a score [0-100], fit summary, and key alignment.
"""

        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}"},
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
            }
        )
        data = response.json()
        text = data["choices"][0]["message"]["content"]
        return Response({"result": text})
