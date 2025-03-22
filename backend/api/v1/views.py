from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class VersionedAPIView(APIView):
    """Base class for API v1 views"""

    version = "v1"

    def get_version_info(self):
        return {"version": self.version, "deprecated": False, "latest": True}

    def finalize_response(self, request, response, *args, **kwargs):
        """Add version headers to response"""
        response = super().finalize_response(request, response, *args, **kwargs)
        response["API-Version"] = self.version
        return response
