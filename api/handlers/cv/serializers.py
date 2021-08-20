from pathlib import Path
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


class FileModelBaseSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'file', 'file_name']

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        if 'file_name' not in data:
            data['file_name'] = Path(data['file'].name).stem
        return data


class CvLinkedObjectBaseSerializer(ModelSerializer):
    cv_id = serializers.PrimaryKeyRelatedIdField(
        queryset=cv_models.CV.objects
    )

    class Meta:
        fields = ['id', 'cv_id']


########################################################################################################################
# CvContact
########################################################################################################################


class CvContactSerializer(CvLinkedObjectBaseSerializer):
    contact_type_id = serializers.PrimaryKeyRelatedIdField(
        queryset=dictionary_models.ContactType.objects
    )

    class Meta(CvLinkedObjectBaseSerializer.Meta):
        model = cv_models.CvContact
        fields = CvLinkedObjectBaseSerializer.Meta.fields + [
            'contact_type_id', 'value', 'is_primary', 'comment',
        ]


class CvContactReadSerializer(CvContactSerializer):
    contact_type = dictionary_serializers.ContactTypeSerializer(read_only=True)

    class Meta(CvContactSerializer.Meta):
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

    class Meta(CvLinkedObjectBaseSerializer.Meta):
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


class CvPositionFileSerializer(FileModelBaseSerializer):
    class Meta:
        model = cv_models.CvPositionFile
        fields = FileModelBaseSerializer.Meta.fields + ['cv_position_id']


class CvPositionFileReadSerializer(CvPositionFileSerializer):
    class Meta(CvPositionFileSerializer.Meta):
        fields = CvPositionFileSerializer.Meta.fields + ['file_name', 'file_ext', 'file_size']


class CvPositionSerializer(CvLinkedObjectBaseSerializer):
    position_id = serializers.PrimaryKeyRelatedIdField(
        queryset=dictionary_models.Position.objects
    )
    competencies_ids = serializers.PrimaryKeyRelatedIdField(
        source='competencies', required=False, many=True,
        queryset=dictionary_models.Competence.objects,
    )

    class Meta(CvLinkedObjectBaseSerializer.Meta):
        model = cv_models.CvPosition
        fields = CvLinkedObjectBaseSerializer.Meta.fields + [
            'position_id', 'competencies_ids', 'title',
        ]


class CvPositionReadSerializer(CvPositionSerializer):
    position = dictionary_serializers.PositionSerializer(read_only=True)
    files = CvPositionFileReadSerializer(read_only=True, many=True)
    competencies = dictionary_serializers.CompetenceInlineSerializer(many=True, read_only=True)

    class Meta(CvPositionSerializer.Meta):
        fields = CvPositionSerializer.Meta.fields + [
            'position', 'files', 'competencies',
        ]


########################################################################################################################
# CvCareer
########################################################################################################################


class CvCareerFileSerializer(FileModelBaseSerializer):
    class Meta:
        model = cv_models.CvCareerFile
        fields = FileModelBaseSerializer.Meta.fields + ['cv_career_id']


class CvCareerFileReadSerializer(CvCareerFileSerializer):
    class Meta(CvCareerFileSerializer.Meta):
        fields = CvCareerFileSerializer.Meta.fields + ['file_name', 'file_ext', 'file_size']


class CvCareerSerializer(CvLinkedObjectBaseSerializer):
    organization_id = serializers.PrimaryKeyRelatedIdField(
        queryset=main_models.Organization.objects
    )
    position_id = serializers.PrimaryKeyRelatedIdField(
        queryset=dictionary_models.Position.objects
    )
    competencies_ids = serializers.PrimaryKeyRelatedIdField(
        source='competencies', required=False, many=True,
        queryset=dictionary_models.Competence.objects,
    )
    projects_ids = serializers.PrimaryKeyRelatedIdField(
        source='projects', required=False, many=True,
        queryset=main_models.OrganizationProject.objects,
    )

    class Meta(CvLinkedObjectBaseSerializer.Meta):
        model = cv_models.CvCareer
        fields = CvLinkedObjectBaseSerializer.Meta.fields + [
            'date_from', 'date_to', 'description', 'is_verified',
            'organization_id', 'position_id', 'competencies_ids', 'projects_ids'
        ]


class CvCareerReadSerializer(CvCareerSerializer):
    organization = main_serializers.OrganizationSerializer(read_only=True)
    position = dictionary_serializers.PositionSerializer(read_only=True)
    projects = main_serializers.OrganizationProjectSerializer(read_only=True, many=True)
    files = CvCareerFileReadSerializer(read_only=True, many=True)
    competencies = dictionary_serializers.CompetenceInlineSerializer(many=True, read_only=True)

    class Meta(CvCareerSerializer.Meta):
        fields = CvCareerSerializer.Meta.fields + ['organization', 'position', 'projects', 'files', 'competencies']


