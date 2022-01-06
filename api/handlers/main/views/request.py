import json
import itertools
from typing import Dict

from django.db import transaction
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status, serializers
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters import rest_framework as filters
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from acc.models import User
from dictionary import models as dictionary_models
from cv import models as cv_models
from main import models as main_models
from api.backends import FilterBackend
from api.views_mixins import ReadWriteSerializersMixin, ReadCreateUpdateSerializersMixin, ViewSetFilteredByUserMixin
from api.filters import OrderingFilterNullsLast, ModelMultipleChoiceCommaSeparatedFilter
from api.handlers.main import serializers as main_serializers
from api.handlers.main.views.base import MainBaseViewSet

__all__ = [
    'RequestTypeViewSet',
    'RequestViewSet',
    'RequestRequirementViewSet',
    'TimeSheetRowViewSet',
]


class RequestTypeViewSet(MainBaseViewSet):
    queryset = main_models.RequestType.objects
    serializer_class = main_serializers.RequestTypeSerializer


class RequestViewSet(ReadWriteSerializersMixin, ViewSetFilteredByUserMixin, ModelViewSet):
    class Filter(filters.FilterSet):
        organization_customer_id = ModelMultipleChoiceCommaSeparatedFilter(
            queryset=main_models.Organization.objects,
            field_name='module__organization_project__organization_customer',
        )
        organization_project_id = ModelMultipleChoiceCommaSeparatedFilter(
            queryset=main_models.OrganizationProject.objects,
            field_name='module__organization_project',
        )
        module_id = ModelMultipleChoiceCommaSeparatedFilter(queryset=main_models.Module.objects)
        type_id = ModelMultipleChoiceCommaSeparatedFilter(queryset=main_models.RequestType.objects)
        industry_sector_id = ModelMultipleChoiceCommaSeparatedFilter(queryset=dictionary_models.IndustrySector.objects)
        resource_manager_id = ModelMultipleChoiceCommaSeparatedFilter(queryset=User.objects)
        recruiter_id = ModelMultipleChoiceCommaSeparatedFilter(queryset=User.objects)
        manager_id = ModelMultipleChoiceCommaSeparatedFilter(queryset=User.objects)

        class Meta:
            model = main_models.Request
            fields = [
                'status', 'priority',
            ]

    http_method_names = ['get', 'post', 'patch', 'delete']
    queryset = main_models.Request.objects.prefetch_related(
        *main_models.Request.objects.get_queryset_prefetch_related()
    )
    serializer_class = main_serializers.RequestSerializer
    serializer_read_class = main_serializers.RequestReadSerializer
    filter_backends = [FilterBackend, OrderingFilterNullsLast, SearchFilter]
    filterset_class = Filter
    search_fields = ['id', 'title', 'description']
    ordering_fields = list(itertools.chain(*[
        [k, f'-{k}']
        for k in ['id', 'type', 'title', 'priority', 'start_date', 'deadline_date']
    ]))
    ordering = ['priority', '-id']

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
                'module_id',
                openapi.IN_QUERY,
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_INTEGER),
                required=False,
            ),
            openapi.Parameter(
                'type_id',
                openapi.IN_QUERY,
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_INTEGER),
                required=False,
            ),
            openapi.Parameter(
                'industry_sector_id',
                openapi.IN_QUERY,
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_INTEGER),
                required=False,
            ),
            openapi.Parameter(
                'resource_manager_id',
                openapi.IN_QUERY,
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_INTEGER),
                required=False,
            ),
            openapi.Parameter(
                'recruiter_id',
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
                'status',
                openapi.IN_QUERY,
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_STRING, enum=main_models.RequestStatus.values),
                required=False,
            ),
            openapi.Parameter(
                'priority',
                openapi.IN_QUERY,
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_INTEGER, enum=main_models.RequestPriority.values),
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


