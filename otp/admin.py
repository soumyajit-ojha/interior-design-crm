from django.contrib import admin
from .models import UserOtp

class AdminUserOTP(admin.ModelAdmin):
    list_display = [
        "user_fk",
        "is_verified_email",
        "email_otp",
        "is_used",
        "created_at",
        "expired_at",
    ]

    search_fields = [
        "user_fk",
    ]
    list_filter = ["is_verified_email", "is_used"]


admin.site.register(UserOtp, AdminUserOTP)
