import itertools

from rest_framework.filters import SearchFilter
from rest_framework.viewsets import ModelViewSet
from django_filters import rest_framework as filters
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from main import models as main_models
from api.views_mixins import ReadWriteSerializersMixin
from api.filters import OrderingFilterNullsLast
from api.handlers.main import serializers as main_serializers

__all__ = [
    'MainBaseViewSet',
    'ProjectViewSet',
]


class MainBaseViewSet(ReadWriteSerializersMixin, ModelViewSet):
    http_method_names = ['get', 'post', 'patch']
    filter_backends = [filters.DjangoFilterBackend, OrderingFilterNullsLast, SearchFilter]
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


class ProjectViewSet(MainBaseViewSet):
    queryset = main_models.Project.objects.prefetch_related(
        *main_models.Project.objects.get_queryset_prefetch_related()
    )
    serializer_class = main_serializers.ProjectSerializer
    serializer_read_class = main_serializers.ProjectReadSerializer
