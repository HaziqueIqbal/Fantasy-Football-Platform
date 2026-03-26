import logging

from rest_framework.response import Response

logger = logging.getLogger(__name__)


def format_response(data, message, status_code, success=True):
    """
    Return a consistent JSON envelope for all API responses:
    { status_code, message, data, success }
    """
    logger.debug("Formatted response: %s", message)
    return Response(
        data={
            "status_code": status_code,
            "message": message,
            "data": data,
            "success": success,
        },
        status=status_code,
    )
