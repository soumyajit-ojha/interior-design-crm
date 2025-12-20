from django.core.mail import send_mail
from igolohomes.settings import EMAIL_HOST
from random import randint
from django.utils import timezone
from datetime import timedelta

now = timezone.now()


def generate_otp():
    otp = str(randint(100000, 999999))
    expiry_time = now + timedelta(minutes=5)  # 5 minutes validity
    return (otp, expiry_time)


def verify_otp(user_otp_obj, user_otp):
    """
    it check otp validation cases as its already used, expiry and verify the user otp.
    return a tuple of bollean value and a string message.
    """
    if user_otp_obj.expired_at < now:
        return False, "OTP expired."
    if user_otp_obj.email_otp != user_otp:
        return False, "Wrong OTP. Try again."
    if user_otp_obj.is_used:
        return False, "OTP already used."

    return True, None


def send_otp_via_email(email: str, otp: int):
    subject = "igolohomes: OTP Verification"
    otp = str(otp)
    message = f"Your OTP is {otp}. Use this to verify your email on igolohomes. Valid for 5 minutes."
    from_email = EMAIL_HOST
    recipient_list = [email]

    send_mail(subject, message, from_email, recipient_list, fail_silently=False)
