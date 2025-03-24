from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.core.mail import send_mail
from .models import User, OTP, UserInvite, EmailVerificationToken
from .serializers import (
    LoginSerializer, OTPVerifySerializer, InviteAcceptSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    ProfileSerializer
)
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from rest_framework.permissions import IsAdminUser
from django.db.models import Count, Max
from .models import UserActivityLog
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
import random

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # ✅ Generate + send OTP
        otp = str(random.randint(100000, 999999))
        OTP.objects.create(user=user, code=otp)

        send_mail("Your OTP", f"Your OTP is: {otp}", "noreply@example.com", [user.email])

        # ✅ Log the login attempt
        UserActivityLog.objects.create(
            user=user,
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            action="login",
        )

        return Response({"detail": "OTP sent"}, status=200)

class VerifyOTPView(APIView):
    def post(self, request):
        code = request.data.get("code")
        otp = OTP.objects.filter(user=request.user, code=code).last()

        if not otp or otp.is_expired():
            return Response({"error": "Invalid or expired OTP"}, status=400)

        OTP.objects.filter(user=request.user).delete()
        refresh = RefreshToken.for_user(request.user)
        return Response({"access": str(refresh.access_token), "refresh": str(refresh)}, status=200)

class AcceptInviteView(APIView):
    def post(self, request):
        serializer = InviteAcceptSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']
        try:
            invite = UserInvite.objects.get(token=token, accepted=False)
        except UserInvite.DoesNotExist:
            return Response({"error": "Invalid token"}, status=400)

        user = User.objects.create_user(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password'],
            email=invite.email,
            role=invite.role,
            is_verified=True
        )
        invite.accepted = True
        invite.save()

        verification = EmailVerificationToken.objects.create(user=user)
        site = request.get_host()
        verify_url = f"http://{site}/auth/verify-email/?token={verification.token}"
        send_mail("Verify your email", f"Click to verify: {verify_url}", "noreply@example.com", [user.email])

        return Response({"message": "Invite accepted"}, status=201)

class PasswordResetRequestView(APIView):
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "If that email exists, a reset link has been sent."}, status=200)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_link = f"{request.get_host()}/reset-password/?uid={uid}&token={token}"

        send_mail("Password Reset", f"Reset your password: {reset_link}", "noreply@example.com", [email])
        return Response({"detail": "Reset link sent."})

class PasswordResetConfirmView(APIView):
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uid = force_str(urlsafe_base64_decode(serializer.validated_data["uid"]))
        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["new_password"]

        try:
            user = User.objects.get(pk=uid)
        except User.DoesNotExist:
            return Response({"error": "Invalid UID"}, status=400)

        if not default_token_generator.check_token(user, token):
            return Response({"error": "Invalid or expired token"}, status=400)

        user.set_password(new_password)
        user.save()
        return Response({"message": "Password has been reset."})

class EmailVerificationView(APIView):
    def get(self, request):
        token_str = request.GET.get("token")
        try:
            token = EmailVerificationToken.objects.get(token=token_str)
        except EmailVerificationToken.DoesNotExist:
            return Response({"error": "Invalid token"}, status=400)

        if token.is_expired():
            return Response({"error": "Expired token"}, status=400)

        user = token.user
        user.is_verified = True
        user.save()
        token.delete()
        return Response({"message": "Email verified successfully"})

class AdminAnalyticsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        logins_per_user = UserActivityLog.objects.filter(action="login") \
            .values("user__username") \
            .annotate(total=Count("id"))

        last_login = UserActivityLog.objects.filter(action="login") \
            .values("user__username") \
            .annotate(last=Max("timestamp"))

        device_stats = UserActivityLog.objects.filter(action="login") \
            .values("user_agent") \
            .annotate(count=Count("id"))

        return Response({
            "logins_per_user": list(logins_per_user),
            "last_login": list(last_login),
            "device_stats": list(device_stats),
        })

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh = request.data["refresh"]
            token = RefreshToken(refresh)
            token.blacklist()
            return Response({"message": "Logout successful"})
        except Exception:
            return Response({"error": "Invalid refresh token"}, status=400)

class CreateUserView(APIView):
    permission_classes = [RolePermission]
    allowed_roles = ["admin"]

    def post(self, request):
        # user creation logic here
        return Response({"message": "User created"})

class UserStatusUpdateView(APIView):
    permission_classes = [RolePermission]
    allowed_roles = ["admin"]

    def post(self, request, user_id):
        status = request.data.get("status")
        if status not in ["active", "inactive", "suspended"]:
            return Response({"error": "Invalid status"}, status=400)

        user = User.objects.get(id=user_id)
        user.status = status
        user.save()
        return Response({"message": "Status updated"})

class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        old = request.data.get("old_password")
        new = request.data.get("new_password")

        if not request.user.check_password(old):
            return Response({"error": "Incorrect old password"}, status=400)

        request.user.set_password(new)
        request.user.save()
        return Response({"message": "Password updated"})

class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(ProfileSerializer(request.user).data)

    def put(self, request):
        serializer = ProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)