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
from api.filters import OrderingFilterNullsLast, ModelMultipleChoiceCommaSeparatedFilter
from api.handlers.main import serializers as main_serializers


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


class OrganizationViewSet(MainBaseViewSet):
    queryset = main_models.Organization.objects
    serializer_class = main_serializers.OrganizationSerializer
    filterset_fields = ['is_customer']


class OrganizationProjectViewSet(MainBaseViewSet):
    class Filter(filters.FilterSet):
        organization_id = filters.ModelChoiceFilter(queryset=main_models.Organization.objects)

    filter_class = Filter
    queryset = main_models.OrganizationProject.objects
    serializer_class = main_serializers.OrganizationProjectSerializer
    serializer_read_class = main_serializers.OrganizationProjectReadSerializer


class ProjectViewSet(MainBaseViewSet):
    queryset = main_models.Project.objects
    serializer_class = main_serializers.ProjectSerializer
    serializer_read_class = main_serializers.ProjectReadSerializer


class RequestTypeViewSet(MainBaseViewSet):
    queryset = main_models.RequestType.objects
    serializer_class = main_serializers.RequestTypeSerializer


class RequestViewSet(ReadWriteSerializersMixin, ViewSetFilteredByUserMixin, ModelViewSet):
    class Filter(filters.FilterSet):
        type_id = ModelMultipleChoiceCommaSeparatedFilter(queryset=main_models.RequestType.objects)

        class Meta:
            model = main_models.Request
            fields = [
                'type_id', 'customer_id', 'status', 'priority', 'industry_sector_id', 'project_id',
                'resource_manager_id', 'recruiter_id',
            ]

    http_method_names = ['get', 'post', 'patch', 'delete']
    queryset = main_models.Request.objects.prefetch_related(
        *main_models.Request.objects.get_queryset_prefetch_related()
    )
    serializer_class = main_serializers.RequestSerializer
    serializer_read_class = main_serializers.RequestReadSerializer
    filter_backends = [filters.DjangoFilterBackend, OrderingFilterNullsLast, SearchFilter]
    filterset_class = Filter
    search_fields = ['id', 'description']
    ordering_fields = list(itertools.chain(*[
        [k, f'-{k}']
        for k in ['id', 'type', 'priority', 'start_date', 'deadline_date', 'customer']
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
        request_body=EmptySerializer(),
        responses={
            status.HTTP_201_CREATED: StatusSerializer()
        },
    )
    @action(detail=True, methods=['post'], url_path='cv-link/(?P<cv_id>[0-9]+)')
    @transaction.atomic
    def cv_link(self, request, pk: int, cv_id: int, *args, **kwargs):
        instance = self.get_object()
        instance.cv_list.add(get_object_or_404(cv_models.CV.objects.filter_by_user(request.user), id=cv_id))
        return Response(StatusSerializer({'status': 'ok'}).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], url_path='cv-unlink/(?P<cv_id>[0-9]+)')
    @transaction.atomic
    def cv_unlink(self, request, pk: int, cv_id: int, *args, **kwargs):
        instance = self.get_object()
        instance.cv_list.remove(get_object_or_404(cv_models.CV.objects.filter_by_user(request.user), id=cv_id))
        return Response(status=status.HTTP_204_NO_CONTENT)
