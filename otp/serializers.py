from django.core.validators import RegexValidator
from rest_framework import serializers
from users.models import User
from .models import UserOtp


class UserOtpSerializer(serializers.ModelSerializer):
    """
    This serializer handles otp stuffs.
    """

    class Meta:
        model = UserOtp
        fields = [
            "user_fk",
            "is_verified_email",
            "email_otp",
            "is_used",
            "created_at",
            "expired_at",
        ]


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    email_otp = serializers.CharField(max_length=6)
