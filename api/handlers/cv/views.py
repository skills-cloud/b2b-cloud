import itertools
from typing import List

from django.db import transaction
from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from django_filters import DateFromToRangeFilter
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from django_filters import rest_framework as filters
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response

from dictionary import models as dictionary_models
from main import models as main_models
from cv import models as cv_models

from api.filters import (
    OrderingFilterNullsLast,
    ModelMultipleChoiceCommaSeparatedFilter,
    DateRangeWidget,
)
from api.serializers import StatusSerializer
from api.views_mixins import ViewSetFilteredByUserMixin
from api.handlers.cv import serializers as cv_serializers
from project.contrib.db import get_sql_from_queryset

cv_viewsets_http_method_names = ['get', 'post', 'patch', 'delete']
cv_linked_filter_cv_field = openapi.Parameter('cv_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False)


class CvViewSet(ViewSetFilteredByUserMixin, viewsets.ModelViewSet):
    class Filter(filters.FilterSet):
        country_id = ModelMultipleChoiceCommaSeparatedFilter(queryset=dictionary_models.Country.objects)
        city_id = ModelMultipleChoiceCommaSeparatedFilter(queryset=dictionary_models.City.objects)
        citizenship_id = ModelMultipleChoiceCommaSeparatedFilter(queryset=dictionary_models.Citizenship.objects)
        competencies_ids_any = ModelMultipleChoiceCommaSeparatedFilter(
            field_name='competencies', queryset=dictionary_models.Competence.objects)
        competencies_ids_all = ModelMultipleChoiceCommaSeparatedFilter(
            field_name='competencies', conjoined=True,
            queryset=dictionary_models.Competence.objects,
        )

    http_method_names = cv_viewsets_http_method_names
    filterset_class = Filter
    filter_backends = [filters.DjangoFilterBackend, OrderingFilterNullsLast, SearchFilter]
    search_fields = ['first_name', 'middle_name', 'last_name']
    ordering_fields = list(itertools.chain(*[
        [k, f'-{k}']
        for k in ['id', 'first_name', 'middle_name', 'last_name', 'created_at', 'updated_at']
    ]))
    ordering = ['-updated_at']
    queryset = cv_models.CV.objects

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            'country',
            'city',
            'citizenship',
            'competencies',
            'contacts', 'contacts__contact_type',
            'time_slots', 'time_slots__country', 'time_slots__city', 'time_slots__type_of_employment',
            'positions', 'positions__position', 'positions__files',
            'career', 'career__files', 'career__organization', 'career__projects', 'career__position',
            'education',
            'certificates',
            'files',
        )

    def get_serializer_class(self):
        if self.action == 'list':
            return cv_serializers.CvListSerializer
        if self.request.method in SAFE_METHODS:
            return cv_serializers.CvDetailReadSerializer
        return cv_serializers.CvDetailSerializer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'country_id',
                openapi.IN_QUERY,
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_INTEGER),
                description='`ANY`',
                required=False
            ),
            openapi.Parameter(
                'city_id',
                openapi.IN_QUERY,
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_INTEGER),
                description='`ANY`',
                required=False,
            ),
            openapi.Parameter(
                'citizenship_id',
                openapi.IN_QUERY,
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_INTEGER),
                description='`ANY`',
                required=False,
            ),
            openapi.Parameter(
                'competencies_ids_any',
                openapi.IN_QUERY,
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_INTEGER),
                description='`ANY`',
                required=False,
            ),
            openapi.Parameter(
                'competencies_ids_all',
                openapi.IN_QUERY,
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_INTEGER),
                description='`ALL`',
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
        request_body=cv_serializers.CvSetPhotoSerializer,
        responses={
            status.HTTP_201_CREATED: cv_serializers.CvSetPhotoSerializer()
        },
    )
    @action(detail=True, methods=['post'], url_path='set-photo', parser_classes=[MultiPartParser])
    @transaction.atomic
    def set_photo(self, request, pk, *args, **kwargs):
        serializer = cv_serializers.CvSetPhotoSerializer(instance=self.get_object(), data=request.data)
        serializer.is_valid()
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        request_body=cv_serializers.CvFileSerializer,
        responses={
            status.HTTP_201_CREATED: cv_serializers.CvFileReadSerializer()
        },
    )
    @action(detail=True, methods=['post'], url_path='upload-file', parser_classes=[MultiPartParser])
    @transaction.atomic
    def upload_file(self, request, pk, *args, **kwargs):
        request_serializer = cv_serializers.CvFileSerializer(data=request.data)
        request_serializer.is_valid()
        instance = request_serializer.save(cv_id=self.get_object().id)
        response_serializer = cv_serializers.CvFileReadSerializer(instance=instance)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        responses={
            status.HTTP_204_NO_CONTENT: StatusSerializer()
        },
    )
    @action(detail=True, methods=['delete'], url_path='delete-file/(?P<file_id>[0-9]+)')
    @transaction.atomic
    def delete_file(self, request, pk, file_id, *args, **kwargs):
        self.get_object()
        get_object_or_404(queryset=cv_models.CvFile.objects, pk=file_id).delete()
        return Response(StatusSerializer({'status': 'ok'}).data, status=status.HTTP_204_NO_CONTENT)


