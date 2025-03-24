from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import Organization
from .serializers import OrganizationSerializer

class MyOrganizationView(generics.RetrieveUpdateAPIView):
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return Organization.objects.get(user=self.request.user)

class MatchedStudentsView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        # Fake data for now
        return Response({"matches": [
            {"id": 1, "name": "Jane Student", "status": "Pending"},
            {"id": 2, "name": "John Law", "status": "Accepted"}
        ]})

class InterviewScheduleView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        return Response({"interviews": [
            {"id": 1, "student": "Jane Student", "datetime": "2025-04-01T10:00"},
            {"id": 2, "student": "John Law", "datetime": "2025-04-03T14:00"},
        ]})
    def post(self, request):
        return Response({"status": "Interview scheduled", "data": request.data})

class DeliverablesView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        return Response({"deliverables": [
            {"student": "Jane Student", "type": "Learning Plan", "status": "Submitted"},
            {"student": "John Law", "type": "Final Reflection", "status": "Pending"}
        ]})
