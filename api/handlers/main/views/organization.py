from typing import Type

from django_filters import rest_framework as filters
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.generics import get_object_or_404
from rest_framework.filters import SearchFilter
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema, no_body

from main import models as main_models
from main.services.labor_estimate import ProjectLaborEstimateService
from api.filters import OrderingFilterNullsLast, ModelMultipleChoiceCommaSeparatedFilter
from api.backends import FilterBackend
from api.views import ReadWriteSerializersMixin, ViewSetFilteredByUserMixin
from api.handlers.main import serializers as main_serializers
from api.handlers.main.views.base import MainBaseViewSet

__all__ = [
    'OrganizationViewSet',
    'OrganizationCustomerViewSet',
    'OrganizationContractorViewSet',
    'OrganizationProjectViewSet',
    'OrganizationProjectCardItemTemplateViewSet',
    'OrganizationProjectCardItemViewSet',
]


class OrganizationViewSet(ViewSetFilteredByUserMixin, MainBaseViewSet):
    class Filter(filters.FilterSet):
        contractor_id = filters.ModelChoiceFilter(queryset=main_models.OrganizationContractor.objects)

    filterset_class = Filter
    queryset = main_models.Organization.objects
    serializer_class = main_serializers.MainOrganizationSerializer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'is_customer',
                openapi.IN_QUERY,
                type=openapi.TYPE_BOOLEAN,
                required=False,
            ),
            openapi.Parameter(
                'is_contractor',
                openapi.IN_QUERY,
                type=openapi.TYPE_BOOLEAN,
                required=False,
            ),
            openapi.Parameter(
                'contractor_id',
                openapi.IN_QUERY,
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_INTEGER),
                required=False,
            ),
            openapi.Parameter(
                'ordering',
                openapi.IN_QUERY,
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_STRING, enum=MainBaseViewSet.ordering_fields),
                default=MainBaseViewSet.ordering
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class OrganizationProjectViewSet(ViewSetFilteredByUserMixin, MainBaseViewSet):
    class Filter(filters.FilterSet):
        organization_customer_id = ModelMultipleChoiceCommaSeparatedFilter(
            queryset=main_models.OrganizationCustomer.objects
        )
        organization_contractor_id = ModelMultipleChoiceCommaSeparatedFilter(
            queryset=main_models.OrganizationContractor.objects,
        )

    filter_class = Filter
    queryset = main_models.OrganizationProject.objects.prefetch_related(
        *main_models.OrganizationProject.objects.get_queryset_prefetch_related()
    )
    serializer_class = main_serializers.OrganizationProjectSerializer
    serializer_read_class = main_serializers.OrganizationProjectReadSerializer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'organization_customer_id',
                openapi.IN_QUERY,
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_INTEGER),
                required=False,
            ),
            openapi.Parameter(
                'organization_contractor_id',
                openapi.IN_QUERY,
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_INTEGER),
                required=False,
            ),
            openapi.Parameter(
                'ordering',
                openapi.IN_QUERY,
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_STRING, enum=MainBaseViewSet.ordering_fields),
                default=MainBaseViewSet.ordering
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: main_serializers.ModulePositionLaborEstimateWorkersAndHoursSerializer(many=True)
        },
        operation_description='Получение сохранённой оценки трудозатрат по всем модулям'
    )
    @action(detail=True, methods=['get'], url_path='get-saved-labor-estimate')
    def get_saved_labor_estimate(self, request, pk, *args, **kwargs):
        return self._get_labor_estimate_response_by_method('get_saved_labor_estimate')

    def _get_labor_estimate_response_by_method(
            self,
            method_name: str,

            serializer_class: Type[main_serializers.ModulePositionLaborEstimateWorkersSerializer]
            = main_serializers.ModulePositionLaborEstimateWorkersAndHoursSerializer,
    ) -> Response:
        service = ProjectLaborEstimateService(self.get_object())
        positions_estimates = getattr(service, method_name)().positions_estimates.values()
        serializer_fields = serializer_class().get_fields().keys()
        serializer = serializer_class(data=[
            {
                **{'position_id': row.position.id},
                **{'position_name': row.position.name},
                **({'hours_count': row.hours_count} if 'hours_count' in serializer_fields else {}),
                **{'workers_count': row.workers_count},
            }
            for row in positions_estimates
        ], many=True)
        return Response(serializer.initial_data, status=status.HTTP_200_OK)


