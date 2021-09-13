from __future__ import unicode_literals

from django.conf import settings
from django.core.exceptions import PermissionDenied, ValidationError as ValidationErrorDjango
from django.http import Http404
from rest_framework import status, exceptions
from rest_framework.views import exception_handler
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if not response:
        response = Response()
    response.data = {
        'status': 'error',
        'details': response.data,
    }
    if isinstance(exc, exceptions.APIException):
        return response
    details = [what for what in exc.args if what] or str(exc)
    if len(details) == 1:
        details = details[0]
    elif isinstance(exc, Http404):
        response.data['details'] = details
        response.status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, PermissionDenied):
        response.data['details'] = details
        response.status_code = status.HTTP_403_FORBIDDEN
    if isinstance(exc, ValidationErrorDjango):
        response.data['details'] = exc.args[0]
        response.status = status.HTTP_400_BAD_REQUEST
    elif isinstance(exc, Exception):
        if settings.DEBUG:
            raise exc
        response.data['details'] = str(details)
        response.status_code = status.HTTP_400_BAD_REQUEST
    return response

