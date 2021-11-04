import itertools

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.filters import SearchFilter
from rest_framework.viewsets import ModelViewSet
from django_filters import rest_framework as filters

from acc.models import User
from main import models as main_models
from api.views_mixins import ViewSetFilteredByUserMixin, ReadWriteSerializersMixin, ViewSetQuerySetPrefetchRelatedMixin
from api.backends import FilterBackend
from api.filters import OrderingFilterNullsLast, ModelMultipleChoiceCommaSeparatedFilter
from api.handlers.main import serializers as main_serializers

__all__ = [
    'FunPointTypeDifficultyLevelViewSet',
    'FunPointTypePositionLaborEstimateViewSet',
    'FunPointTypeViewSet',
    'ModuleViewSet',
    'ModuleFunPointViewSet',
    'ModulePositionLaborEstimateViewSet',
]


class FunPointTypeDifficultyLevelViewSet(ViewSetFilteredByUserMixin, ModelViewSet):
    http_method_names = ['post', 'patch', 'delete']
    queryset = main_models.FunPointTypeDifficultyLevel.objects
    serializer_class = main_serializers.FunPointTypeDifficultyLevelWriteSerializer


class FunPointTypePositionLaborEstimateViewSet(ViewSetFilteredByUserMixin, ModelViewSet):
    http_method_names = ['post', 'patch', 'delete']
    queryset = main_models.FunPointTypePositionLaborEstimate.objects
    serializer_class = main_serializers.FunPointTypePositionLaborEstimateWriteSerializer


class FunPointTypeViewSet(
    ViewSetQuerySetPrefetchRelatedMixin,
    ReadWriteSerializersMixin,
    ViewSetFilteredByUserMixin,
    ModelViewSet
):
    http_method_names = ['get', 'post', 'patch', 'delete']
    queryset = main_models.FunPointType.objects
    serializer_class = main_serializers.FunPointTypeWriteSerializer
    serializer_read_class = main_serializers.FunPointTypeReadSerializer


class ModuleViewSet(
    ViewSetQuerySetPrefetchRelatedMixin,
    ReadWriteSerializersMixin,
    ViewSetFilteredByUserMixin,
    ModelViewSet
):
    class Filter(filters.FilterSet):
        organization_id = ModelMultipleChoiceCommaSeparatedFilter(
            queryset=main_models.Organization.objects,
            field_name='organization_project__organization',
        )
        organization_project_id = ModelMultipleChoiceCommaSeparatedFilter(
            queryset=main_models.OrganizationProject.objects,
            field_name='organization_project',
        )
        manager_id = ModelMultipleChoiceCommaSeparatedFilter(queryset=User.objects)

    http_method_names = ['get', 'post', 'patch', 'delete']
    queryset = main_models.Module.objects
    serializer_class = main_serializers.ModuleWriteSerializer
    serializer_read_class = main_serializers.ModuleReadSerializer
    filter_backends = [FilterBackend, OrderingFilterNullsLast, SearchFilter]
    filterset_class = Filter
    search_fields = ['id', 'name', 'description']
    ordering_fields = list(itertools.chain(*[
        [k, f'-{k}']
        for k in ['id', 'name', 'start_date', 'deadline_date', 'sorting']
    ]))
    ordering = ['sorting']

    @swagger_auto_schema(
        manual_parameters=[

            openapi.Parameter(
                'organization_id',
                openapi.IN_QUERY,
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_INTEGER),
                required=False,
            ),
            openapi.Parameter(
                'organization_project_id',
                openapi.IN_QUERY,
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_INTEGER),
                required=False,
            ),
            openapi.Parameter(
                'manager_id',
                openapi.IN_QUERY,
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_INTEGER),
                required=False,
            ),
            openapi.Parameter(
                'ordering',
                openapi.IN_QUERY,
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_STRING, enum=ordering_fields),
                default=ordering,
                required=False,
            ),
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=False,
                description='Search in: `[%s]`' % ', '.join(search_fields)
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ModuleFunPointViewSet(ViewSetFilteredByUserMixin, ModelViewSet):
    http_method_names = ['post', 'patch', 'delete']
    queryset = main_models.ModuleFunPoint.objects
    serializer_class = main_serializers.ModuleFunPointWriteSerializer


class ModulePositionLaborEstimateViewSet(ViewSetFilteredByUserMixin, ModelViewSet):
    http_method_names = ['post', 'patch', 'delete']
    queryset = main_models.ModulePositionLaborEstimate.objects
    serializer_class = main_serializers.ModulePositionLaborEstimateWriteSerializer
