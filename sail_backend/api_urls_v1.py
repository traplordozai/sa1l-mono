from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("status/", include("sail_backend.status_urls")),
    path("dev/", include("sail_backend.dev_urls")),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema")),
    path("users/", include("users.urls")),
    path("applications/", include("applications.urls")),
    path("feedback/", include("feedback.urls")),
    path("forms/", include("forms.urls")),
    path("matching/", include("matching.urls")),
    path("config/", include("config.urls")),
]
