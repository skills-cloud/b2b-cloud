import itertools

from django.core.exceptions import ValidationError
from rest_framework import status, serializers
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django_filters import rest_framework as filters
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from cv import models as cv_models
from main import models as main_models
from api.views_mixins import ReadCreateUpdateSerializersMixin, ViewSetFilteredByUserMixin
from api.backends import FilterBackend
from api.filters import ModelMultipleChoiceCommaSeparatedFilter, OrderingFilterNullsLast
from api.handlers.main import serializers as main_serializers

__all__ = [
    'TimeSheetRowViewSet',
]


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
        organization_project_id = ModelMultipleChoiceCommaSeparatedFilter(
            queryset=main_models.OrganizationProject.objects,
            field_name='request__organization_project',
        )
        organization_id = ModelMultipleChoiceCommaSeparatedFilter(
            queryset=main_models.Organization.objects,
            field_name='request__organization_project__organization',
        )

        class Meta:
            model = main_models.TimeSheetRow
            fields = [
                'cv_id', 'request_id', 'organization_project_id', 'organization_id',
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
                'organization_project_id',
                openapi.IN_QUERY,
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_INTEGER),
                description='`ANY`',
                required=False,
            ),
            openapi.Parameter(
                'organization_id',
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
