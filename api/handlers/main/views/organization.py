from django_filters import rest_framework as filters
from rest_framework import mixins
from rest_framework.permissions import SAFE_METHODS
from rest_framework.viewsets import GenericViewSet
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from api.filters import ModelMultipleChoiceCommaSeparatedFilter
from main import models as main_models
from api.views_mixins import ReadWriteSerializersMixin, ViewSetFilteredByUserMixin
from api.handlers.main import serializers as main_serializers
from api.handlers.main.views.base import MainBaseViewSet

__all__ = [
    'OrganizationViewSet',
    'OrganizationProjectViewSet',
    'OrganizationProjectCardItemViewSet',
]


class OrganizationViewSet(MainBaseViewSet):
    queryset = main_models.Organization.objects
    serializer_class = main_serializers.OrganizationSerializer
    filterset_fields = ['is_customer']


class OrganizationProjectViewSet(MainBaseViewSet):
    class Filter(filters.FilterSet):
        organization_id = filters.ModelChoiceFilter(queryset=main_models.Organization.objects)

    filter_class = Filter
    queryset = main_models.OrganizationProject.objects.prefetch_related(
        *main_models.OrganizationProject.objects.get_queryset_prefetch_related()
    )
    serializer_class = main_serializers.OrganizationProjectSerializer
    serializer_read_class = main_serializers.OrganizationProjectReadSerializer


class OrganizationProjectCardItemViewSet(
    ReadWriteSerializersMixin,
    ViewSetFilteredByUserMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    class Filter(filters.FilterSet):
        organization_id = ModelMultipleChoiceCommaSeparatedFilter(
            queryset=main_models.Organization.objects,
            field_name='organization_project__organization'
        )
        organization_project_id = ModelMultipleChoiceCommaSeparatedFilter(
            queryset=main_models.OrganizationProject.objects
        )

        class Meta:
            model = main_models.OrganizationProjectCardItem
            fields = ['organization_project_id', 'organization_id']

    filterset_class = Filter
    http_method_names = ['get', 'post', 'patch', 'delete']
    queryset = main_models.OrganizationProjectCardItem.objects.prefetch_related(
        'children'
    )
    pagination_class = None
    serializer_class = main_serializers.OrganizationProjectCardItemTreeSerializer
    serializer_read_class = main_serializers.OrganizationProjectCardItemReadTreeSerializer

    def get_queryset(self) -> main_models.OrganizationProjectCardItem.TreeQuerySet:
        queryset = super().get_queryset()
        if self.request.method in SAFE_METHODS:
            return queryset.filter(mptt_level=0)
        return queryset

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'organization_id',
                openapi.IN_QUERY,
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_INTEGER),
                description='`ANY`',
                required=False,
            ),
            openapi.Parameter(
                'organization_project_id',
                openapi.IN_QUERY,
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_INTEGER),
                description='`ANY`',
                required=False,
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
