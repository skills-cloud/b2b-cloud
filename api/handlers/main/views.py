import itertools

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, mixins
from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter

from main import models as main_models
from api.filters import OrderingFilterNullsLast
from api.handlers.main import serializers as main_serializers
from api.handlers.dictionary.views import DictionaryBaseViewSet


class MainBaseViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
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


class OrganizationViewSet(MainBaseViewSet):
    queryset = main_models.Organization.objects
    serializer_class = main_serializers.OrganizationSerializer


class OrganizationProjectViewSet(MainBaseViewSet):
    class Filter(filters.FilterSet):
        organization_id = filters.ModelChoiceFilter(queryset=main_models.Organization.objects)

    filter_class = Filter
    queryset = main_models.OrganizationProject.objects
    serializer_class = main_serializers.OrganizationProjectSerializer