class OrganizationCustomerViewSet(ViewSetFilteredByUserMixin, MainBaseViewSet):
    class Filter(OrganizationViewSet.Filter):
        is_contractor = filters.BooleanFilter()

    filter_class = Filter
    queryset = main_models.OrganizationCustomer.objects
    serializer_class = main_serializers.OrganizationCustomerSerializer
    serializer_read_class = main_serializers.OrganizationCustomerReadSerializer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'contractor_id',
                openapi.IN_QUERY,
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_INTEGER),
                required=False,
            ),
            openapi.Parameter(
                'is_contractor',
                openapi.IN_QUERY,
                type=openapi.TYPE_BOOLEAN,
                required=False,
            ),
            openapi.Parameter(
                'ordering',
                openapi.IN_QUERY,
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_STRING, enum=MainBaseViewSet.ordering_fields),
                default=MainBaseViewSet.ordering
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class OrganizationContractorViewSet(ViewSetFilteredByUserMixin, MainBaseViewSet):
    queryset = main_models.OrganizationContractor.objects
    serializer_class = main_serializers.OrganizationContractorSerializer
    serializer_read_class = main_serializers.OrganizationContractorReadSerializer


class OrganizationProjectCardItemTemplateViewSet(
    ViewSetFilteredByUserMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    http_method_names = ['get']
    queryset = main_models.OrganizationProjectCardItemTemplate.objects.filter(parent__isnull=True)
    serializer_class = main_serializers.OrganizationProjectCardItemTemplateSerializer
    pagination_class = None


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
        organization_customer_id = ModelMultipleChoiceCommaSeparatedFilter(
            queryset=main_models.Organization.objects,
            field_name='organization_project__organization_customer'
        )
        organization_project_id = ModelMultipleChoiceCommaSeparatedFilter(
            queryset=main_models.OrganizationProject.objects
        )

        class Meta:
            model = main_models.OrganizationProjectCardItem
            fields = ['organization_project_id', 'organization_customer_id']

    filterset_class = Filter
    http_method_names = ['get', 'post', 'patch', 'delete']
    queryset = main_models.OrganizationProjectCardItem.objects.prefetch_related(
        'children'
    )
    pagination_class = None
    serializer_class = main_serializers.OrganizationProjectCardItemSerializer
    serializer_read_class = main_serializers.OrganizationProjectCardItemReadTreeSerializer

    def get_queryset(self) -> main_models.OrganizationProjectCardItem.TreeQuerySet:
        queryset = super().get_queryset()
        if self.request.method in SAFE_METHODS:
            return queryset.filter(mptt_level=0)
        return queryset

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'organization_customer_id',
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

    @swagger_auto_schema(
        request_body=no_body,
        responses={
            status.HTTP_201_CREATED: main_serializers.OrganizationProjectCardItemReadTreeSerializer()
        },
    )
    @action(
        detail=False,
        methods=['post'],
        url_path='create-tree-by-template'
                 '/(?P<organization_project_id>[0-9]+)'
                 '/(?P<template_root_card_item_id>[0-9]+)'
    )
    def create_tree_by_template(
            self,
            request,
            organization_project_id: int,
            template_root_card_item_id: int,
            *args,
            **kwargs
    ):
        root_card = main_models.OrganizationProjectCardItem.objects.create_tree_by_template(
            organization_project=get_object_or_404(
                main_models.OrganizationProject.objects.filter_by_user(request.user),
                id=organization_project_id
            ),
            template_root_card_item=get_object_or_404(
                main_models.OrganizationProjectCardItemTemplate.objects.filter_by_user(request.user),
                id=template_root_card_item_id
            ),
        )
        response_serializer = main_serializers.OrganizationProjectCardItemReadTreeSerializer(instance=root_card)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
