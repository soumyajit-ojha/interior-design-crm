"""
This file contains all view functions for the users app.

All views use Django's API views as a base and handle GET POST and DELETE requests.

Requires authentication for all views.
"""

# Standard Library
from datetime import datetime

# Third-Party Libraries
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes, DjangoUnicodeDecodeError
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.views import TokenRefreshView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from rest_framework import generics
# First-Party Imports (Your Project)
from users.models import User, UserQuery
from users.serializers import (
    UserSerializer,
    UserDetailSerializer,
    UserClientSerializer,
    UserUpdateSerializer,
    UserQuerySerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
)
from videos.models import VideoUser
from videos.serializers import VideoUserSerializer
from igolohomes.custom_logger import log_message
from utils.response_utils import (
    response_success,
    response_bad_request,
    response_created,
    response_not_found,
    response_server_error,
    response_unauthorized,
)
from .utils import send_reset_email, get_tokens_for_user

module = str((__name__).split(".")[0])


class UserList(APIView):
    """
    API view to handle GET and POST requests for a list of users.
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieves and returns a list of clients (users with user_type='client').",
        responses={200: UserSerializer(many=True)},
    )
    def get(self, request):
        users = User.objects.filter(user_type_nn="client")
        serializer = UserSerializer(users, many=True)
        # log-message
        msg = f"[GET] UserList called by user: {request.user.username}"
        log_message(module_name="users", message=msg, level="INFO")
        return response_success(
            data=serializer.data, message="User list retrive successfully"
        )

    @swagger_auto_schema(
        operation_description="Creates a new user based on the provided data in the request.",
        request_body=UserSerializer,
        responses={201: UserSerializer, 400: "Validation error"},
    )
    def post(self, request):
        try:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                # log-message
                msg = f"[POST] UserList created by user: {request.user.username} with data: {request.data}"
                log_message(module_name=module, message=msg, level="INFO")
                return response_created(
                    data=serializer.data, message="User list created successfully"
                )
            # log-message
            msg = f"[POST] Invalid data (or already exist.) send by user: {request.user.username} with data: {request.data}"
            log_message(module_name=module, message=msg, level="WARNING")
            return response_bad_request(
                errors=serializer.errors, message="Data already exits"
            )
        except Exception as e:
            msg = f"[POST] Invalid data (or already exist.) send by user: {request.user.username} with error: {str(e)}"
            log_message(module_name=module, message=msg, level="ERROR")
            return response_bad_request(
                errors=serializer.errors, message="Invalid data"
            )


class UserDetail(APIView):
    """
    API view to handle GET and DELETE requests for a user detail.
    """

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise NotFound("User not found")

    @swagger_auto_schema(
        operation_description="Retrieves and returns a user detail.",
        responses={200: UserDetailSerializer, 404: "User not found"},
    )
    def get(self, request, pk):
        try:
            user = self.get_object(pk)
            serializer = UserDetailSerializer(user)
            # log-message
            msg = f"[GET] UserDetails called by user: {request.user.username}."
            log_message(module_name=module, message=msg, level="INFO")
            return response_success(
                data=serializer.data, message="User details retrive sucessfully"
            )
        except NotFound as e:
            # log-message
            msg = (
                f"[GET] UserDetails NotFound, called by user: {request.user.username}."
            )
            log_message(module_name=module, message=msg, level="WARNING")
            return response_not_found("User details are not found")
        except Exception as e:
            # log-message
            msg = f"[GET] UserDetails called by user: {request.user.username}."
            log_message(module_name=module, message=msg, level="ERROR")
            return response_server_error(message="Internal server error")

    @swagger_auto_schema(
        operation_description="Deletes a user based on the provided primary key.",
        responses={204: "No Content", 403: "Forbidden", 404: "User not found"},
    )
    def delete(self, request, pk):
        try:
            user = self.get_object(pk)
            if not request.user.is_staff:
                raise PermissionDenied(
                    "You do not have permission to perform this action."
                )
            user.delete()
            # log-message
            msg = f"[DELETE] UserDetails called by user: {request.user.username}."
            log_message(module_name=module, message=msg, level="INFO")
            return response_success(message="User_details deleted sucessfully")
        except NotFound as e:
            # log-message
            msg = f"[DELETE] UserDetails NotFound, called by user: {request.user.username}."
            log_message(module_name=module, message=msg, level="ERROR")
            return response_not_found(
                {"error": str(e)}, status=status.HTTP_404_NOT_FOUND
            )
        except PermissionDenied as e:
            # log-message
            msg = f"[DELETE] UserDetails Permissiondenied for user: {request.user.username}."
            log_message(module_name=module, message=msg, level="ERROR")
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            # log-message
            msg = f"[DELETE] UserDetails Exception Raise, called by user: {request.user.username}."
            log_message(module_name=module, message=msg, level="ERROR")
            return Response(
                {"error": "Internal Server Error: " + str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class LoginView(APIView):
    """
    API view to handle POST request to login.
    """

    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Logins to the admin panel.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "username": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Username"
                ),
                "password": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Password"
                ),
            },
            required=["username", "password"],
        ),
        responses={
            200: openapi.Response(
                description="A JSON response containing the serialized data of the logged in admin.",
                examples={
                    "application/json": {
                        "refresh": "refresh_token",
                        "access": "access_token",
                    }
                },
            ),
            401: openapi.Response(
                description="Invalid credentials.",
                examples={"application/json": {"detail": "Invalid credentials"}},
            ),
            500: openapi.Response(
                description="Internal Server Error",
                examples={
                    "application/json": {
                        "error": "Internal Server Error: error details"
                    }
                },
            ),
        },
    )
    def post(self, request):
        try:
            email = request.data.get("email")
            password = request.data.get("password")
            userfound = User.objects.filter(email=email).first()
            if not userfound:
                # log-message : warning
                msg = f"[POST] LoginView Invalid credential user: {email}"
                log_message(module_name=module, message=msg, level="WARNING")
                return Response(
                    {"detail": "Invalid credentials"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            user = authenticate(username=userfound.username, password=password)

            if user:
                token_data = get_tokens_for_user(user)
                msg = f"[POST] Superuser logged in successfully user: {email}."
                log_message(module_name=module, message=msg, level="INFO")

                return Response(
                    token_data,
                    status=status.HTTP_200_OK,
                )
            else:
                msg = f"[POST] LoginView Invalid credential user: {email}"
                log_message(module_name=module, message=msg, level="WARNING")
                return Response(
                    {"detail": "Invalid credentials"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
        except Exception as e:
            msg = f"[POST] LoginView Exception raised,  user: {email}"
            log_message(module_name=module, message=msg, level="ERROR")

            return Response(
                {"error": "Internal Server Error: " + str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ClientCreateAPIView(APIView):
    """
    API view to handle POST request to create a client profile.
    """

    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Creates a new client user based on the provided data in the request.",
        request_body=UserClientSerializer,
        responses={
            201: UserClientSerializer,
            400: "Validation error",
            500: "Internal Server Error",
        },
    )
    def post(self, request):
        try:
            residential_or_commercial = request.data.get("residential_or_commercial")

            prefix = (
                "IgoloR" if residential_or_commercial == "residential" else "IgoloC"
            )
            last_user = (
                User.objects.filter(residential_or_commercial=residential_or_commercial)
                .order_by("-id")
                .first()
            )
            last_id = last_user.id if last_user else 0
            new_id = last_id + 1
            formatted_id = "{:03}".format(new_id)
            username = f"{prefix}_{formatted_id}"
            request.data["username"] = username
            serializer = UserClientSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                # log-message
                msg = f"[POST] ClientCreateAPIView Client Created by user: {request.user.username} for {username}"
                log_message(module_name=module, message=msg, level="INFO")

                return Response(serializer.data, status=status.HTTP_201_CREATED)
            # log-message : error
            msg = f"[POST] ClientCreateAPIView Invalid credentials by user: {request.user.username} for {username}"
            log_message(module_name=module, message=msg, level="WARNING")

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # print(str(e))
            # log-message : error
            msg = f"[POST] ClientCreateAPIView Exception raised by user:{request.user.username} for {username}"
            log_message(module_name=module, message=msg, level="ERROR")

            return Response(
                {"error": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ClientLoginView(APIView):
    """
    API view to handle POST request to login the client.
    """

    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Logins to the client.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "username": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Username"
                ),
                "password": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Password"
                ),
            },
            required=["username", "password"],
        ),
        responses={
            200: openapi.Response(
                description="A JSON response containing the serialized data of the logged in client.",
                examples={
                    "application/json": {
                        "id": 1,
                        "refresh": "refresh_token",
                        "access": "access_token",
                    }
                },
            ),
            401: openapi.Response(
                description="Invalid credentials.",
                examples={"application/json": {"detail": "Invalid credentials"}},
            ),
            500: openapi.Response(
                description="Internal Server Error",
                examples={
                    "application/json": {
                        "error": "Internal Server Error: error details"
                    }
                },
            ),
        },
    )
    def post(self, request):
        try:
            email = request.data.get("email")
            password = request.data.get("password")
            user = authenticate(email=email, password=password)

            if user and user.user_type_nn == "client":
                refresh = RefreshToken.for_user(user)
                # log-message : error
                msg = f"[POST] ClientLoginView Client logged in successfully by user: {email}"
                log_message(module_name=module, message=msg, level="INFO")

                return Response(
                    {
                        "id": user.id,
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                # log-message : warning
                msg = f"[POST] ClientLoginView Invalid credential by user: {email}"
                log_message(module_name=module, message=msg, level="WARNING")

                return Response(
                    {"detail": "Invalid credentials"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
        except Exception as e:
            # log-message : error
            msg = f"[POST] ClientLoginView Exception raised by user: {email}"
            log_message(module_name=module, message=msg, level="ERROR")

            return Response(
                {"detail": "An unexpected error occured. Please try again later"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ClientVideoDetail(APIView):
    """
    API view to handle GET request to retrieve Video details of a client.
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieves and returns video details of a client.",
        responses={
            200: VideoUserSerializer(many=True),
            401: "Invalid user type",
            500: "Internal Server Error",
        },
    )
    def get(self, request):
        try:
            user = request.user

            if user.user_type_nn == "client":
                videos = VideoUser.objects.filter(user_fk=user.id)
                serializer = VideoUserSerializer(videos, many=True)
                # log-message
                msg = f"[GET] ClientVideoDetail Video Found by user: {user.username}"
                log_message(module_name=module, message=msg, level="INFO")
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                # log-message
                msg = f"[GET] ClientVideoDetail Invalid user type by user: {user.username}"
                log_message(module_name=module, message=msg, level="WARNING")
                return Response(
                    {"detail": "Invalid user type"}, status=status.HTTP_401_UNAUTHORIZED
                )
        except Exception as e:
            # log-message
            msg = f"[GET] ClientVideoDetail  by user: {user.username} error: {str(e)}"
            log_message(module_name=module, message=msg, level="ERROR")
            return Response(
                {"error": "Internal Server Error: " + str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UpdateUserDetail(APIView):
    """
    API view to handle PUT request to Update client details.
    """

    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Updates a user partially based on the provided data in the request.",
        request_body=UserUpdateSerializer,
        responses={
            200: UserUpdateSerializer,
            400: "Validation error",
            404: "User not found",
            500: "Internal Server Error",
        },
    )
    def put(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except ObjectDoesNotExist:
            # log-message
            msg = f"[PUT] UpdateUserDetail User not found by user: {request.user.username}"
            log_message(module_name=module, message=msg, level="ERROR")
            return Response(
                {"error": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        try:
            if serializer.is_valid():  ###
                serializer.save()
                # log-message
                msg = f"[PUT] UpdateUserDetail Updated by user: {request.user.username} for user: {user.username}"
                log_message(module_name=module, message=msg, level="INFO")
                return Response(serializer.data)
            else:
                # log-message
                msg = f"[PUT] UpdateUserDetail Bad Request by user: {request.user.username}."
                log_message(module_name=module, message=msg, level="WARNING")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # log-message
            msg = f"[PUT] UpdateUserDetail Exception Raised by user: {request.user.username} error: {str(e)}."
            log_message(module_name=module, message=msg, level="ERROR")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UpdateNewPassword(APIView):
    """
    API view to update a user's password for authorized admin users.

    Requires authentication as an admin user for all requests.
    """

    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Updates the password for a specified user.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "old_password": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Old Password"
                ),
                "new_password": openapi.Schema(
                    type=openapi.TYPE_STRING, description="New Password"
                ),
            },
            required=["old_password", "new_password"],
        ),
        responses={
            200: "Password updated successfully",
            400: "Old password and new password are required",
            404: "User does not exist",
            500: "Internal Server Error",
        },
    )
    def post(self, request, pk):
        try:
            old_password = request.data.get("old_password")
            new_password = request.data.get("new_password")

            if not old_password or not new_password:
                # log-message
                msg = f"[POST] UpdateNewPassword old and new password are required, by user: {request.user.username}"
                log_message(module_name=module, message=msg, level="WARNING")
                return Response(
                    {"error": "Old password and new password are required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            # log-message
            msg = f"[POST] UpdateNewPassword User Not Found by user: {request.user.username}"
            log_message(module_name=module, message=msg, level="WARNING")
            return Response(
                {"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            # log-message
            msg = f"[POST] UpdateNewPassword Exception Raised by user: {request.user.username} error: {str(e)}"
            log_message(module_name=module, message=msg, level="ERROR")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        if not user.check_password(old_password):
            # log-message
            msg = f"[POST] UpdateNewPassword Old password incorrect by user: {request.user.username}"
            log_message(module_name=module, message=msg, level="WARNING")
            return Response(
                {"error": "Old password is incorrect"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user.set_password(new_password)
            user.save()
        except Exception as e:
            # log-message
            msg = f"[POST] UpdateNewPassword Exception Raised by user: {request.user.username} error:{str(e)}"
            log_message(module_name=module, message=msg, level="ERROR")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        # log-message
        msg = f"[POST] UpdateNewPassword Password updated by user: {request.user.username}"
        log_message(module_name=module, message=msg, level="INFO")
        return Response(
            {"success": "Password updated successfully"}, status=status.HTTP_200_OK
        )


class UserQueryCreatAPIView(APIView):
    """
    This APIView handle the creation of user query and retrieve
    """

    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request: Request):
        """
        This Post methos handle the creation of query creation.
        """
        try:
            serializer = UserQuerySerializer(data=request.data)

            if serializer.is_valid():
                serializer.save(user_fk=request.user)

                return Response(
                    {
                        "message": "Query submitted successfully.",
                        "data": serializer.data,
                    },
                    status=status.HTTP_201_CREATED,
                )

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # print(str(e))
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserQueryRetrieveAPIView(APIView):
    """
    This APIView handle the creation of user query and retrieve
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        """
        this method handle the query retrival of authenticated user.
        """
        try:
            user = request.user
            querysets = UserQuery.objects.filter(user_fk=user)
            if not querysets or (len(querysets) == 0):
                raise UserQuery.DoesNotExist

            serializer = UserQuerySerializer(querysets, many=True)
            return Response({"data": serializer.data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordView(APIView):
    """
    API for forgot password in Igolo project.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        This method handle forgot password
        """
        try:
            serializer = ForgotPasswordSerializer(data=request.data)
            if serializer.is_valid():
                email = serializer.validated_data.get("email")

                if email:
                    email = email.lower()

                try:
                    if email:
                        user = User.objects.get(email__iexact=email)
                    token = default_token_generator.make_token(user)
                    uid = urlsafe_base64_encode(force_bytes(user.pk))

                    reset_link = (
                        f"{settings.IGOLO_FRONTEND_URL}/reset-password/{uid}/{token}/"
                    )
                    send_reset_email(user.email, reset_link)
                    log_message("users", f"Password reset link sent to {user.email}")
                    log_message(
                        "users", f"Password reset link: {reset_link}", level="DEBUG"
                    )
                    return response_success(
                        message="Password reset link has been sent to your email."
                    )

                except User.DoesNotExist:
                    log_message(
                        "users", f"No user found with email: {email}", level="WARNING"
                    )
                    return response_bad_request(
                        errors="User not exit", message="User not found."
                    )
            log_message(
                "users", f"Invalid request data: {serializer.errors}", level="WARNING"
            )
            return response_bad_request(errors=serializer.errors)
        except Exception as e:
            log_message(
                "users",
                f"Exception occurred in ForgotPasswordView: {str(e)}",
                level="ERROR",
            )
            return response_bad_request(
                message="Something went wrong",
                errors="An unexpected error occurred. Please try again later.",
            )


class ResetPasswordValidateLinkView(APIView):
    """
    API to validate password reset link without actually resetting the password.
    """
    permission_classes = [AllowAny]

    def get(self, request, uid, token):
        """
        Get api to check and validate the reset url
        """
        try:
            # Decode UID and get user
            uid_decoded = urlsafe_base64_decode(uid).decode()
            user = User.objects.get(pk=uid_decoded)

            # Verify token validity
            if default_token_generator.check_token(user, token):
                return response_success(message="Token is valid.")
            else:
                return response_bad_request(errors="Invalid or expired token.", message="Invalid or expired token.")

        except (User.DoesNotExist, ValueError, TypeError, DjangoUnicodeDecodeError):
            return response_bad_request(errors="Invalid link.", message="Invalid link.")


class ResetPasswordConfirmView(APIView):
    """
    API to confirm password reset and set new password.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        This method handle reset the password using new password and confirm password
        """
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            uid = serializer.validated_data["uid"]
            token = serializer.validated_data["token"]
            new_password = serializer.validated_data["new_password"]

            try:
                uid = urlsafe_base64_decode(uid).decode()
                user = User.objects.get(pk=uid)

                if not default_token_generator.check_token(user, token):
                    log_message(
                        "users",
                        f"[ResetPasswordConfirm] Invalid or expired token for user ID: {uid}",
                        level="WARNING",
                    )
                    return response_bad_request(
                        errors="Invalid or expired token.",
                        message="Invalid or expired token.",
                    )

                user.set_password(new_password)
                user.save()
                log_message(
                    "users",
                    f"[ResetPasswordConfirm] Password reset successful for user: {user.email}",
                )
                return response_success(message="Password has been reset successfully.")

            except (User.DoesNotExist, ValueError, TypeError):
                log_message(
                    "users",
                    f"[ResetPasswordConfirm] Invalid user or token. Error: {str(e)}",
                    level="ERROR",
                )
                return response_bad_request(
                    errors="Invalid user or token.", message="Invalid user or token."
                )
        log_message(
            "users",
            f"[ResetPasswordConfirm] Validation error: {serializer.errors}",
            level="WARNING",
        )
        return response_bad_request(errors=serializer.errors)


@method_decorator(csrf_exempt, name="dispatch")
class CustomTokenRefreshView(TokenRefreshView):
    """
    API for generate custom refresh token
    """

    def post(self, request, *args, **kwargs):
        """
        post method for create custom refresh token
        """
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            log_message(
                "CustomTokenRefreshView",
                "Refresh token is missing in the request.",
                "WARNING",
            )
            return response_bad_request(
                errors="Refresh token is required", message="Refresh token is required."
            )

        try:
            refresh = RefreshToken(refresh_token)
            user_id = refresh["user_id"]
            user = User.objects.get(id=user_id)

            serializer = self.get_serializer(data=request.data)
            try:
                serializer.is_valid(raise_exception=True)
            except InvalidToken as e:
                log_message(
                    "CustomTokenRefreshView",
                    f"Invalid refresh token for user {user_id}: {str(e)}",
                    "WARNING",
                )
                return response_unauthorized(message=str(e))

            new_refresh = RefreshToken.for_user(user)
            new_access = new_refresh.access_token
            log_message(
                "CustomTokenRefreshView",
                f"Token refreshed successfully for user {user_id}.",
                "INFO",
            )
            return response_success(
                {
                    "refresh": str(new_refresh),
                    "access": str(new_access),
                    "expires_in": new_access["exp"],
                },
                message="Tokens refreshed successfully.",
            )

        except User.DoesNotExist:
            log_message(
                "CustomTokenRefreshView",
                f"User with ID {user_id} not found while refreshing token.",
                "ERROR",
            )
            return response_unauthorized(
                message="The user associated with this token no longer exists."
            )
        except InvalidToken as e:
            log_message(
                "CustomTokenRefreshView", f"Invalid or expired token: {str(e)}", "ERROR"
            )
            return response_unauthorized(message="Invalid or expired refresh token.")

class UserListByTypeAPIView(generics.ListAPIView):
    """
    API view to handle GET requests for a list of users filtered by user_type_nn.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    @swagger_auto_schema(
        operation_description="Retrieves and returns a list of users filtered by user_type_nn.",
        responses={200: UserSerializer(many=True)},
    )
    def get_queryset(self):
        user_type_param = self.request.query_params.get("user_type")
        if user_type_param:
            user_types = [ut.strip() for ut in user_type_param.split(",") if ut.strip()]
            return User.objects.filter(user_type_nn__in=user_types)
        return User.objects.all()
        # if user_type:
        #     return User.objects.filter(user_type_nn=user_type)
        # return User.objects.all()
