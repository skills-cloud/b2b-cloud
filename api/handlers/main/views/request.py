import itertools

from django.db import transaction
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters import rest_framework as filters
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from api.serializers import EmptySerializer, StatusSerializer
from main import models as main_models
from cv import models as cv_models
from api.views_mixins import ReadWriteSerializersMixin, ViewSetFilteredByUserMixin
from api.backends import FilterBackend
from api.filters import OrderingFilterNullsLast, ModelMultipleChoiceCommaSeparatedFilter
from api.handlers.main import serializers as main_serializers
from api.handlers.main.views.base import MainBaseViewSet

__all__ = [
    'RequestTypeViewSet',
    'RequestViewSet',
    'RequestRequirementViewSet',
]


class RequestTypeViewSet(MainBaseViewSet):
    queryset = main_models.RequestType.objects
    serializer_class = main_serializers.RequestTypeSerializer


class RequestViewSet(ReadWriteSerializersMixin, ViewSetFilteredByUserMixin, ModelViewSet):
    class Filter(filters.FilterSet):
        type_id = ModelMultipleChoiceCommaSeparatedFilter(queryset=main_models.RequestType.objects)

        class Meta:
            model = main_models.Request
            fields = [
                'organization_project_id', 'type_id', 'status', 'priority', 'industry_sector_id', 'project_id',
                'resource_manager_id', 'recruiter_id',
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
        card_items_ids = request.data.pop('organization_project_card_items_ids', None)
        details_serializer = main_serializers.RequestRequirementCvWriteDetailsSerializer(data=request.data)
        details_serializer.is_valid(raise_exception=True)
        instance = main_models.RequestRequirementCv(
            request_requirement=self.get_object(),
            cv=get_object_or_404(cv_models.CV.objects.filter_by_user(request.user), id=cv_id),
            **details_serializer.validated_data
        )
        instance.save()
        if card_items_ids is not None:
            instance.organization_project_card_items.add(*card_items_ids)
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
        card_items_ids = request.data.pop('organization_project_card_items_ids', None)
        details_serializer = main_serializers.RequestRequirementCvWriteDetailsSerializer(data=request.data)
        details_serializer.is_valid(raise_exception=True)
        instance = self._get_cv_linked_or_404(request, cv_id)
        for k, v in details_serializer.validated_data.items():
            setattr(instance, k, v)
        instance.save()
        if card_items_ids is not None:
            instance.organization_project_card_items.clear()
            instance.organization_project_card_items.add(*card_items_ids)
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

    def _get_cv_linked_or_404(self, request, cv_id: int) -> main_models.RequestRequirementCv:
        return get_object_or_404(main_models.RequestRequirementCv.objects.filter(
            request_requirement=self.get_object(),
            cv=get_object_or_404(cv_models.CV.objects.filter_by_user(request.user), id=cv_id),
        ))
