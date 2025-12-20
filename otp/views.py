from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserOtpSerializer, VerifyOTPSerializer
from .utils import generate_otp, verify_otp, send_otp_via_email
from .models import UserOtp
from users.models import User
from igolohomes.custom_logger import log_message

module = str((__name__).split(".")[0])


class SendOTPAPIView(APIView):
    """
    This APIView Used for authenticate through email otp.'
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request: Request):
        email = request.data.get("email")
        try:
            if not email:
                raise ValueError("Email must required to send OTP.")
            user = User.objects.get(email=email)
            if not user:
                raise User.DoesNotExist
        except Exception as e:
            # log-message
            msg = f"[POST] SendOTPAPIView called by email: '{email}' error raised"
            log_message(module_name=module, message=msg, level="ERROR")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            # log-message
            msg = (
                f"[POST] SendOTPAPIView called by email: '{email}' no registered user."
            )
            log_message(module_name=module, message=msg, level="ERROR")
            return Response(
                {"error": f"User doesn't exist with email '{email}'"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            otp_user_obj, _ = UserOtp.objects.get_or_create(user_fk=user)
            otp, expiry_time = generate_otp()

            payloads = {"email_otp": otp, "expired_at": expiry_time, "is_used": False}
            serializer = UserOtpSerializer(
                instance=otp_user_obj, data=payloads, partial=True
            )
            if serializer.is_valid():
                serializer.save()

                send_otp_via_email(email=email, otp=otp)
                # log-message
                msg = f"[POST] SendOTPAPIView called by email: '{email}' OTP sent."
                log_message(module_name=module, message=msg, level="INFO")
                return Response(
                    # {"data": f"{serializer.data}", "msg": "otp sent to your mail."}, # for testing purpose
                    {"msg": "otp sent to your mail."},
                    status=status.HTTP_200_OK,
                )
            # log-message
            msg = f"[POST] SendOTPAPIView called by email: '{email}'"
            log_message(module_name=module, message=msg, level="WARNING")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # log-message
            msg = f"[POST] SendOTPAPIView called by email: '{email}' error raised"
            log_message(module_name=module, message=msg, level="ERROR")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPAPIView(APIView):
    """
    APIView to handle OTP verification .
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request: Request):
        serializer = VerifyOTPSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            email = serializer.data.get("email")
            user_otp = serializer.data.get("email_otp")
            try:
                user = User.objects.get(email=email)
                user_otp_obj = UserOtp.objects.get(user_fk=user)
                result, error_message = verify_otp(user_otp_obj, user_otp)

                # if otp not valid
                if not result:
                    # log-message
                    msg = f"[POST] VerifyOTPAPIView called by email: '{email}' OTP not valid."
                    log_message(module_name=module, message=msg, level="WARNING")
                    return Response(
                        {"error": str(error_message)},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                # if otp valid
                user_otp_obj.is_verified_email = True
                user_otp_obj.is_used = True
                user_otp_obj.save()
                # log-message
                msg = (
                    f"[POST] VerifyOTPAPIView called by email: '{email}' OTP verified."
                )
                log_message(module_name=module, message=msg, level="INFO")
                # OTP generation
                refresh = RefreshToken.for_user(user)
                return Response(
                    {
                        "tokens": {
                            "refresh": str(refresh),
                            "access": str(refresh.access_token),
                        }
                    },
                    status=status.HTTP_200_OK,
                )

            # Exceptions
            except User.DoesNotExist:
                # log-message
                msg = f"[POST] VerifyOTPAPIView called by email: '{email}' no registered user."
                log_message(module_name=module, message=msg, level="WARNING")
                return Response(
                    {"error": f"User with email '{email}' doesn't exist."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except UserOtp.DoesNotExist:
                # log-message
                msg = (
                    f"[POST] VerifyOTPAPIView called by email: '{email}' no OTP found."
                )
                log_message(module_name=module, message=msg, level="WARNING")
                return Response(
                    {"error": f"OTP for email '{email}' not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except Exception as e:
                # log-message
                msg = (
                    f"[POST] VerifyOTPAPIView called by email: '{email}' error raised."
                )
                log_message(module_name=module, message=msg, level="ERROR")
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # if serializer is not valid.
        # log-message
        msg = (
            f"[POST] VerifyOTPAPIView called by email: '{email}' serializer not valid."
        )
        log_message(module_name=module, message=msg, level="ERROR")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
