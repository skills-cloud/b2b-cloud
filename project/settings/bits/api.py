from drf_yasg.app_settings import SWAGGER_DEFAULTS

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'api.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'api.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'api.backends.FilterBackend',
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
    'DISPLAY_OPERATION_ID': False,
    'DEFAULT_PAGINATOR_INSPECTORS': [
        'api.schema.inspectors.query.DefaultPaginationRestResponsePagination',
        * SWAGGER_DEFAULTS['DEFAULT_PAGINATOR_INSPECTORS'],
    ],
    'DEFAULT_FIELD_INSPECTORS': [
        'api.schema.inspectors.field.PrimaryKeyRelatedFieldInspector',
        'api.schema.inspectors.field.ChoiceFieldInspector',
        *[
            f
            for f in SWAGGER_DEFAULTS['DEFAULT_FIELD_INSPECTORS']
            if f not in [
                'drf_yasg.inspectors.ChoiceFieldInspector',
            ]
        ],
    ]
}
