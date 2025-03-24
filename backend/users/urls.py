from django.urls import path
from .views import (
    LoginView, VerifyOTPView, AcceptInviteView,
    PasswordResetRequestView, PasswordResetConfirmView, 
    EmailVerificationView, AdminAnalyticsView,
    LogoutView, CreateUserView, ProfileView, 
    ChangePasswordView, UserStatusUpdateView
)

urlpatterns = [
    path("auth/login/", LoginView.as_view()),
    path("auth/verify-otp/", VerifyOTPView.as_view()),
    path("auth/invite/accept/", AcceptInviteView.as_view()),
    path("auth/password-reset/", PasswordResetRequestView.as_view()),
    path("auth/password-reset/confirm/", PasswordResetConfirmView.as_view()),
    path("auth/email-verify/", EmailVerificationView.as_view()),
    path("admin/analytics/", AdminAnalyticsView.as_view()),
    path("auth/logout/", LogoutView.as_view()),
    path("me/", ProfileView.as_view()),
    path("me/password/", ChangePasswordView.as_view()),
    path("admin/users/create/", CreateUserView.as_view()),
    path("admin/users/<int:user_id>/status/", UserStatusUpdateView.as_view()),
    path("users/<int:user_id>/status/", UserStatusUpdateView.as_view()),
]
