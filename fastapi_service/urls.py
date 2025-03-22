from django.urls import path
from .views import TokenLoginView, PasswordResetView, UserDetailView, AdminChatLogsView

urlpatterns = [
    path("api/auth/login/", TokenLoginView.as_view()),
    path("api/auth/password-reset/", PasswordResetView.as_view()),
    path("api/auth/user/", UserDetailView.as_view()),
    path("api/chat/logs/", AdminChatLogsView.as_view()),
]
