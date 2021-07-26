import itertools
from typing import List

from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, mixins, status
from django_filters import rest_framework as filters, DateFromToRangeFilter
from rest_framework.filters import SearchFilter
from django_filters import rest_framework as filters
from rest_framework.permissions import SAFE_METHODS

from dictionary import models as dictionary_models
from main import models as main_models
from cv import models as cv_models

from api.filters import (
    OrderingFilterNullsLast,
    ModelMultipleChoiceCommaSeparatedFilter,
    DateRangeWidget,
)
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
            'positions', 'positions__files',
            'career', 'career__files',
            'projects',
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


class CvLinkedObjectFilter(filters.FilterSet):
    cv_id = filters.ModelChoiceFilter(queryset=cv_models.CV.objects)


class CvLinkedObjectFilterBackend(filters.DjangoFilterBackend):
    def get_filterset_class(self, view, queryset=None):
        if filterset_class := getattr(view, 'Filter', None):
            return filterset_class
        return super().get_filterset_class(view, queryset)


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