class CvLinkedObjectFilter(filters.FilterSet):
    cv_id = filters.ModelChoiceFilter(queryset=cv_models.CV.objects)


class CvLinkedObjectFilterBackend(filters.DjangoFilterBackend):
    def get_filterset_class(self, view, queryset=None):
        if filterset_class := getattr(view, 'Filter', None):
            return filterset_class
        return super().get_filterset_class(view, queryset) or CvLinkedObjectFilter


class CvLinkedObjectViewSet(ViewSetFilteredByUserMixin, viewsets.ModelViewSet):
    http_method_names = cv_viewsets_http_method_names
    filter_backends = [CvLinkedObjectFilterBackend, OrderingFilterNullsLast, SearchFilter]

    serializer_class = None
    serializer_read_class = None

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return self.serializer_read_class
        return self.serializer_class

    def get_queryset_prefetch_related(self) -> List:
        return []

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            *self.get_queryset_prefetch_related()
        )


class CvCompetenceViewSet(CvLinkedObjectViewSet):
    queryset = cv_models.CvCompetence.objects
    serializer_class = cv_serializers.CvCompetenceSerializer
    serializer_read_class = cv_serializers.CvCompetenceReadSerializer

    def get_queryset_prefetch_related(self):
        return ['competence']

    @swagger_auto_schema(
        manual_parameters=[
            cv_linked_filter_cv_field,
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class CvContactViewSet(CvLinkedObjectViewSet):
    class Filter(CvLinkedObjectFilter):
        contact_type_id = ModelMultipleChoiceCommaSeparatedFilter(queryset=dictionary_models.ContactType.objects)

    search_fields = ['value']
    queryset = cv_models.CvContact.objects
    serializer_class = cv_serializers.CvContactSerializer
    serializer_read_class = cv_serializers.CvContactReadSerializer

    def get_queryset_prefetch_related(self):
        return ['contact_type']

    @swagger_auto_schema(
        manual_parameters=[
            cv_linked_filter_cv_field,
            openapi.Parameter(
                'contact_type_id',
                openapi.IN_QUERY,
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_INTEGER),
                required=False
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class CvTimeSlotViewSet(CvLinkedObjectViewSet):
    class Filter(CvLinkedObjectFilter):
        class DateRangeFilterField(DateFromToRangeFilter):
            def __init__(self, *args, **kwargs):
                super().__init__(widget=DateRangeWidget, *args, **kwargs)

            def filter(self, qs, value):
                condition = Q()
                if value is not None:
                    if value.start is not None and value.stop is not None:
                        condition = Q(
                            Q(date_from__range=[value.start, value.stop])
                            | Q(date_to__range=[value.start, value.stop])
                        )
                    elif value.start is not None:
                        condition = Q(date_from__gte=value.start)
                    elif value.stop is not None:
                        condition = Q(date_to__lte=value.stop)
                return qs.filter(condition)

        country_id = ModelMultipleChoiceCommaSeparatedFilter(queryset=dictionary_models.Country.objects)
        city_id = ModelMultipleChoiceCommaSeparatedFilter(queryset=dictionary_models.City.objects)
        type_of_employment_id = ModelMultipleChoiceCommaSeparatedFilter(
            queryset=dictionary_models.TypeOfEmployment.objects)
        date_range = DateRangeFilterField()

    queryset = cv_models.CvTimeSlot.objects
    serializer_class = cv_serializers.CvTimeSlotSerializer
    serializer_read_class = cv_serializers.CvTimeSlotReadSerializer

    def get_queryset_prefetch_related(self):
        return ['country', 'city', 'type_of_employment']

    @swagger_auto_schema(
        manual_parameters=[
            cv_linked_filter_cv_field,
            openapi.Parameter(
                'country_id',
                openapi.IN_QUERY,
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_INTEGER),
                required=False
            ),
            openapi.Parameter(
                'city_id',
                openapi.IN_QUERY,
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_INTEGER),
                required=False
            ),
            openapi.Parameter(
                'type_of_employment_id',
                openapi.IN_QUERY,
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_INTEGER),
                required=False
            ),
            openapi.Parameter(
                'date_range_from',
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                required=False
            ),
            openapi.Parameter(
                'date_range_to',
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                required=False
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class CvPositionViewSet(CvLinkedObjectViewSet):
    class Filter(CvLinkedObjectFilter):
        position_id = ModelMultipleChoiceCommaSeparatedFilter(queryset=dictionary_models.Position.objects)

    queryset = cv_models.CvPosition.objects
    serializer_class = cv_serializers.CvPositionSerializer
    serializer_read_class = cv_serializers.CvPositionReadSerializer

    def get_queryset_prefetch_related(self):
        return ['position', 'competencies']

    @swagger_auto_schema(
        manual_parameters=[
            cv_linked_filter_cv_field,
            openapi.Parameter(
                'position_id',
                openapi.IN_QUERY,
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_INTEGER),
                required=False
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=cv_serializers.CvPositionFileSerializer,
        responses={
            status.HTTP_201_CREATED: cv_serializers.CvPositionFileReadSerializer()
        },
    )
    @action(detail=True, methods=['post'], url_path='upload-file', parser_classes=[MultiPartParser])
    @transaction.atomic
    def upload_file(self, request, pk, *args, **kwargs):
        request_serializer = cv_serializers.CvPositionFileSerializer(data=request.data)
        request_serializer.is_valid()
        instance = request_serializer.save(cv_position_id=self.get_object().id)
        response_serializer = cv_serializers.CvPositionFileReadSerializer(instance=instance)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        responses={
            status.HTTP_204_NO_CONTENT: StatusSerializer()
        },
    )
    @action(detail=True, methods=['delete'], url_path='delete-file/(?P<file_id>[0-9]+)')
    @transaction.atomic
    def delete_file(self, request, pk, file_id, *args, **kwargs):
        self.get_object()
        get_object_or_404(queryset=cv_models.CvPositionFile.objects, pk=file_id).delete()
        return Response(StatusSerializer({'status': 'ok'}).data, status=status.HTTP_204_NO_CONTENT)


class CvCareerViewSet(CvLinkedObjectViewSet):
    class Filter(CvLinkedObjectFilter):
        position_id = ModelMultipleChoiceCommaSeparatedFilter(queryset=dictionary_models.Position.objects)
        organization_id = ModelMultipleChoiceCommaSeparatedFilter(queryset=main_models.Organization.objects)

    queryset = cv_models.CvCareer.objects
    serializer_class = cv_serializers.CvCareerSerializer
    serializer_read_class = cv_serializers.CvCareerReadSerializer

    def get_queryset_prefetch_related(self):
        return ['organization', 'position', 'competencies', 'projects']

    @swagger_auto_schema(
        manual_parameters=[
            cv_linked_filter_cv_field,
            openapi.Parameter(
                'position_id',
                openapi.IN_QUERY,
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_INTEGER),
                required=False
            ),
            openapi.Parameter(
                'organization_id',
                openapi.IN_QUERY,
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_INTEGER),
                required=False
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=cv_serializers.CvCareerFileSerializer,
        responses={
            status.HTTP_201_CREATED: cv_serializers.CvCareerFileReadSerializer()
        },
    )
    @action(detail=True, methods=['post'], url_path='upload-file', parser_classes=[MultiPartParser])
    @transaction.atomic
    def upload_file(self, request, pk, *args, **kwargs):
        request_serializer = cv_serializers.CvCareerFileSerializer(data=request.data)
        request_serializer.is_valid()
        instance = request_serializer.save(cv_career_id=self.get_object().id)
        response_serializer = cv_serializers.CvCareerFileReadSerializer(instance=instance)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        responses={
            status.HTTP_204_NO_CONTENT: StatusSerializer()
        },
    )
    @action(detail=True, methods=['delete'], url_path='delete-file/(?P<file_id>[0-9]+)')
    @transaction.atomic
    def delete_file(self, request, pk, file_id, *args, **kwargs):
        self.get_object()
        get_object_or_404(queryset=cv_models.CvCareerFile.objects, pk=file_id).delete()
        return Response(StatusSerializer({'status': 'ok'}).data, status=status.HTTP_204_NO_CONTENT)


class CvEducationViewSet(CvLinkedObjectViewSet):
    class Filter(CvLinkedObjectFilter):
        class DateRangeFilterField(DateFromToRangeFilter):
            def __init__(self, *args, **kwargs):
                super().__init__(widget=DateRangeWidget, *args, **kwargs)

            def filter(self, qs, value):
                condition = Q()
                if value is not None:
                    if value.start is not None and value.stop is not None:
                        condition = Q(
                            Q(date_from__range=[value.start, value.stop])
                            | Q(date_to__range=[value.start, value.stop])
                        )
                    elif value.start is not None:
                        condition = Q(date_from__gte=value.start)
                    elif value.stop is not None:
                        condition = Q(date_to__lte=value.stop)
                return qs.filter(condition)

        date_range = DateRangeFilterField()

    queryset = cv_models.CvEducation.objects
    serializer_class = cv_serializers.CvEducationSerializer
    serializer_read_class = cv_serializers.CvEducationReadSerializer

    def get_queryset_prefetch_related(self):
        return ['education_place', 'education_place', 'education_place']

    @swagger_auto_schema(
        manual_parameters=[
            cv_linked_filter_cv_field,
            openapi.Parameter(
                'date_range_from',
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                required=False
            ),
            openapi.Parameter(
                'date_range_to',
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                required=False
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class CvCertificateViewSet(CvLinkedObjectViewSet):
    queryset = cv_models.CvCertificate.objects
    serializer_class = cv_serializers.CvCertificateSerializer
    serializer_read_class = cv_serializers.CvCertificateReadSerializer

    def get_queryset_prefetch_related(self):
        return ['education_place', 'education_place', 'education_place']

    @swagger_auto_schema(
        manual_parameters=[
            cv_linked_filter_cv_field,
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
