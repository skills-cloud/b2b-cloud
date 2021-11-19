from django.conf import settings
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from api.permissions import IsAuthenticatedOrReadOnly

SchemaViewBase = get_schema_view(
    openapi.Info(
        title="B2B-Cloud API",
        default_version='v1',
    ),
    public=True,
    url=settings.BASE_URL,
    permission_classes=(IsAuthenticatedOrReadOnly,),
)


class SchemaView(SchemaViewBase):
    pass