########################################################################################################################
# CvEducation
########################################################################################################################


class CvProjectSerializer(CvLinkedObjectBaseSerializer):
    organization_id = serializers.PrimaryKeyRelatedIdField(
        queryset=main_models.Organization.objects
    )
    position_id = serializers.PrimaryKeyRelatedIdField(
        queryset=dictionary_models.Position.objects
    )
    industry_sector_id = serializers.PrimaryKeyRelatedIdField(
        queryset=dictionary_models.IndustrySector.objects, required=False
    )
    competencies_ids = serializers.PrimaryKeyRelatedIdField(
        source='competencies', required=False, many=True,
        queryset=dictionary_models.Competence.objects,
    )

    class Meta(CvLinkedObjectBaseSerializer.Meta):
        model = cv_models.CvProject
        fields = CvLinkedObjectBaseSerializer.Meta.fields + [
            'name', 'date_from', 'date_to', 'description', 'is_verified', 'organization_id', 'position_id',
            'industry_sector_id', 'competencies_ids',
        ]


class CvProjectReadSerializer(CvProjectSerializer):
    organization = main_serializers.OrganizationSerializer(read_only=True)
    position = dictionary_serializers.PositionSerializer(read_only=True)
    industry_sector = dictionary_serializers.IndustrySectorSerializer(read_only=True)
    competencies = dictionary_serializers.CompetenceInlineSerializer(many=True, read_only=True)

    class Meta(CvProjectSerializer.Meta):
        fields = CvProjectSerializer.Meta.fields + [
            'organization', 'position', 'industry_sector', 'competencies',
        ]


########################################################################################################################
# CvEducation
########################################################################################################################


class CvEducationSerializer(CvLinkedObjectBaseSerializer):
    education_place_id = serializers.PrimaryKeyRelatedIdField(
        queryset=dictionary_models.EducationPlace.objects
    )
    education_speciality_id = serializers.PrimaryKeyRelatedIdField(
        queryset=dictionary_models.EducationSpecialty.objects
    )
    education_graduate_id = serializers.PrimaryKeyRelatedIdField(
        queryset=dictionary_models.EducationGraduate.objects
    )
    competencies_ids = serializers.PrimaryKeyRelatedIdField(
        source='competencies', required=False, many=True,
        queryset=dictionary_models.Competence.objects,

    )

    class Meta(CvLinkedObjectBaseSerializer.Meta):
        model = cv_models.CvEducation
        fields = CvLinkedObjectBaseSerializer.Meta.fields + [
            'date_from', 'date_to', 'description', 'is_verified', 'education_place_id', 'education_speciality_id',
            'education_graduate_id', 'competencies_ids',
        ]


class CvEducationReadSerializer(CvEducationSerializer):
    education_place = dictionary_serializers.EducationPlaceSerializer(read_only=True, allow_null=True)
    education_speciality = dictionary_serializers.EducationSpecialtySerializer(read_only=True, allow_null=True)
    education_graduate = dictionary_serializers.EducationGraduateSerializer(read_only=True, allow_null=True)
    competencies = dictionary_serializers.CompetenceInlineSerializer(many=True, read_only=True)

    class Meta(CvEducationSerializer.Meta):
        fields = CvEducationSerializer.Meta.fields + [
            'education_place', 'education_speciality', 'education_graduate', 'competencies',
        ]


########################################################################################################################
# CvEducation
########################################################################################################################


class CvCertificateSerializer(CvLinkedObjectBaseSerializer):
    education_place_id = serializers.PrimaryKeyRelatedIdField(
        queryset=dictionary_models.EducationPlace.objects
    )
    education_speciality_id = serializers.PrimaryKeyRelatedIdField(
        queryset=dictionary_models.EducationSpecialty.objects
    )
    education_graduate_id = serializers.PrimaryKeyRelatedIdField(
        queryset=dictionary_models.EducationGraduate.objects
    )
    competencies_ids = serializers.PrimaryKeyRelatedIdField(
        source='competencies', required=False, many=True,
        queryset=dictionary_models.Competence.objects,
    )

    class Meta(CvLinkedObjectBaseSerializer.Meta):
        model = cv_models.CvCertificate
        fields = CvLinkedObjectBaseSerializer.Meta.fields + [
            'date', 'name', 'number', 'description', 'is_verified', 'education_place_id', 'education_speciality_id',
            'education_graduate_id', 'competencies_ids',
        ]


