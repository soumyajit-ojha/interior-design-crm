"""
This file contains all view functions for the videos app.

All views use Django's API views as a base and handle GET,POST,GET and DELETE requests.

Requires authentication for all views.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from videos.models import VideoUser
from videos.serializers import VideoUserSerializer
from igolohomes.custom_logger import log_message

module = str((__name__).split(".")[0])


class VideoUserList(APIView):
    """
    Retrieve details of a specific Model instance.

    Accepts GET and POST requests.

    Args:
        pk (int): Primary key of the Model instance to retrieve.

    Returns:
        JSON response with serialized Model data.

    Raises:
        Http 201 and 400 : If the requested Model instance is created and
        has a bad request respectively.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """
        Retrieves a list of VideoUser instances associated with a specific user.

        Accepts GET requests.

        Args:
            pk (int): Primary key of the user whose VideoUser instances to retrieve.

        Returns:
            JSON response with a serialized list of VideoUser instances.

        Raises:
            Http404: If the specified user is not found.
        """
        try:
            video_users = VideoUser.objects.filter(user_fk=pk)
            serializer = VideoUserSerializer(video_users, many=True)
            # log-message
            msg = f"[GET] VideoUserList called by user: {request.user.username}"
            log_message(module_name=module, message=msg, level="INFO")
            return Response(serializer.data)
        except Exception as e:
            # log-message
            msg = f"[GET] VideoUserList called by user: {request.user.username}"
            log_message(module_name=module, message=msg, level="ERROR")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        """
        Creates a new VideoUser instance based on provided data.

        Accepts POST requests with JSON data containing VideoUser information.

        Requires the following fields in the request body:

            - user_id (int): Primary key of the user associated with the VideoUser.
        Returns:
            - JSON response with serialized data of the newly created VideoUser
            instance on success (status code 201 Created).
            - JSON response with error details on failure (status code 400 Bad Request).
        Raises:
            - PermissionError: If the user is not authenticated or lacks
            permission to create VideoUser instances.
        """
        try:
            serializer = VideoUserSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                # log-message
                msg = f"[POST] VideoUserList called by user: {request.user.username}"
                log_message(module_name=module, message=msg, level="INFO")
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            # log-message
            msg = f"[POST] VideoUserList called by user: {request.user.username}"
            log_message(module_name=module, message=msg, level="WARNING")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # log-message
            msg = f"[POST] VideoUserList called by user: {request.user.username}"
            log_message(module_name=module, message=msg, level="ERROR")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VideoUserDetail(APIView):
    """
    Retrieve details of a specific Model instance.

    Accepts GET,PUT and DELETE requests.

    Args:
        pk (int): Primary key of the Model instance to retrieve.

    Returns:
        JSON response with serialized Model data.

    Raises:
        Http 204 and 400 : If the requested Model instance if deleted and if not found respectively.
    """

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        """
        Retrieves a single VideoUser instance by its primary key.
        Args:
        pk (int): Primary key of the VideoUser instance to retrieve.
        Returns:
        VideoUser instance: The retrieved VideoUser object, or None if not found.
        """
        return VideoUser.objects.filter(pk=pk).first()

    def get(self, request, pk):
        """
        Retrieves a list of VideoUser instances associated with a specific user.

        Accepts GET requests.

        Args:
            pk (int): Primary key of the user whose VideoUser instances to retrieve.

        Returns:
            JSON response with a serialized list of VideoUser instances.
        """
        try:
            video_users = VideoUser.objects.filter(pk=pk).first()
            if video_users is None:
                # log-message
                msg = f"[GET] VideoUserDetail called by user: {request.user.username} user not found."
                log_message(module_name="users", message=msg, level="WARNING")
                return Response(
                    {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
                )

            serializer = VideoUserSerializer(video_users)
            # log-message
            msg = f"[GET] VideoUserDetail called by user: {request.user.username}"
            log_message(module_name=module, message=msg, level="INFO")
            return Response(serializer.data)
        except Exception as e:
            # log-message
            msg = f"[GET] VideoUserDetail called by user: {request.user.username}"
            log_message(module_name=module, message=msg, level="ERROR")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request, pk):
        """
        Updates a specific VideoUser instance with provided data.
        Accepts PUT requests with JSON data containing updated VideoUser information.
        Args:
        pk (int): Primary key of the VideoUser instance to update.
        Returns:
        - JSON response with serialized data of the updated VideoUser instance on
        success (status code 200 OK).
        - JSON response with error details on failure (status code 400 Bad Request).
        Raises:
        - Http404: If the specified VideoUser instance is not found.
        """
        try:
            video_user = self.get_object(pk)
            serializer = VideoUserSerializer(video_user, data=request.data)
            if serializer.is_valid():
                serializer.save()
                # log-message
                msg = f"[PUT] VideoUserDetail called by user: {request.user.username}"
                log_message(module_name=module, message=msg, level="INFO")
                return Response(serializer.data)

            # log-message
            msg = f"[PUT] VideoUserDetail called by user: {request.user.username}"
            log_message(module_name=module, message=msg, level="WARNING")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # log-message
            msg = f"[PUT] VideoUserDetail called by user: {request.user.username}"
            log_message(module_name=module, message=msg, level="ERROR")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, pk):
        """
        Deletes a specific VideoUser instance.
        Accepts DELETE requests.
        Args:
        pk (int): Primary key of the VideoUser instance to delete.
        Returns:
        - JSON response with an "error" message and status code 404
        Not Found if the VideoUser instance is not found.
        - Empty JSON response with status code 204 No Content on successful deletion.
        """
        try:
            video_user = self.get_object(pk)
            if video_user is None:
                # log-message
                msg = f"[DELETE] VideoUserDetail called by user: {request.user.username} 'VideoUser not found."
                log_message(module_name=module, message=msg, level="WARNING")
                return Response(
                    {"error": "Video user not found"}, status=status.HTTP_404_NOT_FOUND
                )

            video_user.delete()
            # log-message
            msg = f"[DELETE] VideoUserDetail called by user: {request.user.username}. VideoUser deleted."
            log_message(module_name=module, message=msg, level="INFO")
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            # log-message
            msg = f"[DELETE] VideoUserDetail called by user: {request.user.username}."
            log_message(module_name=module, message=msg, level="ERROR")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserVideos(APIView):
    """
    Retrieve details of a specific Model instance.

    Accepts GET  requests.

    Returns:
        JSON response with serialized Model data.
    """

    def get(self, request):
        """
        Retrieves a list of VideoUser instances associated with a specific user.

        Accepts GET requests.

        Returns:
            JSON response with a serialized list of VideoUser instances.
        """
        try:
            video_users = VideoUser.objects.filter(user_fk=request.user)
            if not video_users.exists():
                # log-message
                msg = f"[GET] VideoUserDetail called User does not exist."
                log_message(module_name=module, message=msg, level="WARNING")
                return Response(
                    {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
                )

            serializer = VideoUserSerializer(video_users, many=True)
            # log-messages
            msg = f"[GET] VideoUserDetail called by user: {request.user.username}."
            log_message(module_name=module, message=msg, level="INFO")
            return Response(
                serializer.data,
                status=(
                    status.HTTP_200_OK if video_users else status.HTTP_204_NO_CONTENT
                ),
            )
        except Exception as e:
            # log-messages
            msg = f"[GET] VideoUserDetail called and Exception Raised."
            log_message(module_name=module, message=msg, level="ERROR")
            return Response(
                {"error": "Internal Server Error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
