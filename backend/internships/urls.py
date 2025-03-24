from django.urls import path
from .views import MilestoneTimelineView

urlpatterns = [
    path("milestones/<int:internship_id>/", MilestoneTimelineView.as_view()),
]