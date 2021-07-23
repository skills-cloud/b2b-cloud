from django.conf import settings
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

SchemaViewBase = get_schema_view(
    openapi.Info(
        title="B2B-CLOUD API",
        default_version='v1',
    ),
    public=True,
    url=settings.BASE_URL,
)


class SchemaView(SchemaViewBase):
    pass
