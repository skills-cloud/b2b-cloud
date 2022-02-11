import itertools

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, mixins
from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter
from rest_framework.viewsets import ModelViewSet

from dictionary import models as dictionary_models
from api.views import ReadWriteSerializersMixin
from api.filters import OrderingFilterNullsLast, ModelMultipleChoiceCommaSeparatedIdFilter
from api.backends import FilterBackend
from api.handlers.dictionary import serializers as dictionary_serializers


class DictionaryBaseViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [FilterBackend, OrderingFilterNullsLast, SearchFilter]
    search_fields = ['name']
    ordering_fields = list(itertools.chain(*[
        [k, f'-{k}']
        for k in ['id', 'name', 'sorting']
    ]))
    ordering = ['sorting', 'name']

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


class CountryViewSet(DictionaryBaseViewSet):
    queryset = dictionary_models.Country.objects
    serializer_class = dictionary_serializers.CountrySerializer


class TypeOfEmploymentViewSet(DictionaryBaseViewSet):
    queryset = dictionary_models.TypeOfEmployment.objects
    serializer_class = dictionary_serializers.TypeOfEmploymentSerializer


class CityViewSet(ReadWriteSerializersMixin, DictionaryBaseViewSet):
    queryset = dictionary_models.City.objects.prefetch_related('country')
    serializer_class = dictionary_serializers.CitySerializer
    serializer_read_class = dictionary_serializers.CityReadSerializer
    search_fields = ['name', 'country__name']
    filterset_fields = ['country_id']


class CitizenshipViewSet(DictionaryBaseViewSet):
    queryset = dictionary_models.Citizenship.objects
    serializer_class = dictionary_serializers.CitizenshipSerializer


class ContactTypeViewSet(DictionaryBaseViewSet):
    queryset = dictionary_models.ContactType.objects
    serializer_class = dictionary_serializers.ContactTypeSerializer


class EducationPlaceViewSet(DictionaryBaseViewSet):
    queryset = dictionary_models.EducationPlace.objects
    serializer_class = dictionary_serializers.EducationPlaceSerializer


class EducationSpecialtyViewSet(DictionaryBaseViewSet):
    queryset = dictionary_models.EducationSpecialty.objects
    serializer_class = dictionary_serializers.EducationSpecialtySerializer


class EducationGraduateViewSet(DictionaryBaseViewSet):
    queryset = dictionary_models.EducationGraduate.objects
    serializer_class = dictionary_serializers.EducationGraduateSerializer


class PositionViewSet(DictionaryBaseViewSet):
    queryset = dictionary_models.Position.objects
    serializer_class = dictionary_serializers.PositionSerializer


class IndustrySectorViewSet(DictionaryBaseViewSet):
    queryset = dictionary_models.IndustrySector.objects
    serializer_class = dictionary_serializers.IndustrySectorSerializer


class OrganizationViewSet(DictionaryBaseViewSet):
    queryset = dictionary_models.Organization.objects
    serializer_class = dictionary_serializers.OrganizationSerializer


class PhysicalLimitationViewSet(DictionaryBaseViewSet):
    queryset = dictionary_models.PhysicalLimitation.objects
    serializer_class = dictionary_serializers.PhysicalLimitationSerializer


class CompetenceViewSet(DictionaryBaseViewSet):
    class Filter(filters.FilterSet):
        id = ModelMultipleChoiceCommaSeparatedIdFilter(queryset=dictionary_models.Competence.objects)

    queryset = dictionary_models.Competence.objects_flat
    filterset_class = Filter
    serializer_class = dictionary_serializers.CompetenceSerializer
    ordering_fields = list(itertools.chain(*[
        [k, f'-{k}']
        for k in ['id', 'name']
    ]))
    ordering = ['name']

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


class CompetenceTreeViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = dictionary_models.Competence.objects.filter(mptt_level=0).prefetch_related('children')
    serializer_class = dictionary_serializers.CompetenceTreeSerializer
    pagination_class = None
