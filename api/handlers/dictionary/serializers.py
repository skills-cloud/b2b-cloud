from rest_framework import serializers
from rest_framework_recursive.fields import RecursiveField

from api.fields import PrimaryKeyRelatedIdField
from dictionary import models as dictionary_models
from api.serializers import ModelSerializer


class DictionaryBaseSerializer(ModelSerializer):
    class Meta:
        exclude = ['created_at', 'updated_at', 'attributes']


class TypeOfEmploymentSerializer(DictionaryBaseSerializer):
    class Meta(DictionaryBaseSerializer.Meta):
        model = dictionary_models.TypeOfEmployment


class CountrySerializer(DictionaryBaseSerializer):
    class Meta(DictionaryBaseSerializer.Meta):
        model = dictionary_models.Country


class CitySerializer(DictionaryBaseSerializer):
    country_id = PrimaryKeyRelatedIdField(
        queryset=dictionary_models.Country.objects,
        label=dictionary_models.City._meta.get_field('country').verbose_name,
    )

    class Meta:
        model = dictionary_models.City
        fields = ['id', 'country_id', 'name', 'is_verified', 'sorting']


class CityReadSerializer(CitySerializer):
    country = CountrySerializer()

    class Meta(CitySerializer.Meta):
        fields = CitySerializer.Meta.fields + ['country']


class CitizenshipSerializer(DictionaryBaseSerializer):
    class Meta(DictionaryBaseSerializer.Meta):
        model = dictionary_models.Citizenship


class ContactTypeSerializer(DictionaryBaseSerializer):
    class Meta(DictionaryBaseSerializer.Meta):
        model = dictionary_models.ContactType


class EducationPlaceSerializer(DictionaryBaseSerializer):
    class Meta(DictionaryBaseSerializer.Meta):
        model = dictionary_models.EducationPlace


class EducationSpecialtySerializer(DictionaryBaseSerializer):
    class Meta(DictionaryBaseSerializer.Meta):
        model = dictionary_models.EducationSpecialty


class EducationGraduateSerializer(DictionaryBaseSerializer):
    class Meta(DictionaryBaseSerializer.Meta):
        model = dictionary_models.EducationGraduate


class PositionSerializer(DictionaryBaseSerializer):
    class Meta(DictionaryBaseSerializer.Meta):
        model = dictionary_models.Position


class CompetenceSerializer(DictionaryBaseSerializer):
    parent_id = PrimaryKeyRelatedIdField(
        queryset=dictionary_models.Competence.objects,
        label=dictionary_models.Competence._meta.get_field('parent').verbose_name,
    )

    class Meta(DictionaryBaseSerializer.Meta):
        model = dictionary_models.Competence
        fields = ['id', 'parent_id', 'name', 'description', 'sorting', 'is_verified']
        exclude = None


class PhysicalLimitationSerializer(DictionaryBaseSerializer):
    class Meta(DictionaryBaseSerializer.Meta):
        model = dictionary_models.PhysicalLimitation


class IndustrySectorSerializer(DictionaryBaseSerializer):
    class Meta(DictionaryBaseSerializer.Meta):
        model = dictionary_models.IndustrySector


class OrganizationSerializer(DictionaryBaseSerializer):
    class Meta(DictionaryBaseSerializer.Meta):
        model = dictionary_models.Organization


class CompetenceInlineSerializer(CompetenceSerializer):
    class Meta(CompetenceSerializer.Meta):
        fields = ['id', 'parent_id', 'name']
        exclude = None


class CompetenceTreeSerializer(DictionaryBaseSerializer):
    children = serializers.ListField(source='get_children', child=RecursiveField())

    class Meta(DictionaryBaseSerializer.Meta):
        model = dictionary_models.Competence
        exclude = None
        fields = ['id', 'parent_id', 'name', 'description', 'is_verified', 'children']
