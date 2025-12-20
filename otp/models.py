from django.db import models
from users.models import User


class UserOtp(models.Model):
    user_fk = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="user name"
    )
    is_verified_email = models.BooleanField(default=False)
    email_otp = models.CharField(max_length=6, null=True, blank=True)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user_fk.email}"
