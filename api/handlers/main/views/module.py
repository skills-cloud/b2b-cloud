import itertools
from typing import Type

from django.db import transaction
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema, no_body
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django_filters import rest_framework as filters

from acc.models import User
from main import models as main_models
from main.services.organization_project.module import ModuleLaborEstimateService
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
    filter_backends = [SearchFilter]
    search_fields = ['name']


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
    filter_backends = [SearchFilter]
    search_fields = ['name']


class ModuleViewSet(
    ViewSetQuerySetPrefetchRelatedMixin,
    ReadWriteSerializersMixin,
    ViewSetFilteredByUserMixin,
    ModelViewSet
):
    class Filter(filters.FilterSet):
        organization_customer_id = ModelMultipleChoiceCommaSeparatedFilter(
            queryset=main_models.Organization.objects,
            field_name='organization_project__organization_customer',
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
                'organization_customer_id',
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

    @swagger_auto_schema(
        request_body=no_body,
        responses={
            status.HTTP_201_CREATED: main_serializers.RequestSerializer(),
            status.HTTP_204_NO_CONTENT: '',
        },
        operation_description='Возвращает'
                              '<br> * `201` если запрос создан'
                              '<br> * `204` если запрос не создан – потому, что не было такой необходимости'
    )
    @action(detail=True, methods=['post'], url_path='create-request-for-saved-labor-estimate')
    @transaction.atomic
    def create_request_for_saved_labor_estimate(self, request, pk, *args, **kwargs):
        service = ModuleLaborEstimateService(self.get_object())
        result = service.create_request_for_saved_labor_estimate()
        if not result:
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = main_serializers.RequestSerializer(instance=result)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: main_serializers.ModulePositionLaborEstimateWorkersAndHoursSerializer(many=True)
        },
        operation_description='Получение расчётной оценки трудозатрат на основе ф-х точек'
    )
    @action(detail=True, methods=['get'], url_path='get-expected-labor-estimate')
    def get_expected_labor_estimate(self, request, pk, *args, **kwargs):
        return self._get_labor_estimate_response_by_method('get_expected_labor_estimate')

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: main_serializers.ModulePositionLaborEstimateWorkersAndHoursSerializer(many=True)
        },
        operation_description='Получение разницы расчётной и сохранённой оценок трудозатрат'
                              '<br>`расчётная - сохранённая`'
                              '<br><i>т.е. если цифры минусовые – в сохранённой больше, чем в расчётной</i>'
    )
    @action(detail=True, methods=['get'], url_path='get-expected-minus-saved-labor-estimate')
    def get_expected_minus_saved_labor_estimate(self, request, pk, *args, **kwargs):
        return self._get_labor_estimate_response_by_method('get_expected_minus_saved_labor_estimate')

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: main_serializers.ModulePositionLaborEstimateWorkersSerializer(many=True)
        },
        operation_description='Получение разницы сохранённой и запрошенной оценок трудозатрат'
                              '<br>`сохранённая – запрошенная`'
                              '<br><i>т.е. если цифры минусовые – в запрошенной больше, чем в сохранённая</i>'
    )
    @action(detail=True, methods=['get'], url_path='get-saved-minus-requested-labor-estimate')
    def get_saved_minus_requested_labor_estimate(self, request, pk, *args, **kwargs):
        return self._get_labor_estimate_response_by_method(
            'get_saved_minus_requested_labor_estimate',
            serializer_class=main_serializers.ModulePositionLaborEstimateWorkersSerializer
        )

    @swagger_auto_schema(
        request_body=no_body,
        responses={
            status.HTTP_200_OK: '',
            status.HTTP_204_NO_CONTENT: '',
        },
        operation_description='Возвращает'
                              '<br> * `200` если что-то поменялось'
                              '<br> * `204` если ничего не поменялось'
    )
    @action(detail=True, methods=['post'], url_path='set-expected-labor-estimate-as-saved')
    @transaction.atomic
    def set_expected_labor_estimate_as_saved(self, request, pk, *args, **kwargs):
        service = ModuleLaborEstimateService(self.get_object())
        if not service.set_expected_labor_estimate_as_saved():
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_200_OK)

    def _get_labor_estimate_response_by_method(
            self,
            method_name: str,

            serializer_class: Type[main_serializers.ModulePositionLaborEstimateWorkersSerializer]
            = main_serializers.ModulePositionLaborEstimateWorkersAndHoursSerializer,
    ) -> Response:
        service = ModuleLaborEstimateService(self.get_object())
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


class ModuleFunPointViewSet(ViewSetFilteredByUserMixin, ModelViewSet):
    http_method_names = ['post', 'patch', 'delete']
    queryset = main_models.ModuleFunPoint.objects
    serializer_class = main_serializers.ModuleFunPointWriteSerializer
    filter_backends = [SearchFilter]
    search_fields = ['name']


class ModulePositionLaborEstimateViewSet(ViewSetFilteredByUserMixin, ModelViewSet):
    http_method_names = ['post', 'patch', 'delete']
    queryset = main_models.ModulePositionLaborEstimate.objects
    serializer_class = main_serializers.ModulePositionLaborEstimateWriteSerializer
