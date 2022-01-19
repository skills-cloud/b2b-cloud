import datetime

from typing import TYPE_CHECKING, Type
from pathlib import Path
from typing import Dict

from django.utils import timezone
from rest_framework import serializers

from acc.models import User
from main import models as main_models
from dictionary import models as dictionary_models
from cv import models as cv_models
from api.fields import PrimaryKeyRelatedIdField
from api.serializers import ModelSerializer, ModelSerializerWithCallCleanMethod
from api.handlers.dictionary import serializers as dictionary_serializers
from api.handlers.acc.serializers import UserInlineSerializer
from api.handlers.main.serializers.organization import OrganizationProjectSerializer

if TYPE_CHECKING:
    from api.handlers.main.serializers.request import RequestRequirementReadSerializer


class FileModelBaseSerializer(ModelSerializerWithCallCleanMethod):
    class Meta:
        fields = ['id', 'file', 'file_name']

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        if 'file_name' not in data:
            data['file_name'] = Path(data['file'].name).stem
        return data


class CvLinkedObjectBaseSerializer(ModelSerializerWithCallCleanMethod):
    cv_id = PrimaryKeyRelatedIdField(queryset=cv_models.CV.objects)

    class Meta:
        fields = ['id', 'cv_id']


########################################################################################################################
# CvContact
########################################################################################################################


