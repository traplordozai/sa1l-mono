from django.urls import path
from .views import (
    StudentProfileView,
    StudentDashboardView,
    StudentApplicationsView,
    StudentFeedbackView,
    StudentLearningPlanView
)

urlpatterns = [
    path('profile/', StudentProfileView.as_view(), name='student-profile'),
    path('dashboard/', StudentDashboardView.as_view(), name='student-dashboard'),
    path('applications/', StudentApplicationsView.as_view(), name='student-applications'),
    path('feedback/', StudentFeedbackView.as_view(), name='student-feedback'),
    path('learning-plan/', StudentLearningPlanView.as_view(), name='student-learning-plan'),
] 