from rest_framework import serializers

from acc.models import User
from main import models as main_models
from dictionary import models as dictionary_models
from api.fields import PrimaryKeyRelatedIdField
from api.serializers import ModelSerializer
from api.handlers.acc.serializers import UserInlineSerializer
from api.handlers.dictionary import serializers as dictionary_serializers
from api.handlers.cv import serializers as cv_serializers

from .organization import OrganizationSerializer, ProjectSerializer


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
    cv_list = cv_serializers.CvInlineSerializer(many=True, read_only=True)

    class Meta(RequestRequirementSerializer.Meta):
        fields = RequestRequirementSerializer.Meta.fields + [
            'position', 'type_of_employment', 'work_location_city',
            'competencies', 'cv_list_ids', 'cv_list',
        ]


class RequestSerializer(ModelSerializer):
    customer_model_field = main_models.Request._meta.get_field('customer')
    type_id = PrimaryKeyRelatedIdField(
        queryset=main_models.RequestType.objects,
        allow_null=True, required=False
    )
    customer_id = PrimaryKeyRelatedIdField(
        queryset=main_models.Organization.objects.filter(**customer_model_field.get_limit_choices_to()),
        help_text=customer_model_field.help_text + '<br>`/api/main/organization/?is_customer=true`'
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
            'description', 'status', 'priority', 'start_date', 'deadline_date',
        ]


class RequestReadSerializer(RequestSerializer):
    type = RequestTypeSerializer(read_only=True)
    customer = OrganizationSerializer(read_only=True)
    industry_sector = dictionary_serializers.IndustrySectorSerializer(read_only=True)
    project = ProjectSerializer(read_only=True)
    resource_manager = UserInlineSerializer(read_only=True)
    recruiter = UserInlineSerializer(read_only=True)

    requirements = RequestRequirementReadSerializer(many=True, read_only=True)

    requirements_count_sum = serializers.SerializerMethodField(read_only=True)

    class Meta(RequestSerializer.Meta):
        fields = RequestSerializer.Meta.fields + [
            'type', 'customer', 'industry_sector', 'project', 'resource_manager', 'recruiter', 'requirements_count_sum',
            'requirements',
        ]

    def get_requirements_count_sum(self, instance: main_models.Request) -> int:
        return sum(row.count or 0 for row in instance.requirements.all()) or 0
