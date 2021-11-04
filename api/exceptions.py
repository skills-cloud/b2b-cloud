import json

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import Http404
from rest_framework import status, exceptions
from rest_framework.renderers import JSONRenderer
from rest_framework.views import exception_handler
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    if settings.DEBUG:
        raise exc
    response = exception_handler(exc, context)
    if not response:
        response = Response()
    response.data = {
        'status': 'error',
        'details': response.data,
    }
    if isinstance(exc, (exceptions.APIException, Http404, PermissionDenied)):
        return response
    details = [what for what in exc.args if what] or str(exc)
    if isinstance(details, (list, tuple)) and len(details) == 1:
        details = details[0]
    try:
        response.data['details'] = json.loads(JSONRenderer().render(details))
        response.status = status.HTTP_400_BAD_REQUEST
        return response
    except Exception:
        raise exc
