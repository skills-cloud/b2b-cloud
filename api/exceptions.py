import json

from django.core.exceptions import PermissionDenied
from django.db.models import RestrictedError
from django.http import Http404
from rest_framework import status, exceptions
from rest_framework.renderers import JSONRenderer
from rest_framework.views import exception_handler
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    is_debug_mode = False
    if request := context.get('request', None):
        if '__debug_error__' in request.GET:
            is_debug_mode = True
    if is_debug_mode:
        raise exc
    response = exception_handler(exc, context)
    if not response:
        response = Response(status=status.HTTP_400_BAD_REQUEST)
    response.data = {
        'status': 'error',
        'details': response.data,
    }
    if isinstance(exc, (exceptions.APIException, Http404, PermissionDenied, RestrictedError)):
        if isinstance(exc, PermissionDenied):
            response.status_code = status.HTTP_403_FORBIDDEN
        if isinstance(exc, Http404):
            response.status_code = status.HTTP_404_NOT_FOUND
    details = [what for what in exc.args if what] or str(exc)
    if isinstance(details, (list, tuple)) and len(details) == 1:
        details = details[0]
    try:
        details = json.loads(JSONRenderer().render(details))
    except Exception:
        if isinstance(details, (list, tuple)):
            details = list(map(str, details))
        else:
            details = str(details)
    response.data['details'] = details
    return response
