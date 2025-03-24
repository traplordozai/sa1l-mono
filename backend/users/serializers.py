from rest_framework import serializers
from .models import User, UserInvite, OTP
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.tokens import default_token_generator


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if not user:
            raise serializers.ValidationError("Invalid login")
        return {"user": user}

class OTPVerifySerializer(serializers.Serializer):
    code = serializers.CharField()

class InviteAcceptSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    username = serializers.CharField()
    password = serializers.CharField()

class UserInviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInvite
        fields = '__all__'

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField()

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "avatar", "role", "status"]
        read_only_fields = ["role", "status"]
