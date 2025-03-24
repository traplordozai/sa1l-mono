from django.urls import path
from .views import SubmitFeedbackView, GetFeedbackView

urlpatterns = [
    path("submit/", SubmitFeedbackView.as_view()),
    path("user/<int:user_id>/", GetFeedbackView.as_view()),
]