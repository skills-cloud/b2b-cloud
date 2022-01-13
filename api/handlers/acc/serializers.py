import pytz
from django.conf import settings
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from main import models as main_models
from acc.models import User
from api.fields import PrimaryKeyRelatedIdField
from api.serializers import ModelSerializer, ModelSerializerWithCallCleanMethod

__all__ = [
    'UserOrganizationContractorRoleSerializer',
    'UserOrganizationProjectRoleSerializer',
    'UserManageSerializer',
    'UserManageReadSerializer',
    'UserSerializer',
    'UserInlineSerializer',
    'UserSetPhotoSerializer',
    'WhoAmISerializer',
    'LoginSerializer',
]


class UserOrganizationContractorRoleSerializer(ModelSerializerWithCallCleanMethod):
    organization_contractor_id = PrimaryKeyRelatedIdField(queryset=main_models.OrganizationContractor.objects)
    organization_contractor_name = serializers.CharField(source='organization_contractor.name', read_only=True)

    class Meta:
        model = main_models.OrganizationContractorUserRole
        fields = ['role', 'organization_contractor_id', 'organization_contractor_name']


class UserOrganizationProjectRoleSerializer(ModelSerializerWithCallCleanMethod):
    organization_project_id = PrimaryKeyRelatedIdField(queryset=main_models.OrganizationProject.objects)
    organization_project_name = serializers.CharField(source='organization_project.name', read_only=True)
    organization_contractor_id = serializers.IntegerField(source='organization_project.organization.id', read_only=True)
    organization_contractor_name = serializers.CharField(
        source='organization_project.organization.name', read_only=True)

    class Meta:
        model = main_models.OrganizationProjectUserRole
        fields = [
            'role', 'organization_project_id', 'organization_project_name',
            'organization_contractor_id', 'organization_contractor_name',
        ]


class UserManageSerializer(ModelSerializerWithCallCleanMethod):
    organization_contractors_roles = UserOrganizationContractorRoleSerializer(
        source='organizations_contractors_roles', many=True, allow_null=True, required=False)
    organization_projects_roles = UserOrganizationProjectRoleSerializer(
        source='organizations_projects_roles', many=True, allow_null=True, required=False)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'middle_name', 'last_name', 'gender', 'birth_date', 'phone',
            'organization_contractors_roles', 'organization_projects_roles',
        ]

    @transaction.atomic
    def save(self, **kwargs):
        organizations_contractors_roles = self.validated_data.pop('organizations_contractors_roles', None)
        organizations_projects_roles = self.validated_data.pop('organizations_projects_roles', None)
        super().save(**kwargs)
        if organizations_contractors_roles is not None:
            for row in organizations_contractors_roles:
                role_kwargs = {
                    'user': self.instance,
                    'organization_contractor_id': row['organization_contractor_id'],
                }
                main_models.OrganizationContractorUserRole.objects.filter(**role_kwargs).delete()
                role_instance = main_models.OrganizationContractorUserRole(**role_kwargs, role=row['role'])
                role_instance.clean()
                role_instance.save()
        if organizations_projects_roles is not None:
            for row in organizations_projects_roles:
                role_kwargs = {
                    'user': self.instance,
                    'organization_project_id': row['organization_project_id'],
                }
                main_models.OrganizationProjectUserRole.objects.filter(**role_kwargs).delete()
                role_instance = main_models.OrganizationProjectUserRole(**role_kwargs, role=row['role'])
                role_instance.clean()
                role_instance.save()
        return self.instance

    def is_valid(self, raise_exception=False):
        ModelSerializer.is_valid(self, raise_exception=raise_exception)
        organizations_contractors_roles = self.validated_data.pop('organizations_contractors_roles', None)
        organizations_projects_roles = self.validated_data.pop('organizations_projects_roles', None)
        if not self.context['request'].user.is_superuser and not organizations_contractors_roles:
            raise ValidationError({'organizations_contractors_roles': _('Обязательное поле.')})
        super().is_valid(raise_exception=raise_exception)
        if organizations_contractors_roles is not None:
            self.validated_data['organizations_contractors_roles'] = organizations_contractors_roles
        if organizations_projects_roles is not None:
            self.validated_data['organizations_projects_roles'] = organizations_projects_roles


class UserManageReadSerializer(UserManageSerializer):
    class Meta(UserManageSerializer.Meta):
        ...


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        exclude = [
            'password', 'groups', 'user_permissions', 'date_joined', 'is_superuser', 'is_staff', 'email'
        ]
        read_only_fields = [
            'is_superuser', 'is_staff', 'is_active', 'last_login', 'date_joined', 'date_updated',
        ]


class UserInlineSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        exclude = UserSerializer.Meta.exclude + ['last_login', 'is_active']


class UserSetPhotoSerializer(UserSerializer):
    photo = serializers.ImageField(required=True)

    class Meta:
        model = User
        fields = ['photo']


class WhoAmISerializer(UserSerializer):
    roles = serializers.ListSerializer(child=serializers.CharField(), read_only=True)

    class Meta(UserSerializer.Meta):
        exclude = ['password', 'groups', 'user_permissions']


class LoginSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        exclude = None
        fields = ['email', 'password']


class SetTimeZoneSerializer(serializers.Serializer):
    time_zone = serializers.ChoiceField(
        choices=[[what] * 2 for what in pytz.all_timezones_set],
        default=settings.TIME_ZONE,
    )
