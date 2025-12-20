"""
This file contains all view functions for the users app.

All views use Django's API views as a base and handle GET POST and DELETE requests.

Requires authentication for all views.
"""

# from io import BytesIO
# import tempfile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate

# from django.http import FileResponse
# from django.template.loader import render_to_string
from users.serializers import (
    UserSerializer,
    UserDetailSerializer,
    UserClientSerializer,
    UserUpdateSerializer,
)  # OtpVerificationSerializer
from users.models import User
from videos.models import VideoUser
from videos.serializers import VideoUserSerializer

# from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import letter
# import tablib
# from weasyprint import HTML

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from igolohomes.custom_logger import log_message

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
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Creates a new user based on the provided data in the request.",
        request_body=UserSerializer,
        responses={201: UserSerializer, 400: "Validation error"},
    )
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # log-message
            msg = f"[POST] UserList created by user: {request.user.username} with data: {request.data}"
            log_message(module_name=module, message=msg, level="INFO")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        # log-message
        msg = f"[POST] Invalid data send by user: {request.user.username} with data: {request.data}"
        log_message(module_name=module, message=msg, level="WARNING")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
            return Response(serializer.data)
        except NotFound as e:
            # log-message
            msg = (
                f"[GET] UserDetails NotFound, called by user: {request.user.username}."
            )
            log_message(module_name=module, message=msg, level="WARNING")
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # print(str(e))
            # log-message
            msg = f"[GET] UserDetails called by user: {request.user.username}."
            log_message(module_name=module, message=msg, level="ERROR")
            return Response(
                {"error": "Internal Server Error: " + str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

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
            return Response(status=status.HTTP_204_NO_CONTENT)
        except NotFound as e:
            # log-message
            msg = f"[DELETE] UserDetails NotFound, called by user: {request.user.username}."
            log_message(module_name=module, message=msg, level="ERROR")
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied as e:
            # log-message
            msg = f"[DELETE] UserDetails Permissiondenied for user: {request.user.username}."
            log_message(module_name=module, message=msg, level="ERROR")
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            # print(str(e))
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
            username = request.data.get("username")
            password = request.data.get("password")
            user = authenticate(username=username, password=password)

            if user and user.is_superuser:
                refresh = RefreshToken.for_user(user)
                # log-message
                msg = f"[POST] Superuser logged in successfully user: {username}."
                log_message(module_name=module, message=msg, level="INFO")

                return Response(
                    {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                # log-message : warning
                msg = f"[POST] LoginView Invalid credential user: {username}"
                log_message(module_name=module, message=msg, level="WARNING")
                return Response(
                    {"detail": "Invalid credentials"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
        except Exception as e:
            # log-message : error
            msg = f"[POST] LoginView Exception raised,  user: {username}"
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
            username = request.data.get("username")
            password = request.data.get("password")
            user = authenticate(username=username, password=password)

            if user and user.user_type_nn == "client":
                refresh = RefreshToken.for_user(user)
                # log-message : error
                msg = f"[POST] ClientLoginView Client logged in successfully by user: {username}"
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
                msg = f"[POST] ClientLoginView Invalid credential by user: {username}"
                log_message(module_name=module, message=msg, level="WARNING")

                return Response(
                    {"detail": "Invalid credentials"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
        except Exception as e:
            # log-message : error
            msg = f"[POST] ClientLoginView Exception raised by user: {username}"
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
