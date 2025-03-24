from django.urls import path
from .status_views import system_status

urlpatterns = [
    path("", system_status),
]
