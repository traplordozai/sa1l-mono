from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import User, UserRole, UserInvite, OTP, EmailVerificationToken

class UserModelTest(TestCase):
    def setUp(self):
        self.role = UserRole.objects.create(name="test_role")
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            role="intern"
        )

    def test_user_creation(self):
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user.email, "test@example.com")
        self.assertEqual(self.user.role, "intern")
        self.assertTrue(self.user.check_password("testpass123"))

class UserAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            role="intern"
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse("user-profile")

    def test_get_profile(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testuser")
        self.assertEqual(response.data["email"], "test@example.com")

    def test_update_profile(self):
        data = {
            "first_name": "Test",
            "last_name": "User"
        }
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "Test")
        self.assertEqual(response.data["last_name"], "User")

class AuthenticationTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            role="intern"
        )
        self.login_url = reverse("user-login")
        self.verify_url = reverse("user-verify-otp")

    def test_login(self):
        data = {
            "username": "testuser",
            "password": "testpass123"
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(OTP.objects.filter(user=self.user).exists())

    def test_verify_otp(self):
        otp = OTP.objects.create(user=self.user, code="123456")
        data = {"code": "123456"}
        response = self.client.post(self.verify_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("access" in response.data)
        self.assertTrue("refresh" in response.data)

class UserInviteTest(APITestCase):
    def setUp(self):
        self.role = UserRole.objects.create(name="test_role")
        self.invite = UserInvite.objects.create(
            email="invited@example.com",
            role=self.role
        )
        self.accept_url = reverse("user-accept-invite")

    def test_accept_invite(self):
        data = {
            "token": str(self.invite.token),
            "username": "inviteduser",
            "password": "testpass123"
        }
        response = self.client.post(self.accept_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(User.objects.filter(username="inviteduser").exists())
        self.invite.refresh_from_db()
        self.assertTrue(self.invite.accepted) 