from typing import Optional

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
    'OrganizationCustomerSerializer',
    'OrganizationCustomerReadSerializer',
    'OrganizationContractorSerializer',
    'OrganizationContractorReadSerializer',
    'OrganizationProjectSerializer',
    'OrganizationProjectReadSerializer',
    'OrganizationProjectInlineSerializer',
    'OrganizationProjectCardItemTemplateSerializer',
    'OrganizationProjectCardItemSerializer',
    'OrganizationProjectCardItemReadTreeSerializer',
]


class OrganizationSerializer(ModelSerializerWithCallCleanMethod):
    class Meta:
        model = main_models.Organization
        fields = [
            'id', 'contractor_id', 'name', 'description', 'is_customer', 'is_contractor',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['contractor_id']


class OrganizationCustomerSerializer(OrganizationSerializer):
    contractor_id = PrimaryKeyRelatedIdField(
        queryset=main_models.OrganizationContractor.objects,
        label=main_models.Organization._meta.get_field('contractor').verbose_name,
    )

    class Meta(OrganizationSerializer.Meta):
        model = main_models.OrganizationCustomer
        fields = [f for f in OrganizationSerializer.Meta.fields if f not in [
            'is_customer', 'is_contractor',
        ]]
        read_only_fields = None

    def save(self, **kwargs):
        return super().save(is_customer=True, **kwargs)


class OrganizationCustomerReadSerializer(OrganizationCustomerSerializer):
    class Meta(OrganizationCustomerSerializer.Meta):
        ...


class OrganizationContractorSerializer(OrganizationSerializer):
    class Meta(OrganizationSerializer.Meta):
        model = main_models.OrganizationContractor
        fields = [f for f in OrganizationSerializer.Meta.fields if f not in [
            'contractor_id', 'is_contractor',
        ]]

    def save(self, **kwargs):
        return super().save(is_contractor=True, **kwargs)


class OrganizationContractorReadSerializer(OrganizationContractorSerializer):
    current_user_role = serializers.SerializerMethodField()

    class Meta(OrganizationContractorSerializer.Meta):
        fields = OrganizationContractorSerializer.Meta.fields + ['current_user_role']

    def get_current_user_role(self, instance: main_models.OrganizationContractor) -> Optional[str]:
        return instance.get_user_role(self.context['request'].user)


class OrganizationProjectSerializer(ModelSerializer):
    organization_customer_id = PrimaryKeyRelatedIdField(
        queryset=main_models.OrganizationCustomer.objects,
        label=main_models.OrganizationProject._meta.get_field('organization_customer').verbose_name,
    )
    industry_sector_id = PrimaryKeyRelatedIdField(
        queryset=dictionary_models.IndustrySector.objects, allow_null=True, required=False,
        label=main_models.OrganizationProject._meta.get_field('industry_sector').verbose_name,
    )
    manager_id = PrimaryKeyRelatedIdField(
        queryset=User.objects, allow_null=True, required=False,
        label=main_models.OrganizationProject._meta.get_field('manager').verbose_name,
    )

    class Meta:
        model = main_models.OrganizationProject
        fields = [
            'id', 'organization_customer_id', 'industry_sector_id', 'manager_id',
            'name', 'description', 'goals', 'plan_description', 'date_from', 'date_to', 'created_at', 'updated_at',
        ]


class OrganizationProjectReadSerializer(OrganizationProjectSerializer):
    organization_customer = OrganizationSerializer(read_only=True)
    industry_sector = dictionary_serializers.IndustrySectorSerializer(read_only=True, allow_null=True)
    manager = UserInlineSerializer(read_only=True, allow_null=True)

    modules_count = serializers.IntegerField(read_only=True)
    current_user_role = serializers.SerializerMethodField()

    class Meta(OrganizationProjectSerializer.Meta):
        fields = OrganizationProjectSerializer.Meta.fields + [
            'organization_customer', 'industry_sector', 'manager', 'modules_count', 'current_user_role',
        ]

    def get_current_user_role(self, instance: main_models.OrganizationProject) -> Optional[str]:
        return instance.get_user_role(self.context['request'].user)


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
