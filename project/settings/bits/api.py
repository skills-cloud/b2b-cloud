REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'api.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'api.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_PAGINATION_CLASS': 'api.pagination.DefaultPagination',
    'DEFAULT_RENDERER_CLASSES': (
        'drf_ujson.renderers.UJSONRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'drf_ujson.parsers.UJSONParser',
    ),
    'EXCEPTION_HANDLER': 'api.exceptions.custom_exception_handler',
}

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': [],
    'USE_SESSION_AUTH': True,
    'REFETCH_SCHEMA_WITH_AUTH': True,
}