class CvCertificateReadSerializer(CvCertificateSerializer):
    education_place = dictionary_serializers.EducationPlaceSerializer(read_only=True, allow_null=True)
    education_speciality = dictionary_serializers.EducationSpecialtySerializer(read_only=True, allow_null=True)
    education_graduate = dictionary_serializers.EducationGraduateSerializer(read_only=True, allow_null=True)
    competencies = dictionary_serializers.CompetenceInlineSerializer(many=True, read_only=True)

    class Meta(CvCertificateSerializer.Meta):
        fields = CvCertificateSerializer.Meta.fields + [
            'education_place', 'education_speciality', 'education_graduate', 'competencies',
        ]


########################################################################################################################
# CvFile
########################################################################################################################


class CvFileSerializer(FileModelBaseSerializer):
    class Meta:
        model = cv_models.CvFile
        fields = FileModelBaseSerializer.Meta.fields + ['cv_id']


class CvFileReadSerializer(CvFileSerializer):
    class Meta(CvFileSerializer.Meta):
        fields = CvFileSerializer.Meta.fields + ['file_name', 'file_ext', 'file_size']


########################################################################################################################
# CV
########################################################################################################################

class CvSetPhotoSerializer(ModelSerializer):
    class Meta:
        model = cv_models.CV
        fields = ['id', 'photo']


class CvDetailWriteSerializer(ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedIdField(queryset=User.objects, allow_null=True, required=False)
    country_id = serializers.PrimaryKeyRelatedIdField(
        queryset=dictionary_models.Country.objects, allow_null=True, required=False
    )
    city_id = serializers.PrimaryKeyRelatedIdField(
        queryset=dictionary_models.City.objects, allow_null=True, required=False
    )
    citizenship_id = serializers.PrimaryKeyRelatedIdField(
        queryset=dictionary_models.Citizenship.objects, allow_null=True, required=False
    )
    physical_limitations_ids = serializers.PrimaryKeyRelatedIdField(
        source='physical_limitations', required=False, many=True,
        queryset=dictionary_models.PhysicalLimitation.objects,
    )
    competencies_ids = serializers.PrimaryKeyRelatedIdField(
        source='competencies', required=False, many=True,
        queryset=dictionary_models.Competence.objects,
    )

    class Meta:
        model = cv_models.CV
        fields = [
            'id', 'first_name', 'middle_name', 'last_name', 'photo', 'gender', 'birth_date', 'is_resource_owner',
            'user_id', 'country_id', 'city_id', 'citizenship_id',
            'days_to_contact', 'time_to_contact_from', 'time_to_contact_to',
            'physical_limitations_ids', 'competencies_ids',
        ]


class CvDetailReadSerializer(CvDetailWriteSerializer):
    user = UserInlineSerializer(read_only=True, allow_null=True)
    country = dictionary_serializers.CountrySerializer(read_only=True, allow_null=True)
    city = dictionary_serializers.CitySerializer(read_only=True, allow_null=True)
    citizenship = dictionary_serializers.CitizenshipSerializer(read_only=True, allow_null=True)

    physical_limitations = dictionary_serializers.PhysicalLimitationSerializer(many=True, read_only=True)
    competencies = dictionary_serializers.CompetenceInlineSerializer(many=True, read_only=True)

    contacts = CvContactReadSerializer(many=True, read_only=True)
    time_slots = CvTimeSlotReadSerializer(many=True, read_only=True)
    positions = CvPositionReadSerializer(many=True, read_only=True)
    career = CvCareerReadSerializer(many=True, read_only=True)
    projects = CvProjectReadSerializer(many=True, read_only=True)
    education = CvEducationReadSerializer(many=True, read_only=True)
    certificates = CvCertificateReadSerializer(many=True, read_only=True)
    files = CvFileReadSerializer(many=True, read_only=True)

    class Meta(CvDetailWriteSerializer.Meta):
        fields = CvDetailWriteSerializer.Meta.fields + [
            'user', 'country', 'city', 'citizenship', 'physical_limitations', 'contacts', 'time_slots', 'positions',
            'career', 'projects', 'education', 'certificates', 'files', 'competencies',
        ]


class CvListSerializer(CvDetailReadSerializer):
    class Meta(CvDetailReadSerializer.Meta):
        fields = [
            k
            for k in CvDetailReadSerializer.Meta.fields
            if k not in [
                # 'contacts', 'time_slots', 'positions', 'career', 'education', 'certificates'
            ]
        ]
