from typing import Optional, Dict, List

from django.forms import model_to_dict
from rest_framework import serializers
from rest_framework.relations import RelatedField
from rest_framework_recursive.fields import RecursiveField
from drf_yasg.utils import swagger_serializer_method

from acc.models import User, Role
from dictionary import models as dictionary_models
from main import models as main_models
from api.fields import PrimaryKeyRelatedIdField
from api.serializers import ModelSerializer, ModelSerializerWithCallCleanMethod
from api.handlers.acc.serializers import UserInlineSerializer
from api.handlers.dictionary import serializers as dictionary_serializers

__all__ = [
    'MainOrganizationSerializer',
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


class MainOrganizationSerializer(ModelSerializerWithCallCleanMethod):
    current_user_roles = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = main_models.Organization
        fields = [
            'id', 'name', 'description', 'is_customer', 'is_contractor', 'is_partner',
            'legal_name', 'legal_name', 'short_name', 'general_manager_name',
            'contact_person', 'contacts_phone', 'contacts_email',
            'created_at', 'updated_at', 'current_user_roles',
        ]

    @swagger_serializer_method(serializer_or_field=serializers.MultipleChoiceField(choices=Role.choices))
    def get_current_user_roles(self, instance: main_models.Organization) -> List[str]:
        if not instance.is_contractor:
            return []
        return main_models.OrganizationContractor(**model_to_dict(instance)).get_user_roles(
            self.context['request'].user)


class OrganizationCustomerSerializer(MainOrganizationSerializer):
    class Meta(MainOrganizationSerializer.Meta):
        model = main_models.OrganizationCustomer
        fields = [f for f in MainOrganizationSerializer.Meta.fields if f not in [
            'is_customer',
        ]]
        read_only_fields = None

    def save(self, **kwargs):
        return super().save(is_customer=True, **kwargs)


class OrganizationCustomerReadSerializer(OrganizationCustomerSerializer):
    class Meta(OrganizationCustomerSerializer.Meta):
        ...


class OrganizationContractorSerializer(MainOrganizationSerializer):
    class Meta(MainOrganizationSerializer.Meta):
        model = main_models.OrganizationContractor
        fields = [f for f in MainOrganizationSerializer.Meta.fields if f not in [
            'is_contractor',
        ]]

    def save(self, **kwargs):
        return super().save(is_contractor=True, **kwargs)


class OrganizationContractorReadSerializer(OrganizationContractorSerializer):
    class Meta(OrganizationContractorSerializer.Meta):
        fields = OrganizationContractorSerializer.Meta.fields


class OrganizationProjectSerializer(ModelSerializerWithCallCleanMethod):
    organization_customer_id = PrimaryKeyRelatedIdField(
        queryset=main_models.OrganizationCustomer.objects,
        label=main_models.OrganizationProject._meta.get_field('organization_customer').verbose_name,
    )
    organization_contractor_id = PrimaryKeyRelatedIdField(
        queryset=main_models.OrganizationContractor.objects,
        label=main_models.OrganizationProject._meta.get_field('organization_contractor').verbose_name,
    )
    industry_sector_id = PrimaryKeyRelatedIdField(
        queryset=dictionary_models.IndustrySector.objects, allow_null=True, required=False,
        label=main_models.OrganizationProject._meta.get_field('industry_sector').verbose_name,
    )
    manager_pfm_id = PrimaryKeyRelatedIdField(
        queryset=User.objects, allow_null=True, required=False,
        label=main_models.OrganizationProject._meta.get_field('manager_pfm').verbose_name,
    )
    manager_pm_id = PrimaryKeyRelatedIdField(
        queryset=User.objects, allow_null=True, required=False,
        label=main_models.OrganizationProject._meta.get_field('manager_pm').verbose_name,
    )

    class Meta:
        model = main_models.OrganizationProject
        fields = [
            'id', 'status', 'organization_customer_id', 'organization_contractor_id', 'industry_sector_id',
            'manager_pfm_id', 'manager_pm_id', 'name', 'description', 'goals', 'plan_description', 'date_from',
            'date_to', 'created_at', 'updated_at',
        ]


class OrganizationProjectReadSerializer(OrganizationProjectSerializer):
    organization_customer = MainOrganizationSerializer(read_only=True)
    organization_contractor = MainOrganizationSerializer(read_only=True)
    industry_sector = dictionary_serializers.IndustrySectorSerializer(read_only=True, allow_null=True)
    manager_pfm = UserInlineSerializer(read_only=True, allow_null=True)
    manager_pm = UserInlineSerializer(read_only=True, allow_null=True)

    modules_count = serializers.IntegerField(read_only=True)
    current_user_roles = serializers.SerializerMethodField(read_only=True)
    requests_count_total = serializers.SerializerMethodField(read_only=True)
    requests_count_by_status = serializers.SerializerMethodField(read_only=True)
    requests_requirements_count_total = serializers.SerializerMethodField(read_only=True)
    requests_requirements_count_by_status = serializers.SerializerMethodField(read_only=True)

    class Meta(OrganizationProjectSerializer.Meta):
        fields = OrganizationProjectSerializer.Meta.fields + [
            'organization_customer', 'organization_contractor', 'industry_sector', 'manager_pfm', 'manager_pm',
            'modules_count', 'current_user_roles', 'requests_count_total', 'requests_count_by_status',
            'requests_requirements_count_total', 'requests_requirements_count_by_status',
        ]

    @swagger_serializer_method(serializer_or_field=serializers.MultipleChoiceField(choices=Role.choices))
    def get_current_user_roles(self, instance: main_models.OrganizationProject) -> List[str]:
        return instance.get_user_roles(self.context['request'].user)

    @swagger_serializer_method(serializer_or_field=serializers.IntegerField)
    def get_requests_count_total(self, instance: main_models.OrganizationProject) -> int:
        return instance.get_requests_count()

    @swagger_serializer_method(serializer_or_field=serializers.DictField)
    def get_requests_count_by_status(self, instance: main_models.OrganizationProject) -> Dict[str, int]:
        return {
            c: instance.get_requests_count(c)
            for c in main_models.RequestStatus.values
        }

    @swagger_serializer_method(serializer_or_field=serializers.IntegerField)
    def get_requests_requirements_count_total(self, instance: main_models.OrganizationProject) -> int:
        return instance.get_requests_requirements_count()

    @swagger_serializer_method(serializer_or_field=serializers.DictField)
    def get_requests_requirements_count_by_status(self, instance: main_models.OrganizationProject) -> Dict[str, int]:
        return {
            c: instance.get_requests_requirements_count(c)
            for c in main_models.RequestRequirementStatus.values
        }


class OrganizationProjectInlineSerializer(OrganizationProjectReadSerializer):
    class Meta(OrganizationProjectReadSerializer.Meta):
        fields = [
            f for f in OrganizationProjectReadSerializer.Meta.fields
            if f not in ['current_user_role', 'modules_count', 'requests_count_total', 'requests_count_by_status']
        ]


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
