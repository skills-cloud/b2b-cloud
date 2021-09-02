from acc.models import User
from main import models as main_models
from api.fields import PrimaryKeyRelatedIdField
from api.serializers import ModelSerializer
from api.handlers.acc.serializers import UserInlineSerializer


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
