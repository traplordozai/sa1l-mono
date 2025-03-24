from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    # API Documentation
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    
    # API Endpoints
    path("users/", include("users.urls")),
    path("applications/", include("applications.urls")),
    path("feedback/", include("feedback.urls")),
    path("forms/", include("forms.urls")),
    path("matching/", include("matching.urls")),
    path("config/", include("config.urls")),
    path("students/", include("students.urls")),
    path("organizations/", include("organizations.urls")),
]
