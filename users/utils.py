"""
Helper functions for user app
"""

from django.core.mail import send_mail
from igolohomes.settings import EMAIL_HOST_USER
from rest_framework_simplejwt.tokens import RefreshToken


def upload_screenshot_path(query_instance, filename):
    """
    Generate upload path for a user's profile image.
    Example path: profile_images/5/avatar.png
    """

    return f"screenshots/{query_instance.user_fk}/{filename}"


def send_reset_email(email, reset_link):
    subject = "Reset Your Password"
    message = f"Click the link below to reset your password:\n{reset_link}"
    from_email = EMAIL_HOST_USER
    recipient_list = [email]

    send_mail(subject, message, from_email, recipient_list)


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
        "is_staff": user.is_staff,
        "is_active": user.is_active,
        "user_data": {
            "user_id": user.id,
            "email": user.email,
            "phone_number": str(user.phone_number_nn),
            "username": user.username,
            "first_name": user.first_name_nn,
            "last_name": user.last_name_nn,
            "status": user.status_nn,
            "user_type": user.user_type_nn,
            "residential_or_commercial": user.residential_or_commercial,
            "address": user.address_nn,
            "location": user.location_nn,
            "registered_date": user.registered_date
        },
    }
