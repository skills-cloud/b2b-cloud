from rest_framework import serializers

from acc.models import User
from main import models as main_models
from dictionary import models as dictionary_models
from api.fields import PrimaryKeyRelatedIdField
from api.serializers import ModelSerializer
from api.handlers.acc.serializers import UserInlineSerializer
from api.handlers.dictionary import serializers as dictionary_serializers


class OrganizationSerializer(ModelSerializer):
    class Meta:
        model = main_models.Organization
        exclude = ['created_at', 'updated_at']


class OrganizationProjectSerializer(ModelSerializer):
    organization_id = PrimaryKeyRelatedIdField(
        queryset=main_models.Organization.objects
    )

    class Meta:
        model = main_models.OrganizationProject
        fields = ['id', 'organization_id', 'name', 'description', 'created_at', 'updated_at']


class OrganizationProjectReadSerializer(OrganizationProjectSerializer):
    organization = OrganizationSerializer()

    class Meta(OrganizationProjectSerializer.Meta):
        fields = OrganizationProjectSerializer.Meta.fields + ['organization']


class ProjectSerializer(ModelSerializer):
    resource_managers_ids = PrimaryKeyRelatedIdField(
        source='resource_managers', queryset=User.objects,
        many=True, allow_null=True, required=False,
    )
    recruiters_ids = PrimaryKeyRelatedIdField(
        source='recruiters', queryset=User.objects,
        many=True, allow_null=True, required=False,
    )

    class Meta:
        model = main_models.Project
        fields = ['id', 'name', 'description', 'resource_managers_ids', 'recruiters_ids', 'created_at', 'updated_at']


class ProjectReadSerializer(ProjectSerializer):
    resource_managers = UserInlineSerializer(many=True, read_only=True)
    recruiters = UserInlineSerializer(many=True, read_only=True)

    class Meta(ProjectSerializer.Meta):
        fields = ProjectSerializer.Meta.fields + ['resource_managers', 'recruiters']


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

    class Meta(RequestRequirementSerializer.Meta):
        fields = RequestRequirementSerializer.Meta.fields + [
            'position', 'type_of_employment', 'work_location_city',
            'competencies',
        ]


class RequestSerializer(ModelSerializer):
    type_id = PrimaryKeyRelatedIdField(
        queryset=main_models.RequestType.objects,
        allow_null=True, required=False
    )
    customer_id = PrimaryKeyRelatedIdField(
        queryset=main_models.Organization.objects,
    )
    industry_sector_id = PrimaryKeyRelatedIdField(
        queryset=dictionary_models.IndustrySector.objects,
        allow_null=True, required=False
    )
    project_id = PrimaryKeyRelatedIdField(
        queryset=main_models.Project.objects,
        allow_null=True, required=False
    )
    resource_manager_id = PrimaryKeyRelatedIdField(
        queryset=User.objects,
        allow_null=True, required=False
    )
    recruiter_id = PrimaryKeyRelatedIdField(
        queryset=User.objects,
        allow_null=True, required=False
    )

    class Meta:
        model = main_models.Request
        fields = [
            'id', 'type_id', 'customer_id', 'industry_sector_id', 'project_id', 'resource_manager_id', 'recruiter_id',
            'description', 'status', 'priority', 'deadline_date',
        ]


class RequestReadSerializer(RequestSerializer):
    type = RequestTypeSerializer(read_only=True)
    customer = OrganizationSerializer(read_only=True)
    industry_sector = dictionary_serializers.IndustrySectorSerializer(read_only=True)
    project = ProjectSerializer(read_only=True)
    resource_manager = UserInlineSerializer(read_only=True)
    recruiter = UserInlineSerializer(read_only=True)

    requirements = RequestRequirementReadSerializer(many=True, read_only=True)

    class Meta(RequestSerializer.Meta):
        fields = RequestSerializer.Meta.fields + [
            'type', 'customer', 'industry_sector', 'project', 'resource_manager', 'recruiter', 'requirements'
        ]
