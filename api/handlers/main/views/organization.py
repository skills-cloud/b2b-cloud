from django_filters import rest_framework as filters
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from main import models as main_models
from api.views_mixins import ReadWriteSerializersMixin
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
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    http_method_names = MainBaseViewSet.http_method_names

    queryset = main_models.OrganizationProjectCardItem.objects
    serializer_class = main_serializers.OrganizationProjectCardItemTreeSerializer
    serializer_read_class = main_serializers.OrganizationProjectCardItemReadTreeSerializer
