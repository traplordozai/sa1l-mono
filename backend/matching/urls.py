from django.urls import path
from .views import MatchingTriggerView

urlpatterns = [
    path("trigger-matching/", MatchingTriggerView.as_view(), name="trigger-matching")
]