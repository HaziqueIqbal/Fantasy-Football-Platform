import logging

from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Wrap DRF's default exception handler so every error response uses the
    standard { status_code, message, data, success } envelope.
    """
    response = exception_handler(exc, context)

    if response is not None:
        status_code = response.status_code
        data = response.data

        if isinstance(data, dict):
            detail = data.get("detail", None)
            if detail:
                message = str(detail)
                error_data = None
            else:
                message = "Validation error."
                error_data = data
        elif isinstance(data, list):
            message = "Validation error."
            error_data = data
        else:
            message = str(data)
            error_data = None

        logger.warning(
            "API error %s: %s | path: %s",
            status_code,
            message,
            context.get("request", {}).path if hasattr(context.get("request", {}), "path") else "",
        )

        response.data = {
            "status_code": status_code,
            "message": message,
            "data": error_data,
            "success": False,
        }

    return response
