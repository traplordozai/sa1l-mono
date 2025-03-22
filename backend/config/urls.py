from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # API v1 routes
    path("api/v1/", include("backend.api.v1.urls")),
    # Legacy or unversioned routes if needed
    path("api/", include("backend.api.urls")),
]
