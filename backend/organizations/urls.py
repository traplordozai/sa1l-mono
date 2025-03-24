from django.urls import path
from .views import MyOrganizationView, MatchedStudentsView, InterviewScheduleView, DeliverablesView

urlpatterns = [
    path("profile/", MyOrganizationView.as_view()),
    path("matches/", MatchedStudentsView.as_view()),
    path("interviews/", InterviewScheduleView.as_view()),
    path("deliverables/", DeliverablesView.as_view()),
]
