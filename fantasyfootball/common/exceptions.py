from rest_framework.exceptions import APIException
from rest_framework import status


class AuthenticationFailedException(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Authentication failed."
    default_code = "authentication_failed"


class PermissionDeniedException(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "You do not have permission to perform this action."
    default_code = "permission_denied"


class ResourceNotFoundException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "The requested resource was not found."
    default_code = "not_found"


class BadRequestException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Invalid request."
    default_code = "bad_request"


class ConflictException(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Conflict with current state."
    default_code = "conflict"
