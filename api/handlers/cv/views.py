import itertools
from typing import List

from django.db import transaction
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response
from django_filters import DateFromToRangeFilter
from django_filters import rest_framework as filters
from django.utils.translation import gettext_lazy as _
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from dictionary import models as dictionary_models
from main import models as main_models
from cv import models as cv_models

from api.filters import (
    OrderingFilterNullsLast,
    ModelMultipleChoiceCommaSeparatedFilter,
    DateRangeWidget, ModelMultipleChoiceCommaSeparatedIdFilter,
)
from api.serializers import StatusSerializer, EmptySerializer
from api.views_mixins import ViewSetFilteredByUserMixin, ReadWriteSerializersMixin
from api.backends import FilterBackend
from api.handlers.cv import serializers as cv_serializers

cv_viewsets_http_method_names = ['get', 'post', 'patch', 'delete']
cv_linked_filter_cv_field = openapi.Parameter('cv_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False)


class CvViewSet(ViewSetFilteredByUserMixin, viewsets.ModelViewSet):
    class Filter(filters.FilterSet):
        id = ModelMultipleChoiceCommaSeparatedIdFilter(queryset=cv_models.CV.objects)
        country_id = ModelMultipleChoiceCommaSeparatedFilter(queryset=dictionary_models.Country.objects)
        city_id = ModelMultipleChoiceCommaSeparatedFilter(queryset=dictionary_models.City.objects)
        citizenship_id = ModelMultipleChoiceCommaSeparatedFilter(queryset=dictionary_models.Citizenship.objects)
        positions_ids_any = ModelMultipleChoiceCommaSeparatedFilter(
            field_name='positions__position_id',
            queryset=dictionary_models.Position.objects,
        )
        positions_ids_all = ModelMultipleChoiceCommaSeparatedFilter(
            field_name='positions__position_id',
            conjoined=True,
            queryset=dictionary_models.Position.objects,
        )
        competencies_ids_any = ModelMultipleChoiceCommaSeparatedFilter(
            field_name='positions__competencies__competence_id',
            queryset=dictionary_models.Competence.objects
        )
        competencies_ids_all = ModelMultipleChoiceCommaSeparatedFilter(
            field_name='positions__competencies__competence_id',
            conjoined=True,
            queryset=dictionary_models.Competence.objects,
        )
        years = filters.NumberFilter()

        def filter_queryset(self, queryset):
            if years := self.form.cleaned_data.pop('years'):
                queryset = queryset.filter_by_position_years(years)
            return super().filter_queryset(queryset)

    http_method_names = cv_viewsets_http_method_names
    filterset_class = Filter
    filter_backends = [FilterBackend, OrderingFilterNullsLast, SearchFilter]
    search_fields = ['first_name', 'middle_name', 'last_name', 'positions__title', 'positions__position__name']
    ordering_fields = list(itertools.chain(*[
        [k, f'-{k}']
        for k in ['id', 'first_name', 'middle_name', 'last_name', 'created_at', 'updated_at']
    ]))
    ordering = ['-updated_at']
    queryset = cv_models.CV.objects.distinct()

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            *cv_models.CV.objects.get_queryset_prefetch_related(),
            *cv_models.CV.objects.get_queryset_request_requirements_prefetch_related(),
        )

    def get_serializer_class(self):
        if self.action == 'list':
            return cv_serializers.CvListReadFullSerializer
        if self.request.method in SAFE_METHODS:
            return cv_serializers.CvDetailReadFullSerializer
        return cv_serializers.CvDetailWriteSerializer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_QUERY,
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_INTEGER),
                description='`ANY`',
                required=False
            ),
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
                'positions_ids_any',
                openapi.IN_QUERY,
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_INTEGER),
                description='`ANY`',
                required=False,
            ),
            openapi.Parameter(
                'positions_ids_all',
                openapi.IN_QUERY,
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_INTEGER),
                description='`ALL`',
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
        serializer.is_valid(raise_exception=True)
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

    @action(detail=True, methods=['delete'], url_path='delete-file/(?P<file_id>[0-9]+)')
    @transaction.atomic
    def delete_file(self, request, pk: int, file_id: int, *args, **kwargs):
        self.get_object()
        get_object_or_404(cv_models.CvFile.objects.filter_by_user(request.user), id=file_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        request_body=EmptySerializer(),
        responses={
            status.HTTP_201_CREATED: StatusSerializer()
        },
    )
    @action(detail=True, methods=['post'], url_path='cv-link/(?P<cv_link_id>[0-9]+)')
    @transaction.atomic
    def cv_link(self, request, pk: int, cv_link_id: int, *args, **kwargs):
        self.get_object().linked.add(
            get_object_or_404(cv_models.CV.objects.filter_by_user(request.user), id=cv_link_id)
        )
        return Response(StatusSerializer({'status': 'ok'}).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], url_path='cv-unlink/(?P<cv_link_id>[0-9]+)')
    @transaction.atomic
    def cv_unlink(self, request, pk: int, cv_link_id: int, *args, **kwargs):
        self.get_object().linked.remove(
            get_object_or_404(cv_models.CV.objects.filter_by_user(request.user), id=cv_link_id)
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class CvLinkedObjectFilter(filters.FilterSet):
    cv_id = filters.ModelChoiceFilter(queryset=cv_models.CV.objects)


class CvLinkedObjectFilterBackend(FilterBackend):
    def get_filterset_class(self, view, queryset=None):
        if filterset_class := getattr(view, 'Filter', None):
            return filterset_class
        return super().get_filterset_class(view, queryset) or CvLinkedObjectFilter


class CvLinkedObjectViewSet(ViewSetFilteredByUserMixin, ReadWriteSerializersMixin, viewsets.ModelViewSet):
    http_method_names = cv_viewsets_http_method_names
    filter_backends = [CvLinkedObjectFilterBackend, OrderingFilterNullsLast, SearchFilter]

    @classmethod
    def get_queryset_prefetch_related(cls) -> List[str]:
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

    @classmethod
    def get_queryset_prefetch_related(cls) -> List[str]:
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

        class Meta:
            model = cv_models.CvTimeSlot
            fields = [
                'country_id', 'city_id', 'type_of_employment_id', 'kind', 'is_free',
            ]

    queryset = cv_models.CvTimeSlot.objects
    serializer_class = cv_serializers.CvTimeSlotSerializer
    serializer_read_class = cv_serializers.CvTimeSlotReadSerializer

    @classmethod
    def get_queryset_prefetch_related(cls) -> List[str]:
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
                'kind',
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                enum=cv_models.CvTimeSlotKind.values,
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
            openapi.Parameter(
                'is_free',
                openapi.IN_QUERY,
                type=openapi.TYPE_BOOLEAN,
                required=False
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if self.get_object().kind == cv_models.CvTimeSlotKind.REQUEST_REQUIREMENT:
            raise ValidationError({'kind': _('Нельзя удалять слот, созданный системой')})
        return super().destroy(request, *args, **kwargs)


class CvPositionViewSet(CvLinkedObjectViewSet):
    class Filter(CvLinkedObjectFilter):
        position_id = ModelMultipleChoiceCommaSeparatedFilter(queryset=dictionary_models.Position.objects)

    queryset = cv_models.CvPosition.objects
    serializer_class = cv_serializers.CvPositionSerializer
    serializer_read_class = cv_serializers.CvPositionReadSerializer

    @classmethod
    def get_queryset_prefetch_related(cls) -> List[str]:
        return ['position', 'competencies', 'competencies__competence', 'files']

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
        request_body=cv_serializers.CvPositionCompetenceReplaceSerializer(many=True),
        responses={
            status.HTTP_201_CREATED: cv_serializers.CvPositionCompetenceSerializer(many=True)
        },
    )
    @action(detail=True, methods=['post'], url_path='competencies-set')
    @transaction.atomic
    def competencies_set(self, request, pk: int, *args, **kwargs):
        request_serializer = cv_serializers.CvPositionCompetenceReplaceSerializer(data=request.data, many=True)
        request_serializer.is_valid(raise_exception=True)
        response_serializer = cv_serializers.CvPositionCompetenceSerializer(
            cv_models.CvPositionCompetence.objects.set_for_position(
                self.get_object(),
                request_serializer.to_internal_value(request_serializer.data)
            ),
            many=True
        )
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

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
        request_serializer.is_valid(raise_exception=True)
        instance = request_serializer.save(cv_position_id=self.get_object().id)
        response_serializer = cv_serializers.CvPositionFileReadSerializer(instance=instance)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], url_path='delete-file/(?P<file_id>[0-9]+)')
    @transaction.atomic
    def delete_file(self, request, pk: int, file_id: int, *args, **kwargs):
        self.get_object()
        get_object_or_404(cv_models.CvPositionFile.objects.filter_by_user(request.user), id=file_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CvCareerViewSet(CvLinkedObjectViewSet):
    class Filter(CvLinkedObjectFilter):
        position_id = ModelMultipleChoiceCommaSeparatedFilter(queryset=dictionary_models.Position.objects)
        organization_id = ModelMultipleChoiceCommaSeparatedFilter(queryset=main_models.Organization.objects)

    queryset = cv_models.CvCareer.objects
    serializer_class = cv_serializers.CvCareerSerializer
    serializer_read_class = cv_serializers.CvCareerReadSerializer

    def get_queryset_prefetch_related(self):
        return ['organization', 'position', 'competencies', 'projects', 'projects__organization', 'files']

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
        request_serializer.is_valid(raise_exception=True)
        instance = request_serializer.save(cv_career_id=self.get_object().id)
        response_serializer = cv_serializers.CvCareerFileReadSerializer(instance=instance)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], url_path='delete-file/(?P<file_id>[0-9]+)')
    @transaction.atomic
    def delete_file(self, request, pk: int, file_id: int, *args, **kwargs):
        self.get_object()
        get_object_or_404(cv_models.CvCareerFile.objects.filter_by_user(request.user), id=file_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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

    @classmethod
    def get_queryset_prefetch_related(cls) -> List[str]:
        return ['education_place', 'education_graduate', 'education_speciality']

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


class CvProjectViewSet(CvLinkedObjectViewSet):
    class Filter(CvLinkedObjectFilter):
        position_id = ModelMultipleChoiceCommaSeparatedFilter(queryset=dictionary_models.Position.objects)
        organization_id = ModelMultipleChoiceCommaSeparatedFilter(queryset=main_models.Organization.objects)
        industry_sector_id = ModelMultipleChoiceCommaSeparatedFilter(queryset=dictionary_models.IndustrySector.objects)

    queryset = cv_models.CvProject.objects
    serializer_class = cv_serializers.CvProjectSerializer
    serializer_read_class = cv_serializers.CvProjectReadSerializer

    def get_queryset_prefetch_related(self):
        return ['organization', 'position', 'industry_sector', 'competencies']

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
            openapi.Parameter(
                'industry_sector_id',
                openapi.IN_QUERY,
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_INTEGER),
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

    @classmethod
    def get_queryset_prefetch_related(cls) -> List[str]:
        return ['education_place', 'education_graduate', 'education_speciality']

    @swagger_auto_schema(
        manual_parameters=[
            cv_linked_filter_cv_field,
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
