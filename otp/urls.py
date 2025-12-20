from django.urls import path
from .views import (
    SendOTPAPIView,
    VerifyOTPAPIView,
)

urlpatterns = [
    path("send_otp/", SendOTPAPIView.as_view(), name="send-otp"),
    path("verify_otp/", VerifyOTPAPIView.as_view(), name="verify-otp"),
]
