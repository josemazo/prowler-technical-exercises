import logging
import traceback

from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

# Configure basic logging
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


# This custom exception handler is little and simple, but works perfectly for this exercise
def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        return response

    elif isinstance(exc, IntegrityError):
        response = {
            "error": "Integrity error",
            "detail": str(exc),
        }
        status_code = status.HTTP_409_CONFLICT

    elif isinstance(exc, DjangoValidationError):
        response = {
            "error": "Validation error",
            "detail": str(exc),
        }
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

    elif isinstance(exc, Http404):
        response = {
            "error": "Not found",
            "detail": str(exc),
        }
        status_code = status.HTTP_404_NOT_FOUND

    else:
        exception_traceback = traceback.format_exception(exc)
        logger.error("\n\n" + "".join(exception_traceback))

        response = {
            "error": "Internal server error",
            "detail": "An unexpected error occurred. Please try again later.",
        }
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

        if settings.DEBUG:
            response["exception"] = str(exc)

    return Response(response, status=status_code)
