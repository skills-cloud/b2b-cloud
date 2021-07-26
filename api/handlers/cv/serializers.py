from rest_framework import fields

from acc.models import User
from api import serializers
from api.handlers.acc.serializers import UserInlineSerializer
from dictionary import models as dictionary_models
from main import models as main_models
from cv import models as cv_models

from api.serializers import ModelSerializer
from api.handlers.dictionary import serializers as dictionary_serializers
from api.handlers.main import serializers as main_serializers


class CvLinkedObjectBaseSerializer(ModelSerializer):
    cv_id = serializers.PrimaryKeyRelatedIdField(
        queryset=dictionary_models.ContactType.objects
    )

    class Meta:
        fields = ['cv_id', 'id']


########################################################################################################################
# CvContact
########################################################################################################################


class CvContactSerializer(CvLinkedObjectBaseSerializer):
    contact_type_id = serializers.PrimaryKeyRelatedIdField(
        queryset=dictionary_models.ContactType.objects
    )

    class Meta:
        model = cv_models.CvContact
        fields = CvLinkedObjectBaseSerializer.Meta.fields + [
            'contact_type_id', 'value', 'is_primary', 'comment',
        ]


class CvContactReadSerializer(CvContactSerializer):
    contact_type_id = serializers.PrimaryKeyRelatedIdField(
        queryset=dictionary_models.ContactType.objects
    )
    contact_type = dictionary_serializers.ContactTypeSerializer(read_only=True)

    class Meta(CvContactSerializer.Meta):
        model = cv_models.CvContact
        fields = CvContactSerializer.Meta.fields + ['contact_type']


########################################################################################################################
# CvTimeSlot
########################################################################################################################


class CvTimeSlotSerializer(CvLinkedObjectBaseSerializer):
    country_id = serializers.PrimaryKeyRelatedIdField(
        queryset=dictionary_models.Country.objects, allow_null=True, required=False
    )
    city_id = serializers.PrimaryKeyRelatedIdField(
        queryset=dictionary_models.City.objects, allow_null=True, required=False
    )
    type_of_employment_id = serializers.PrimaryKeyRelatedIdField(
        queryset=dictionary_models.TypeOfEmployment.objects
    )

    class Meta:
        model = cv_models.CvTimeSlot
        fields = CvLinkedObjectBaseSerializer.Meta.fields + [
            'date_from', 'date_to', 'price', 'is_work_permit_required', 'description',
            'country_id', 'city_id', 'type_of_employment_id',
        ]


class CvTimeSlotReadSerializer(CvTimeSlotSerializer):
    country = dictionary_serializers.CountrySerializer(read_only=True, allow_null=True)
    city = dictionary_serializers.CitySerializer(read_only=True, allow_null=True)
    type_of_employment = dictionary_serializers.TypeOfEmploymentSerializer(read_only=True, allow_null=True)

    class Meta(CvTimeSlotSerializer.Meta):
        fields = CvTimeSlotSerializer.Meta.fields + [
            'country', 'city', 'type_of_employment'
        ]


########################################################################################################################
# CvPosition
########################################################################################################################


class CvPositionSerializer(CvLinkedObjectBaseSerializer):
    position_id = serializers.PrimaryKeyRelatedIdField(
        queryset=dictionary_models.Position.objects
    )
    competencies_ids = serializers.PrimaryKeyRelatedIdField(source='competencies', read_only=True, many=True)

    class Meta:
        model = cv_models.CvPosition
        fields = CvLinkedObjectBaseSerializer.Meta.fields + [
            'position_id', 'competencies_ids'
        ]


class CvPositionReadSerializer(CvPositionSerializer):
    position = dictionary_serializers.CountrySerializer(read_only=True, allow_null=True)

    class Meta(CvPositionSerializer.Meta):
        fields = CvPositionSerializer.Meta.fields + [
            'position'
        ]


########################################################################################################################
# CV
########################################################################################################################


class CvDetailSerializer(ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedIdField(queryset=User.objects, allow_null=True, required=False)
    country_id = serializers.PrimaryKeyRelatedIdField(
        queryset=dictionary_models.Country.objects, allow_null=True, required=False
    )
    city_id = serializers.PrimaryKeyRelatedIdField(
        queryset=dictionary_models.City.objects, allow_null=True, required=False
    )
    citizenship_id = serializers.PrimaryKeyRelatedIdField(
        queryset=dictionary_models.City.objects, allow_null=True, required=False
    )

    class Meta:
        model = cv_models.CV
        fields = [
            'id', 'first_name', 'middle_name', 'last_name', 'photo', 'gender', 'birth_date', 'is_with_disabilities',
            'is_resource_owner', 'user_id', 'country_id', 'city_id', 'citizenship_id',
        ]


class CvDetailReadSerializer(CvDetailSerializer):
    user = UserInlineSerializer(read_only=True, allow_null=True)
    country = dictionary_serializers.CountrySerializer(read_only=True, allow_null=True)
    city = dictionary_serializers.CitySerializer(read_only=True, allow_null=True)
    citizenship = dictionary_serializers.CitizenshipSerializer(read_only=True, allow_null=True)
    competencies_ids = serializers.PrimaryKeyRelatedIdField(source='competencies', read_only=True, many=True)

    contacts = CvContactReadSerializer(many=True, read_only=True)
    time_slots = CvTimeSlotSerializer(many=True, read_only=True)

    class Meta(CvDetailSerializer.Meta):
        fields = CvDetailSerializer.Meta.fields + [
            'user', 'country', 'city', 'citizenship', 'competencies_ids', 'contacts', 'time_slots'
        ]


class CvListSerializer(CvDetailSerializer):
    class Meta(CvDetailSerializer.Meta):
        fields = [
            k
            for k in CvDetailSerializer.Meta.fields
            if k not in ['contacts', 'time_slots', ]
        ]