class RequestRequirementViewSet(ReadWriteSerializersMixin, ViewSetFilteredByUserMixin, ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    queryset = main_models.RequestRequirement.objects.prefetch_related(
        *main_models.RequestRequirement.objects.get_queryset_prefetch_related()
    )
    serializer_class = main_serializers.RequestRequirementSerializer
    serializer_read_class = main_serializers.RequestRequirementReadSerializer

    @swagger_auto_schema(
        request_body=main_serializers.RequestRequirementCvWriteDetailsSerializer(),
        responses={
            status.HTTP_200_OK: main_serializers.RequestRequirementCvSerializer()
        },
    )
    @action(detail=True, methods=['post'], url_path='cv-link/(?P<cv_id>[0-9]+)')
    @transaction.atomic
    def cv_link(self, request, pk: int, cv_id: int, *args, **kwargs):
        instance = main_models.RequestRequirementCv(
            request_requirement=self.get_object(),
            cv=get_object_or_404(cv_models.CV.objects.filter_by_user(request.user), id=cv_id),
        )
        instance = self._save_cv_linked(instance, request.data)
        instance.save()
        return Response(
            main_serializers.RequestRequirementCvSerializer(instance=instance).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['delete'], url_path='cv-unlink/(?P<cv_id>[0-9]+)')
    @transaction.atomic
    def cv_unlink(self, request, pk: int, cv_id: int, *args, **kwargs):
        self._get_cv_linked_or_404(request, cv_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        request_body=main_serializers.RequestRequirementCvWriteDetailsSerializer(),
        responses={
            status.HTTP_200_OK: main_serializers.RequestRequirementCvSerializer()
        },
    )
    @action(detail=True, methods=['post'], url_path='cv-set-details/(?P<cv_id>[0-9]+)')
    @transaction.atomic
    def cv_set_details(self, request, pk: int, cv_id: int, *args, **kwargs):
        instance = self._save_cv_linked(self._get_cv_linked_or_404(request, cv_id), request.data)
        return Response(
            main_serializers.RequestRequirementCvSerializer(instance=instance).data,
            status=status.HTTP_200_OK
        )

    @swagger_auto_schema(
        request_body=main_serializers.RequestRequirementCompetenceReplaceSerializer(many=True),
        responses={
            status.HTTP_201_CREATED: main_serializers.RequestRequirementCompetenceSerializer(many=True)
        },
    )
    @action(detail=True, methods=['post'], url_path='competencies-set')
    @transaction.atomic
    def competencies_set(self, request, pk: int, *args, **kwargs):
        request_serializer = main_serializers.RequestRequirementCompetenceReplaceSerializer(data=request.data,
                                                                                            many=True)
        request_serializer.is_valid(raise_exception=True)
        response_serializer = main_serializers.RequestRequirementCompetenceSerializer(
            main_models.RequestRequirementCompetence.objects.set_for_request_requirement(
                self.get_object(),
                request_serializer.to_internal_value(request_serializer.data)
            ),
            many=True
        )
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def _save_cv_linked(
            self,
            instance: main_models.RequestRequirementCv,
            request_data: Dict
    ) -> main_models.RequestRequirementCv:
        serializer = main_serializers.RequestRequirementCvWriteDetailsSerializer(
            data=request_data,
            instance=instance
        )
        serializer.is_valid(raise_exception=True)
        details = serializer.validated_data
        cards_items = details.pop('organization_project_card_items', None)
        for k, v in details.items():
            setattr(instance, k, v)
        if cards_items:
            if not instance.attributes:
                instance.attributes = {}
            instance.attributes['organization_project_card_items'] = json.loads(json.dumps(cards_items, default=str))
        try:
            instance.save()
        except DjangoValidationError as e:
            raise ValidationError(e.args[0])
        return instance

    def _get_cv_linked_or_404(self, request, cv_id: int) -> main_models.RequestRequirementCv:
        return get_object_or_404(main_models.RequestRequirementCv.objects.filter(
            request_requirement=self.get_object(),
            cv_id=cv_id,
        ))


class TimeSheetRowViewSet(ReadCreateUpdateSerializersMixin, ViewSetFilteredByUserMixin, ModelViewSet):
    class Filter(filters.FilterSet):
        task_name = filters.CharFilter()
        cv_id = ModelMultipleChoiceCommaSeparatedFilter(
            queryset=cv_models.CV.objects,
        )
        request_id = ModelMultipleChoiceCommaSeparatedFilter(
            queryset=main_models.Request.objects,
            field_name='request',
        )
        module_id = ModelMultipleChoiceCommaSeparatedFilter(
            queryset=main_models.Module.objects,
            field_name='request__module',
        )
        organization_project_id = ModelMultipleChoiceCommaSeparatedFilter(
            queryset=main_models.OrganizationProject.objects,
            field_name='request__module__organization_project',
        )
        organization_customer_id = ModelMultipleChoiceCommaSeparatedFilter(
            queryset=main_models.Organization.objects,
            field_name='request__module__organization_project__organization_customer',
        )

        class Meta:
            model = main_models.TimeSheetRow
            fields = [
                'cv_id', 'request_id', 'module_id', 'organization_project_id', 'organization_customer_id',
            ]

        def get_schema_fields(self):
            return []

    filterset_class = Filter
    filter_backends = [FilterBackend, OrderingFilterNullsLast, SearchFilter]
    http_method_names = ['get', 'post', 'patch', 'delete']
    queryset = main_models.TimeSheetRow.objects.prefetch_related(
        *main_models.TimeSheetRow.objects.get_queryset_prefetch_related()
    )

    serializer_read_class = main_serializers.TimeSheetRowReadSerializer
    serializer_create_class = main_serializers.TimeSheetRowCreateSerializer
    serializer_update_class = main_serializers.TimeSheetRowUpdateSerializer

    search_fields = ['task_name', 'task_description']
    ordering_fields = list(itertools.chain(*[
        [k, f'-{k}']
        for k in ['id', 'date_from', 'date_to', 'cv_id', 'reques_id', 'task_name']
    ]))
    ordering = ['-date_from', '-id']

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'cv_id',
                openapi.IN_QUERY,
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_INTEGER),
                description='`ANY`',
                required=False,
            ),
            openapi.Parameter(
                'request_id',
                openapi.IN_QUERY,
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_INTEGER),
                description='`ANY`',
                required=False,
            ),
            openapi.Parameter(
                'module_id',
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
            openapi.Parameter(
                'organization_customer_id',
                openapi.IN_QUERY,
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_INTEGER),
                description='`ANY`',
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
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        responses={
            status.HTTP_201_CREATED: main_serializers.TimeSheetRowUpdateSerializer(many=True)
        }
    )
    def create(self, request, *args, **kwargs):
        request_serializer = self.get_serializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        request_serializer_data = request_serializer.validated_data
        cv_ids = request_serializer_data.pop('cv_ids')
        try:
            time_sheet_rows = main_models.TimeSheetRow.objects.create_for_cv(cv_ids, **request_serializer_data)
        except ValidationError as e:
            raise serializers.ValidationError(e.args[0])
        response_serializer = main_serializers.TimeSheetRowUpdateSerializer(instance=time_sheet_rows, many=True)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
