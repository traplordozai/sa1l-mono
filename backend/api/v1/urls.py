from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .matching.views import MatchingViewSet
from .organizations.views import OrganizationViewSet
from .statements.views import StatementViewSet
from .students.views import StudentViewSet

# Create a router for RESTful endpoints
router = DefaultRouter()
router.register(r"students", StudentViewSet)
router.register(r"organizations", OrganizationViewSet)
router.register(r"statements", StatementViewSet)
router.register(r"matching", MatchingViewSet)

urlpatterns = [
    # Include all router-generated URLs
    path("", include(router.urls)),
    # Add any custom endpoints that don't fit the RESTful pattern
    path(
        "students/<uuid:student_id>/profile/",
        StudentViewSet.as_view({"get": "get_profile"}),
        name="student-profile",
    ),
    path(
        "matching/rounds/<uuid:round_id>/run/",
        MatchingViewSet.as_view({"post": "run_matching"}),
        name="run-matching",
    ),
]
