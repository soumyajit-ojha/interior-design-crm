# response_utils.py

from rest_framework.response import Response
from rest_framework import status

def response_success(data=None, message="Request was successful", status_code=status.HTTP_200_OK):
    """
    Standard response for successful requests.

    :param data: The data to include in the response body.
    :param message: The success message to include in the response body.
    :param status_code: The HTTP status code for the response.
    :return: A DRF Response object.
    """
    return Response({
        "success": True,
        "message": message,
        "data": data
    }, status=status_code)

def response_created(data=None, message="Resource created successfully"):
    """
    Standard response for resource creation.

    :param data: The data to include in the response body.
    :param message: The success message to include in the response body.
    :return: A DRF Response object.
    """
    return response_success(data, message, status.HTTP_201_CREATED)

def response_bad_request(errors, message="Bad request"):
    """
    Standard response for bad requests.

    :param errors: The errors to include in the response body.
    :param message: The error message to include in the response body.
    :return: A DRF Response object.
    """
    return Response({
        "success": False,
        "message": message,
        "errors": errors
    }, status=status.HTTP_400_BAD_REQUEST)

def response_unauthorized(message="Unauthorized"):
    """
    Standard response for unauthorized requests.

    :param message: The error message to include in the response body.
    :return: A DRF Response object.
    """
    return Response({
        "success": False,
        "message": message
    }, status=status.HTTP_401_UNAUTHORIZED)

def response_forbidden(message="Forbidden"):
    """
    Standard response for forbidden requests.

    :param message: The error message to include in the response body.
    :return: A DRF Response object.
    """
    return Response({
        "success": False,
        "message": message
    }, status=status.HTTP_403_FORBIDDEN)

def response_not_found(message="Not found"):
    """
    Standard response for resource not found.

    :param message: The error message to include in the response body.
    :return: A DRF Response object.
    """
    return Response({
        "success": False,
        "message": message
    }, status=status.HTTP_404_NOT_FOUND)

def response_conflict(errors, message="Conflict"):
    """
    Standard response for conflict requests.

    :param errors: The errors to include in the response body.
    :param message: The error message to include in the response body.
    :return: A DRF Response object.
    """
    return Response({
        "success": False,
        "message": message,
        "errors": errors
    }, status=status.HTTP_409_CONFLICT)

def response_server_error(message="Internal server error"):
    """
    Standard response for server errors.

    :param message: The error message to include in the response body.
    :return: A DRF Response object.
    """
    return Response({
        "success": False,
        "message": message
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

