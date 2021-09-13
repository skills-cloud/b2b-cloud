from typing import Dict, List, Any

from rest_framework import serializers
from rest_framework_recursive.fields import RecursiveField

from dictionary import models as dictionary_models
from api.serializers import ModelSerializer


class DictionaryBaseSerializer(ModelSerializer):
    class Meta:
        exclude = ['created_at', 'updated_at', 'sorting']


class TypeOfEmploymentSerializer(DictionaryBaseSerializer):
    class Meta(DictionaryBaseSerializer.Meta):
        model = dictionary_models.TypeOfEmployment


class CountrySerializer(DictionaryBaseSerializer):
    class Meta(DictionaryBaseSerializer.Meta):
        model = dictionary_models.Country


class CitySerializer(DictionaryBaseSerializer):
    country = CountrySerializer()

    class Meta(DictionaryBaseSerializer.Meta):
        model = dictionary_models.City


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
    class Meta(DictionaryBaseSerializer.Meta):
        model = dictionary_models.Competence
        fields = ['id', 'parent_id', 'name']
        exclude = None


class PhysicalLimitationSerializer(DictionaryBaseSerializer):
    class Meta(DictionaryBaseSerializer.Meta):
        model = dictionary_models.PhysicalLimitation


class IndustrySectorSerializer(DictionaryBaseSerializer):
    class Meta(DictionaryBaseSerializer.Meta):
        model = dictionary_models.IndustrySector


class CompetenceInlineSerializer(CompetenceSerializer):
    class Meta(CompetenceSerializer.Meta):
        fields = ['id', 'parent_id', 'name', 'description', 'is_verified']
        exclude = None


class CompetenceTreeSerializer(DictionaryBaseSerializer):
    children = serializers.ListField(source='get_children', child=RecursiveField())

    class Meta(DictionaryBaseSerializer.Meta):
        model = dictionary_models.Competence
        exclude = None
        fields = ['id', 'parent_id', 'name', 'description', 'is_verified', 'children']
