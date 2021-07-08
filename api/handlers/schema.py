from django.conf import settings
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

__all__ = ['SchemaView']

SchemaViewBase = get_schema_view(
    openapi.Info(
        title="TET-A-TET API",
        default_version='v1',
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    url=settings.BASE_URL,
)


class SchemaView(SchemaViewBase):
    pass
