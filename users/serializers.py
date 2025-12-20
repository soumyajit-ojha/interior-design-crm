"""
This module defines serializers for the applications.
Each serializer is associated with a specific model and includes fields relevant to that model.
"""

from rest_framework import serializers
from users.models import User, UserQuery
from django.core.validators import RegexValidator
from django.utils import timezone
from videos.serializers import VideoUserSerializer
from utils.constants import MAX_MESSAGE_LENGTH, MAX_SCREENSHOT_FILE_SIZE
from django.utils.http import urlsafe_base64_decode
import re


class UserSerializer(serializers.ModelSerializer):
    """
    This serializer is used for serializing  User model instances.

    It inherits from `ModelSerializer` to automatically generate fields based on the User model.
    """

    class Meta:
        """
        Meta class for User Serialize
        """

        model = User
        fields = [
            "id",
            "username",
            "first_name_nn",
            "last_name_nn",
            "phone_number_nn",
            "email",
            "address_nn",
            "location_nn",
            "residential_or_commercial",
            "status_nn",
            "user_type_nn",
        ]


class UserDetailSerializer(serializers.ModelSerializer):
    """
    This serializer is used for serializing  User model instances.

    It inherits from `ModelSerializer` to automatically generate fields based on the User model.
    """

    videos = VideoUserSerializer(many=True)

    class Meta:
        """
        Meta class for User Serialize
        """

        model = User
        fields = [
            "id",
            "username",
            "first_name_nn",
            "last_name_nn",
            "phone_number_nn",
            "email",
            "address_nn",
            "location_nn",
            "residential_or_commercial",
            "status_nn",
            "user_type_nn",
            "videos",
        ]


class UserClientSerializer(serializers.ModelSerializer):
    """
    This serializer is used for creating new client user instances.

    It inherits from `ModelSerializer` and provides fields for basic user information and
    a password field.

    """

    password = serializers.CharField(
        write_only=True,
        validators=[
            RegexValidator(
                regex=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+])[a-zA-Z\d!@#$%^&*()_+]{8,}$",
                message="Password must contain at least 8 characters, including uppercase, lowercase, and numbers.",
            )
        ],
    )

    class Meta:
        """
        Meta class for UserClient Serializer
        """

        model = User
        fields = [
            "id",
            "username",
            "first_name_nn",
            "last_name_nn",
            "phone_number_nn",
            "address_nn",
            "location_nn",
            "email",
            "residential_or_commercial",
            "status_nn",
            "user_type_nn",
            "password",
            "registered_date",
        ]

    def create(self, validated_data):
        validated_data["user_type_nn"] = "client"
        password = validated_data.pop("password")
        instance = User.objects.create(**validated_data)
        registered_date = validated_data.pop("registered_date", timezone.now())
        instance.set_password(password)
        instance.save()
        return instance


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    This serializer is used for updating existing user instances.

    It inherits from `ModelSerializer` and allows updating specific user information.
    """

    class Meta:
        """
        Meta class for UserUpdate Serializer
        """

        model = User
        fields = [
            "first_name_nn",
            "last_name_nn",
            "email",
            "address_nn",
            "location_nn",
            "status_nn",
        ]

    def update(self, instance, validated_data):
        instance.first_name_nn = validated_data.get(
            "first_name_nn", instance.first_name_nn
        )
        instance.last_name_nn = validated_data.get(
            "last_name_nn", instance.last_name_nn
        )
        instance.email = validated_data.get("email", instance.email)
        instance.address_nn = validated_data.get("address_nn", instance.address_nn)
        instance.location_nn = validated_data.get("location_nn", instance.location_nn)
        instance.status_nn = validated_data.get("status_nn", instance.status_nn)
        instance.save()
        return instance


class UserQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserQuery
        fields = [
            "id",
            "user_fk",
            "category_nn",
            "subject_nn",
            "message_nn",
            "screenshots",
        ]
        read_only_fields = ["id"]

    def validate_message_nn(self, value):
        """
        Ensure the message length is within allowed limits.
        """
        length = len(value.strip())
        if length == 0:
            raise serializers.ValidationError("Message cannot be blank.")
        if length > MAX_MESSAGE_LENGTH:
            raise serializers.ValidationError(
                f"Message is too long (max {MAX_MESSAGE_LENGTH} characters)."
            )
        return value

    def validate_screenshots(self, value):
        """
        Ensure uploaded file is not larger than 5MB.
        """
        if value and hasattr(value, "size"):
            if value.size > MAX_SCREENSHOT_FILE_SIZE:
                raise serializers.ValidationError(
                    f"Image size should not exceed {MAX_SCREENSHOT_FILE_SIZE // (1024*1024)} MB."
                )
        return value


class ForgotPasswordSerializer(serializers.Serializer):
    """
    serializers for forgot password using email
    """

    email = serializers.EmailField(required=False)
    username = serializers.CharField(required=False)

    def validate(self, data):
        """
        added validation for
        """
        email = data.get("email")
        if not email:
            raise serializers.ValidationError("email is required.")
        return data


class ResetPasswordSerializer(serializers.Serializer):
    """
    serializer for reset password
    """

    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        """
        Adding validation for new password and confirm_password
        """
        password = data["new_password"]
        confirm = data["confirm_password"]

        if password != confirm:
            raise serializers.ValidationError("Passwords do not mactched")
        if len(password) < 8:
            raise serializers.ValidationError("Password must be 8 charecters")
        if not re.search(r"[A-Z]", password):
            raise serializers.ValidationError(
                "Password must contain at least one uppercase letter"
            )
        if not re.search(r"[a-z]", password):
            raise serializers.ValidationError(
                "Password must contain at least one lowercase letter"
            )
        if not re.search(r"\d", password):
            raise serializers.ValidationError(
                "Password must contain at least one digit"
            )
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise serializers.ValidationError(
                "Password must contain at least one special character"
            )
        try:
            uidb64 = data.get("uid")
            decoded_uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=decoded_uid)
        except (User.DoesNotExist, ValueError, TypeError):
            raise serializers.ValidationError("Invalid user identifier.")

        if user.check_password(password):
            raise serializers.ValidationError(
                "New password cannot be the same as the current password."
            )

        return data
