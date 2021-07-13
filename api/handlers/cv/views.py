import itertools

from django.utils.translation import gettext_lazy as _
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, mixins, status
from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter
from django_filters import rest_framework as filters
from rest_framework.permissions import SAFE_METHODS

from dictionary import models as dictionary_models
from main import models as main_models
from cv import models as cv_models

from api.filters import (
    OrderingFilterNullsLast,
    ModelMultipleChoiceCommaSeparatedFilter,
)
from api.views_mixins import ViewSetFilteredByUserMixin
from api.handlers.cv import serializers as cv_serializers

cv_viewsets_http_method_names = ['get', 'post', 'patch', 'delete']


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
                description='`ANY`', required=False),
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


class CvContactViewSet(ViewSetFilteredByUserMixin, viewsets.ModelViewSet):
    class Filter(CvLinkedObjectFilter):
        contact_type_id = filters.ModelChoiceFilter(queryset=dictionary_models.ContactType.objects)

    http_method_names = cv_viewsets_http_method_names
    filterset_class = Filter
    filter_backends = [filters.DjangoFilterBackend, SearchFilter]
    search_fields = ['value']
    queryset = cv_models.CvContact.objects

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            'contact_type',
        )

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return cv_serializers.CvContactReadSerializer
        return cv_serializers.CvContactSerializer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('cv_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('contact_type_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class CvTimeSlotViewSet(ViewSetFilteredByUserMixin, viewsets.ModelViewSet):
    class Filter(CvLinkedObjectFilter):
        country_id = filters.ModelChoiceFilter(queryset=dictionary_models.Country.objects)
        city_id = filters.ModelChoiceFilter(queryset=dictionary_models.City.objects)
        type_of_employment_id = filters.ModelChoiceFilter(queryset=dictionary_models.TypeOfEmployment.objects)

    http_method_names = cv_viewsets_http_method_names
    filterset_class = Filter
    filter_backends = [filters.DjangoFilterBackend, SearchFilter]
    queryset = cv_models.CvTimeSlot.objects

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            'country', 'city', 'type_of_employment',
        )

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return cv_serializers.CvTimeSlotReadSerializer
        return cv_serializers.CvTimeSlotSerializer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('cv_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('country_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('city_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('type_of_employment_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
