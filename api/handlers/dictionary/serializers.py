from typing import Dict, List, Any

from rest_framework import serializers

from dictionary import models as dictionary_models
from api.serializers import ModelSerializer


class DictionaryBaseSerializer(ModelSerializer):
    class Meta:
        exclude = ['created_at', 'updated_at', 'sorting']


class CountrySerializer(DictionaryBaseSerializer):
    class Meta(DictionaryBaseSerializer.Meta):
        model = dictionary_models.Country


class TypeOfEmploymentSerializer(DictionaryBaseSerializer):
    class Meta(DictionaryBaseSerializer.Meta):
        model = dictionary_models.TypeOfEmployment


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


class CompetenceTreeSerializer(DictionaryBaseSerializer):
    children = serializers.SerializerMethodField()

    class Meta(DictionaryBaseSerializer.Meta):
        model = dictionary_models.Competence
        exclude = None
        fields = ['id', 'name', 'children']

    def get_children(self, instance: dictionary_models.Competence) -> List[Dict[str, Any]]:
        return CompetenceTreeSerializer(instance.get_children(), many=True).data
