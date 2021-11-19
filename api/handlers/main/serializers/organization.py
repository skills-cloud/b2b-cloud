from rest_framework import serializers
from rest_framework.relations import RelatedField
from rest_framework_recursive.fields import RecursiveField

from acc.models import User
from dictionary import models as dictionary_models
from main import models as main_models
from api.fields import PrimaryKeyRelatedIdField
from api.serializers import ModelSerializer, ModelSerializerWithCallCleanMethod
from api.handlers.acc.serializers import UserInlineSerializer
from api.handlers.dictionary import serializers as dictionary_serializers

__all__ = [
    'OrganizationSerializer',
    'OrganizationProjectSerializer',
    'OrganizationProjectReadSerializer',
    'OrganizationProjectInlineSerializer',
    'OrganizationProjectCardItemTemplateSerializer',
    'OrganizationProjectCardItemSerializer',
    'OrganizationProjectCardItemReadTreeSerializer',
]


class OrganizationSerializer(ModelSerializer):
    class Meta:
        model = main_models.Organization
        exclude = ['created_at', 'updated_at']


class OrganizationProjectSerializer(ModelSerializer):
    organization_id = PrimaryKeyRelatedIdField(
        queryset=main_models.Organization.objects,
        label=main_models.OrganizationProject._meta.get_field('organization').verbose_name,
    )
    industry_sector_id = PrimaryKeyRelatedIdField(
        queryset=dictionary_models.IndustrySector.objects, allow_null=True, required=False,
        label=main_models.OrganizationProject._meta.get_field('industry_sector').verbose_name,
    )
    manager_id = PrimaryKeyRelatedIdField(
        queryset=User.objects, allow_null=True, required=False,
        label=main_models.OrganizationProject._meta.get_field('manager').verbose_name,
    )
    resource_managers_ids = PrimaryKeyRelatedIdField(
        source='resource_managers', queryset=User.objects, many=True, required=False, allow_null=True,
        label=main_models.OrganizationProject._meta.get_field('resource_managers').verbose_name,
    )
    recruiters_ids = PrimaryKeyRelatedIdField(
        source='recruiters', queryset=User.objects, many=True, required=False, allow_null=True,
        label=main_models.OrganizationProject._meta.get_field('recruiters').verbose_name,
    )

    class Meta:
        model = main_models.OrganizationProject
        fields = [
            'id', 'organization_id', 'industry_sector_id', 'manager_id', 'resource_managers_ids', 'recruiters_ids',
            'name', 'description', 'date_from', 'date_to', 'created_at', 'updated_at',
        ]


class OrganizationProjectReadSerializer(OrganizationProjectSerializer):
    organization = OrganizationSerializer(read_only=True)
    industry_sector = dictionary_serializers.IndustrySectorSerializer(read_only=True, allow_null=True)
    manager = UserInlineSerializer(read_only=True, allow_null=True)
    resource_managers = UserInlineSerializer(many=True, read_only=True)
    recruiters = UserInlineSerializer(many=True, read_only=True)

    modules_count = serializers.IntegerField(read_only=True)

    class Meta(OrganizationProjectSerializer.Meta):
        fields = OrganizationProjectSerializer.Meta.fields + [
            'organization', 'industry_sector', 'manager', 'resource_managers', 'recruiters',
            'modules_count',
        ]


class OrganizationProjectInlineSerializer(OrganizationProjectReadSerializer):
    pass


class OrganizationProjectCardItemBaseSerializer(ModelSerializerWithCallCleanMethod):
    parent_id = PrimaryKeyRelatedIdField(
        queryset=main_models.OrganizationProjectCardItem.objects, allow_null=True, required=False,
        label=main_models.OrganizationProjectCardItem._meta.get_field('parent').verbose_name,
    )
    positions_ids = PrimaryKeyRelatedIdField(
        queryset=dictionary_models.Position.objects, source='positions',
        many=True, allow_null=True, required=False,
        label=main_models.OrganizationProjectCardItem._meta.get_field('positions').verbose_name,
    )

    class Meta:
        fields = [
            'id', 'parent_id', 'positions_ids', 'name', 'description',
        ]


class OrganizationProjectCardItemTemplateSerializer(OrganizationProjectCardItemBaseSerializer):
    class Meta(OrganizationProjectCardItemBaseSerializer.Meta):
        model = main_models.OrganizationProjectCardItemTemplate


class OrganizationProjectCardItemSerializer(OrganizationProjectCardItemBaseSerializer):
    organization_project_id = PrimaryKeyRelatedIdField(
        queryset=main_models.OrganizationProject.objects, allow_null=True, required=False,
        label=main_models.OrganizationProjectCardItem._meta.get_field('organization_project').verbose_name,
        help_text=main_models.OrganizationProjectCardItem._meta.get_field('organization_project').help_text,
    )

    class Meta(OrganizationProjectCardItemBaseSerializer.Meta):
        model = main_models.OrganizationProjectCardItem
        fields = OrganizationProjectCardItemBaseSerializer.Meta.fields + [
            'organization_project_id',
        ]


class OrganizationProjectCardItemReadTreeSerializer(OrganizationProjectCardItemSerializer):
    children = serializers.ListField(source='get_children', child=RecursiveField())

    class Meta(OrganizationProjectCardItemSerializer.Meta):
        fields = OrganizationProjectCardItemSerializer.Meta.fields + ['children']
