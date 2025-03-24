from rest_framework import generics, permissions
from .models import Organization
from .serializers import OrganizationSerializer

class MyOrganizationView(generics.RetrieveUpdateAPIView):
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return Organization.objects.get(user=self.request.user)
