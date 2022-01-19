from rest_framework import serializers

from acc.models import User
from main import models as main_models
from dictionary import models as dictionary_models
from api.fields import PrimaryKeyRelatedIdField
from api.serializers import ModelSerializerWithCallCleanMethod, ModelSerializer
from api.handlers.acc.serializers import UserInlineSerializer
from api.handlers.dictionary import serializers as dictionary_serializers
from api.handlers.cv.serializers import CvInlineShortSerializer
from api.handlers.main.serializers.module import ModuleInlineSerializer

__all__ = [
    'RequestTypeSerializer',
    'RequestRequirementCompetenceSerializer',
    'RequestRequirementCompetenceReplaceSerializer',
    'RequestRequirementCompetenceReadSerializer',
    'RequestRequirementCvWriteDetailsSerializer',
    'RequestRequirementCvSerializer',
    'RequestRequirementCvReadSerializer',
    'RequestRequirementSerializer',
    'RequestRequirementReadSerializer',
    'RequestRequirementInlineSerializer',
    'RequestSerializer',
    'RequestReadSerializer',
    'RequestInlineSerializer',
]


class RequestTypeSerializer(ModelSerializerWithCallCleanMethod):
    class Meta:
        model = main_models.RequestType
        fields = '__all__'


class RequestRequirementCompetenceSerializer(ModelSerializerWithCallCleanMethod):
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


class RequestRequirementCvWriteDetailsSerializer(ModelSerializer):
    class RequestRequirementCvOrganizationProjectCardItem(serializers.Serializer):
        id = PrimaryKeyRelatedIdField(queryset=main_models.OrganizationProjectCardItem.objects.all())
        date = serializers.DateField(required=False, allow_null=True)

    organization_project_card_items = RequestRequirementCvOrganizationProjectCardItem(many=True, required=False)

    class Meta:
        model = main_models.RequestRequirementCv
        fields = [
            'status', 'date_from', 'date_to', 'rating',
            'organization_project_card_items'
        ]


class RequestRequirementCvSerializer(RequestRequirementCvWriteDetailsSerializer):
    class Meta(RequestRequirementCvWriteDetailsSerializer.Meta):
        fields = RequestRequirementCvWriteDetailsSerializer.Meta.fields + [
            'id', 'request_requirement_id', 'cv_id', 'created_at', 'updated_at'
        ]


class RequestRequirementCvReadSerializer(RequestRequirementCvSerializer):
    cv = CvInlineShortSerializer(read_only=True)

    class Meta(RequestRequirementCvSerializer.Meta):
        fields = RequestRequirementCvSerializer.Meta.fields + ['cv']


class RequestRequirementSerializer(ModelSerializerWithCallCleanMethod):
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
            'date_from', 'date_to',
        ]


class RequestRequirementReadSerializer(RequestRequirementSerializer):
    position = dictionary_serializers.PositionSerializer(read_only=True)
    type_of_employment = dictionary_serializers.TypeOfEmploymentSerializer(read_only=True)
    work_location_city = dictionary_serializers.CitySerializer(read_only=True)

    competencies = RequestRequirementCompetenceReadSerializer(many=True, read_only=True)

    cv_list_ids = serializers.ListField(read_only=True)
    cv_list = RequestRequirementCvReadSerializer(source='cv_links', many=True, read_only=True)

    class Meta(RequestRequirementSerializer.Meta):
        fields = RequestRequirementSerializer.Meta.fields + [
            'position', 'type_of_employment', 'work_location_city',
            'competencies',
            'cv_list_ids', 'cv_list',
        ]


class RequestRequirementInlineSerializer(RequestRequirementSerializer):
    class Meta(RequestRequirementSerializer.Meta):
        fields = RequestRequirementSerializer.Meta.fields


class RequestSerializer(ModelSerializerWithCallCleanMethod):
    type_id = PrimaryKeyRelatedIdField(
        queryset=main_models.RequestType.objects, allow_null=True, required=False,
        label=main_models.Request._meta.get_field('type').verbose_name,
    )
    industry_sector_id = PrimaryKeyRelatedIdField(
        queryset=dictionary_models.IndustrySector.objects, allow_null=True, required=False,
        label=main_models.Request._meta.get_field('industry_sector').verbose_name,
    )
    module_id = PrimaryKeyRelatedIdField(
        queryset=main_models.Module.objects,
        label=main_models.Request._meta.get_field('module').verbose_name,
    )
    manager_rm_id = PrimaryKeyRelatedIdField(
        queryset=User.objects, allow_null=True, required=False,
        label=main_models.Request._meta.get_field('manager_rm').verbose_name,
    )

    class Meta:
        model = main_models.Request
        fields = [
            'id', 'module_id', 'type_id', 'industry_sector_id',
            'manager_rm_id', 'title', 'description', 'status', 'priority', 'start_date', 'deadline_date',
        ]


class RequestReadSerializer(RequestSerializer):
    module = ModuleInlineSerializer(read_only=True)
    type = RequestTypeSerializer(read_only=True, allow_null=True)
    industry_sector = dictionary_serializers.IndustrySectorSerializer(read_only=True, allow_null=True)
    manager_rm = UserInlineSerializer(read_only=True, allow_null=True)

    requirements = RequestRequirementReadSerializer(many=True, read_only=True)

    requirements_count_sum = serializers.SerializerMethodField(read_only=True)

    class Meta(RequestSerializer.Meta):
        fields = RequestSerializer.Meta.fields + [
            'module', 'type', 'industry_sector', 'manager_rm', 'requirements_count_sum', 'requirements',
        ]

    def get_requirements_count_sum(self, instance: main_models.Request) -> int:
        return sum(row.count or 0 for row in instance.requirements.all()) or 0


class RequestInlineSerializer(RequestReadSerializer):
    class Meta(RequestReadSerializer.Meta):
        fields = [f for f in RequestReadSerializer.Meta.fields if f not in [
            'type', 'industry_sector',
            'resource_manager', 'recruiter', 'requirements',
            'requirements_count_sum',
        ]]
