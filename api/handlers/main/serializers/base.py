from acc.models import User
from main import models as main_models
from api.fields import PrimaryKeyRelatedIdField
from api.serializers import ModelSerializer
from api.handlers.acc.serializers import UserInlineSerializer

__all__ = [
    'ProjectSerializer',
    'ProjectReadSerializer',
    'ProjectInlineSerializer',
]


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


class ProjectInlineSerializer(ProjectReadSerializer):
    pass
