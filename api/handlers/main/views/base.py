import itertools

from rest_framework.filters import SearchFilter
from rest_framework.viewsets import ModelViewSet
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from api.views import ReadWriteSerializersMixin
from api.backends import FilterBackend
from api.filters import OrderingFilterNullsLast

__all__ = [
    'MainBaseViewSet',
]


class MainBaseViewSet(ReadWriteSerializersMixin, ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [FilterBackend, OrderingFilterNullsLast, SearchFilter]
    search_fields = ['name']
    ordering_fields = list(itertools.chain(*[
        [k, f'-{k}']
        for k in ['id', 'name']
    ]))
    ordering = ['name']

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'ordering',
                openapi.IN_QUERY,
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_STRING, enum=ordering_fields),
                default=ordering
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
