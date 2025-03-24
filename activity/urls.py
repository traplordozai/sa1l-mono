from django.urls import path
from .views import activity_feed

urlpatterns = [
    path("", activity_feed),
]