class CvContactSerializer(CvLinkedObjectBaseSerializer):
    contact_type_id = PrimaryKeyRelatedIdField(
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
    country_id = PrimaryKeyRelatedIdField(
        queryset=dictionary_models.Country.objects,
        allow_null=True, required=False,
    )
    city_id = PrimaryKeyRelatedIdField(
        queryset=dictionary_models.City.objects,
        allow_null=True, required=False,
    )
    type_of_employment_id = PrimaryKeyRelatedIdField(
        queryset=dictionary_models.TypeOfEmployment.objects
    )

    class Meta(CvLinkedObjectBaseSerializer.Meta):
        model = cv_models.CvTimeSlot
        fields = CvLinkedObjectBaseSerializer.Meta.fields + [
            'date_from', 'date_to', 'price', 'is_work_permit_required', 'description',
            'country_id', 'city_id', 'type_of_employment_id', 'is_free',
        ]


class CvTimeSlotReadSerializer(CvTimeSlotSerializer):
    country = dictionary_serializers.CountrySerializer(read_only=True, allow_null=True)
    city = dictionary_serializers.CitySerializer(read_only=True, allow_null=True)
    type_of_employment = dictionary_serializers.TypeOfEmploymentSerializer(read_only=True, allow_null=True)

    request_requirement_id = serializers.IntegerField(source='request_requirement.id', read_only=True, allow_null=True)
    request_requirement_name = serializers.CharField(source='request_requirement.name', read_only=True, allow_null=True)
    request_id = serializers.IntegerField(source='request.id', read_only=True, allow_null=True)
    request_title = serializers.CharField(source='request.title', read_only=True, allow_null=True)
    organization_project_id = serializers.IntegerField(
        source='organization_project.id', read_only=True, allow_null=True
    )
    organization_project_name = serializers.CharField(
        source='organization_project.name', read_only=True, allow_null=True
    )

    class Meta(CvTimeSlotSerializer.Meta):
        fields = CvTimeSlotSerializer.Meta.fields + [
            'country', 'city', 'type_of_employment', 'kind',

            'request_requirement_id', 'request_requirement_name', 'request_id', 'request_title',
            'organization_project_id', 'organization_project_name',
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


class CvPositionCompetenceSerializer(ModelSerializerWithCallCleanMethod):
    competence_id = PrimaryKeyRelatedIdField(
        queryset=dictionary_models.Competence.objects,
    )
    years = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = cv_models.CvPositionCompetence
        fields = ['cv_position_id', 'competence_id', 'years', ]


class CvPositionCompetenceReplaceSerializer(CvPositionCompetenceSerializer):
    cv_position_id = None
    year_started = serializers.IntegerField(read_only=True)

    class Meta(CvPositionCompetenceSerializer.Meta):
        fields = ['competence_id', 'years', 'year_started']

    def to_internal_value(self, data: Dict):
        if 'year_started' not in data and data.get('years'):
            data['year_started'] = timezone.now().year - data['years']
        return data


class CvPositionCompetenceReadSerializer(CvPositionCompetenceSerializer):
    competence = dictionary_serializers.CompetenceSerializer(read_only=True)

    class Meta(CvPositionCompetenceSerializer.Meta):
        fields = CvPositionCompetenceSerializer.Meta.fields + ['competence']


class CvPositionSerializer(CvLinkedObjectBaseSerializer):
    year_started = serializers.IntegerField(read_only=True)
    years = serializers.IntegerField(required=False, allow_null=True)
    position_id = PrimaryKeyRelatedIdField(
        queryset=dictionary_models.Position.objects,
        required=False, allow_null=True,
    )

    class Meta(CvLinkedObjectBaseSerializer.Meta):
        model = cv_models.CvPosition
        fields = CvLinkedObjectBaseSerializer.Meta.fields + [
            'position_id', 'title', 'years', 'year_started'
        ]

    def to_internal_value(self, data: Dict):
        if 'year_started' not in data and data.get('years', None):
            data['year_started'] = timezone.now().year - data['years']
        if 'years' in data:
            del data['years']
        return data


class CvPositionReadSerializer(CvPositionSerializer):
    position = dictionary_serializers.PositionSerializer(read_only=True)
    files = CvPositionFileReadSerializer(read_only=True, many=True)
    competencies_ids = PrimaryKeyRelatedIdField(
        source='competencies', queryset=cv_models.CvPositionCompetence.objects,
        many=True, allow_null=True, required=False,
    )
    competencies = CvPositionCompetenceReadSerializer(many=True, read_only=True)

    class Meta(CvPositionSerializer.Meta):
        fields = CvPositionSerializer.Meta.fields + [
            'position', 'files', 'competencies_ids', 'competencies',
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
    organization_id = PrimaryKeyRelatedIdField(
        queryset=dictionary_models.Organization.objects
    )
    position_id = PrimaryKeyRelatedIdField(
        queryset=dictionary_models.Position.objects,
        required=False, allow_null=True,
    )
    competencies_ids = PrimaryKeyRelatedIdField(
        source='competencies', queryset=dictionary_models.Competence.objects,
        many=True, required=False, allow_null=True,
    )
    projects_ids = PrimaryKeyRelatedIdField(
        source='projects', queryset=main_models.OrganizationProject.objects,
        many=True, required=False, allow_null=True,
    )

    class Meta(CvLinkedObjectBaseSerializer.Meta):
        model = cv_models.CvCareer
        fields = CvLinkedObjectBaseSerializer.Meta.fields + [
            'date_from', 'date_to', 'description', 'is_verified',
            'organization_id', 'position_id', 'competencies_ids', 'projects_ids'
        ]


class CvCareerReadSerializer(CvCareerSerializer):
    organization = dictionary_serializers.OrganizationSerializer(read_only=True)
    position = dictionary_serializers.PositionSerializer(read_only=True)
    projects = OrganizationProjectSerializer(read_only=True, many=True)
    files = CvCareerFileReadSerializer(read_only=True, many=True)
    competencies = dictionary_serializers.CompetenceInlineSerializer(many=True, read_only=True)

    class Meta(CvCareerSerializer.Meta):
        fields = CvCareerSerializer.Meta.fields + ['organization', 'position', 'projects', 'files', 'competencies']


########################################################################################################################
# CvEducation
########################################################################################################################


class CvProjectSerializer(CvLinkedObjectBaseSerializer):
    organization_id = PrimaryKeyRelatedIdField(
        queryset=dictionary_models.Organization.objects
    )
    position_id = PrimaryKeyRelatedIdField(
        queryset=dictionary_models.Position.objects
    )
    industry_sector_id = PrimaryKeyRelatedIdField(
        queryset=dictionary_models.IndustrySector.objects,
        required=False, allow_null=True,
    )
    competencies_ids = PrimaryKeyRelatedIdField(
        source='competencies', queryset=dictionary_models.Competence.objects,
        many=True, required=False, allow_null=True,
    )

    class Meta(CvLinkedObjectBaseSerializer.Meta):
        model = cv_models.CvProject
        fields = CvLinkedObjectBaseSerializer.Meta.fields + [
            'name', 'date_from', 'date_to', 'description', 'is_verified', 'organization_id', 'position_id',
            'industry_sector_id', 'competencies_ids',
        ]


class CvProjectReadSerializer(CvProjectSerializer):
    organization = dictionary_serializers.OrganizationSerializer(read_only=True)
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
    education_place_id = PrimaryKeyRelatedIdField(
        queryset=dictionary_models.EducationPlace.objects
    )
    education_speciality_id = PrimaryKeyRelatedIdField(
        queryset=dictionary_models.EducationSpecialty.objects
    )
    education_graduate_id = PrimaryKeyRelatedIdField(
        queryset=dictionary_models.EducationGraduate.objects
    )
    competencies_ids = PrimaryKeyRelatedIdField(
        source='competencies', queryset=dictionary_models.Competence.objects,
        many=True, required=False, allow_null=True,
    )

    class Meta(CvLinkedObjectBaseSerializer.Meta):
        model = cv_models.CvEducation
        fields = CvLinkedObjectBaseSerializer.Meta.fields + [
            'date_from', 'date_to', 'diploma_number', 'description', 'is_verified', 'education_place_id',
            'education_speciality_id', 'education_graduate_id', 'competencies_ids',
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
    education_place_id = PrimaryKeyRelatedIdField(
        queryset=dictionary_models.EducationPlace.objects
    )
    education_speciality_id = PrimaryKeyRelatedIdField(
        queryset=dictionary_models.EducationSpecialty.objects
    )
    education_graduate_id = PrimaryKeyRelatedIdField(
        queryset=dictionary_models.EducationGraduate.objects
    )
    competencies_ids = PrimaryKeyRelatedIdField(
        source='competencies', queryset=dictionary_models.Competence.objects,
        many=True, required=False, allow_null=True,
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


class CvDetailWriteSerializer(ModelSerializerWithCallCleanMethod):
    organization_contractor_id = PrimaryKeyRelatedIdField(
        queryset=main_models.OrganizationContractor.objects,
    )
    manager_rm_id = PrimaryKeyRelatedIdField(
        queryset=User.objects, allow_null=True, required=False,
    )
    user_id = PrimaryKeyRelatedIdField(
        queryset=User.objects,
        allow_null=True, required=False,
    )
    country_id = PrimaryKeyRelatedIdField(
        queryset=dictionary_models.Country.objects,
        allow_null=True, required=False,
    )
    city_id = PrimaryKeyRelatedIdField(
        queryset=dictionary_models.City.objects,
        allow_null=True, required=False,
    )
    citizenship_id = PrimaryKeyRelatedIdField(
        queryset=dictionary_models.Citizenship.objects,
        allow_null=True, required=False,
    )
    physical_limitations_ids = PrimaryKeyRelatedIdField(
        source='physical_limitations', queryset=dictionary_models.PhysicalLimitation.objects,
        many=True, required=False, allow_null=True,
    )
    types_of_employment_ids = PrimaryKeyRelatedIdField(
        source='types_of_employment', queryset=dictionary_models.PhysicalLimitation.objects,
        many=True, required=False, allow_null=True,
    )
    linked_ids = PrimaryKeyRelatedIdField(
        source='linked', queryset=cv_models.CV.objects,
        many=True, required=False, allow_null=True,
    )

    class Meta:
        model = cv_models.CV
        fields = [
            'id', 'organization_contractor_id', 'manager_rm_id', 'first_name', 'middle_name', 'last_name', 'photo',
            'gender', 'birth_date', 'user_id', 'country_id', 'city_id', 'citizenship_id', 'days_to_contact',
            'time_to_contact_from', 'time_to_contact_to', 'price', 'physical_limitations_ids',
            'types_of_employment_ids', 'linked_ids',
        ]


class CvDetailReadBaseSerializer(CvDetailWriteSerializer):
    pass


class CvDetailReadFullSerializer(CvDetailReadBaseSerializer):
    manager_rm = UserInlineSerializer(read_only=True, allow_null=True)
    user = UserInlineSerializer(read_only=True, allow_null=True)
    country = dictionary_serializers.CountrySerializer(read_only=True, allow_null=True)
    city = dictionary_serializers.CitySerializer(read_only=True, allow_null=True)
    citizenship = dictionary_serializers.CitizenshipSerializer(read_only=True, allow_null=True)

    physical_limitations = dictionary_serializers.PhysicalLimitationSerializer(many=True, read_only=True)
    types_of_employment = dictionary_serializers.TypeOfEmploymentSerializer(many=True, read_only=True)

    contacts = CvContactReadSerializer(many=True, read_only=True)
    time_slots = CvTimeSlotReadSerializer(many=True, read_only=True)
    positions = CvPositionReadSerializer(many=True, read_only=True)
    career = CvCareerReadSerializer(many=True, read_only=True)
    projects = CvProjectReadSerializer(many=True, read_only=True)
    education = CvEducationReadSerializer(many=True, read_only=True)
    certificates = CvCertificateReadSerializer(many=True, read_only=True)
    files = CvFileReadSerializer(many=True, read_only=True)

    rating = serializers.IntegerField(source='info.rating', allow_null=True)

    class Meta(CvDetailReadBaseSerializer.Meta):
        fields = CvDetailReadBaseSerializer.Meta.fields + [
            'manager_rm', 'user', 'country', 'city', 'citizenship', 'physical_limitations', 'types_of_employment',
            'contacts', 'time_slots', 'positions', 'career', 'projects', 'education', 'certificates', 'files',
            'rating',
        ]

    def get_fields(self):
        fields = super().get_fields()
        fields['requests_requirements'] = self.get_requests_requirements_serializer_class()(many=True, read_only=True)
        return fields

    def to_representation(self, instance: cv_models.CV):
        result = super().to_representation(instance)
        result['requests_requirements'] = self.get_requests_requirements_serializer_class()(
            [
                row.request_requirement
                for row in instance.requests_requirements_links.all()
            ],
            many=True, read_only=True
        ).data
        return result

    @classmethod
    def get_requests_requirements_serializer_class(cls) -> Type['RequestRequirementReadSerializer']:
        from api.handlers.main.serializers.request import RequestReadSerializer, RequestRequirementReadSerializer

        class CvRequestInlineSerializer(RequestReadSerializer):
            class Meta(RequestReadSerializer.Meta):
                ref_name = 'CvRequestInlineSerializer'
                fields = [
                    f
                    for f in RequestReadSerializer.Meta.fields
                    if f not in ['requirements', 'requirements_count_sum']
                ]

        class CvRequestRequirementInlineSerializer(RequestRequirementReadSerializer):
            request = CvRequestInlineSerializer(read_only=True)

            class Meta(RequestRequirementReadSerializer.Meta):
                ref_name = 'CvRequestRequirementInlineSerializer'
                fields = [
                    *[
                        f
                        for f in RequestRequirementReadSerializer.Meta.fields
                        if f not in ['cv_list_ids', 'cv_list']
                    ],
                    'request'
                ]

        return CvRequestRequirementInlineSerializer


class CvListReadFullSerializer(CvDetailReadFullSerializer):
    pass


class CvInlineFullSerializer(CvListReadFullSerializer):
    pass


class CvInlineShortSerializer(CvDetailReadBaseSerializer):
    physical_limitations_ids = None
    types_of_employment_ids = None
    linked_ids = None

    class Meta(CvDetailReadBaseSerializer.Meta):
        fields = [
            f for f in CvDetailReadBaseSerializer.Meta.fields if f not in [
                'physical_limitations_ids', 'types_of_employment_ids', 'linked_ids',
            ]
        ]
