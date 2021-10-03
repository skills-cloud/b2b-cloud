from rest_framework import serializers

from acc.models import User
from main import models as main_models
from dictionary import models as dictionary_models
from api.fields import PrimaryKeyRelatedIdField
from api.serializers import ModelSerializer
from api.handlers.acc.serializers import UserInlineSerializer
from api.handlers.dictionary import serializers as dictionary_serializers
from api.handlers.cv.serializers import CvInlineShortSerializer
from api.handlers.main.serializers.organization import OrganizationProjectInlineSerializer
from api.handlers.main.serializers.base import ProjectInlineSerializer

__all__ = [
    'RequestTypeSerializer',
    'RequestRequirementCompetenceSerializer',
    'RequestRequirementCompetenceReplaceSerializer',
    'RequestRequirementCompetenceReadSerializer',
    'RequestRequirementSerializer',
    'RequestRequirementReadSerializer',
    'RequestRequirementInlineSerializer',
    'RequestSerializer',
    'RequestReadSerializer',
    'RequestInlineSerializer',
]


class RequestTypeSerializer(ModelSerializer):
    class Meta:
        model = main_models.RequestType
        fields = '__all__'


class RequestRequirementCompetenceSerializer(ModelSerializer):
    competence_id = PrimaryKeyRelatedIdField(
        queryset=dictionary_models.Competence.objects
    )

    class Meta:
        model = main_models.RequestRequirementCompetence
        fields = ['id', 'request_requirement_id', 'competence_id', 'experience_years', 'sorting']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['experience_years'].help_text = '\n'.join(
            f'`{k}` : *{v}*'
            for k, v in self.fields['experience_years'].choices.items()
        )


class RequestRequirementCompetenceReplaceSerializer(RequestRequirementCompetenceSerializer):
    request_requirement_id = None

    class Meta(RequestRequirementCompetenceSerializer.Meta):
        fields = [k for k in RequestRequirementCompetenceSerializer.Meta.fields if k not in ['request_requirement_id']]


class RequestRequirementCompetenceReadSerializer(RequestRequirementCompetenceSerializer):
    competence = dictionary_serializers.CompetenceSerializer(read_only=True)

    class Meta(RequestRequirementCompetenceSerializer.Meta):
        fields = RequestRequirementCompetenceSerializer.Meta.fields + ['competence']


class RequestRequirementSerializer(ModelSerializer):
    request_id = PrimaryKeyRelatedIdField(
        queryset=main_models.Request.objects,
    )
    position_id = PrimaryKeyRelatedIdField(
        queryset=dictionary_models.Position.objects,
        allow_null=True, required=False
    )
    type_of_employment_id = PrimaryKeyRelatedIdField(
        queryset=dictionary_models.TypeOfEmployment.objects,
        allow_null=True, required=False
    )
    work_location_city_id = PrimaryKeyRelatedIdField(
        queryset=dictionary_models.City.objects,
        allow_null=True, required=False
    )

    class Meta:
        model = main_models.RequestRequirement
        fields = [
            'id', 'request_id', 'position_id', 'type_of_employment_id', 'work_location_city_id',
            'sorting', 'name', 'description', 'experience_years', 'count', 'work_location_address', 'max_price',
        ]


class RequestRequirementReadSerializer(RequestRequirementSerializer):
    position = dictionary_serializers.PositionSerializer(read_only=True)
    type_of_employment = dictionary_serializers.TypeOfEmploymentSerializer(read_only=True)
    work_location_city = dictionary_serializers.CitySerializer(read_only=True)

    competencies = RequestRequirementCompetenceReadSerializer(many=True, read_only=True)

    cv_list_ids = PrimaryKeyRelatedIdField(source='cv_list', many=True, read_only=True)
    cv_list = CvInlineShortSerializer(many=True, read_only=True)

    class Meta(RequestRequirementSerializer.Meta):
        fields = RequestRequirementSerializer.Meta.fields + [
            'position', 'type_of_employment', 'work_location_city',
            'competencies', 'cv_list_ids', 'cv_list',
        ]


class RequestRequirementInlineSerializer(RequestRequirementSerializer):
    class Meta(RequestRequirementSerializer.Meta):
        fields = RequestRequirementSerializer.Meta.fields


class RequestSerializer(ModelSerializer):
    type_id = PrimaryKeyRelatedIdField(
        queryset=main_models.RequestType.objects, allow_null=True, required=False,
        label=main_models.Request._meta.get_field('type').verbose_name,
    )
    industry_sector_id = PrimaryKeyRelatedIdField(
        queryset=dictionary_models.IndustrySector.objects, allow_null=True, required=False,
        label=main_models.Request._meta.get_field('industry_sector').verbose_name,
    )
    organization_project_id = PrimaryKeyRelatedIdField(
        queryset=main_models.OrganizationProject.objects,
        label=main_models.Request._meta.get_field('organization_project').verbose_name,
    )
    project_id = PrimaryKeyRelatedIdField(
        queryset=main_models.Project.objects, allow_null=True, required=False,
        label=main_models.Request._meta.get_field('project').verbose_name,
        help_text=main_models.Request._meta.get_field('project').help_text,
    )
    manager_id = PrimaryKeyRelatedIdField(
        queryset=User.objects, allow_null=True, required=False,
        label=main_models.Request._meta.get_field('manager').verbose_name,
    )
    resource_manager_id = PrimaryKeyRelatedIdField(
        queryset=User.objects, allow_null=True, required=False,
        label=main_models.Request._meta.get_field('resource_manager').verbose_name,
    )
    recruiter_id = PrimaryKeyRelatedIdField(
        queryset=User.objects, allow_null=True, required=False,
        label=main_models.Request._meta.get_field('recruiter').verbose_name,
    )

    class Meta:
        model = main_models.Request
        fields = [
            'id', 'organization_project_id', 'type_id', 'industry_sector_id', 'project_id',
            'manager_id', 'resource_manager_id', 'recruiter_id', 'title', 'description', 'status', 'priority',
            'start_date', 'deadline_date',
        ]


class RequestReadSerializer(RequestSerializer):
    organization_project = OrganizationProjectInlineSerializer(read_only=True)
    type = RequestTypeSerializer(read_only=True, allow_null=True)
    industry_sector = dictionary_serializers.IndustrySectorSerializer(read_only=True, allow_null=True)
    project = ProjectInlineSerializer(read_only=True, allow_null=True)
    resource_manager = UserInlineSerializer(read_only=True, allow_null=True)
    recruiter = UserInlineSerializer(read_only=True, allow_null=True)

    requirements = RequestRequirementReadSerializer(many=True, read_only=True)

    requirements_count_sum = serializers.SerializerMethodField(read_only=True)

    class Meta(RequestSerializer.Meta):
        fields = RequestSerializer.Meta.fields + [
            'organization_project', 'type', 'industry_sector', 'project', 'resource_manager', 'recruiter',
            'requirements_count_sum', 'requirements',
        ]

    def get_requirements_count_sum(self, instance: main_models.Request) -> int:
        return sum(row.count or 0 for row in instance.requirements.all()) or 0


class RequestInlineSerializer(RequestSerializer):
    class Meta(RequestSerializer.Meta):
        fields = RequestSerializer.Meta.fields
