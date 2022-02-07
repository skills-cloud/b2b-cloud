from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from acc.models import User
from api.handlers.acc.serializers import UserInlineSerializer
from dictionary import models as dictionary_models
from main import models as main_models
from api.fields import PrimaryKeyRelatedIdField
from api.serializers import ModelSerializerWithCallCleanMethod
from api.handlers.dictionary import serializers as dictionary_serializers
from api.handlers.main.serializers.organization import OrganizationProjectInlineSerializer
from api.handlers.main.serializers.module.fun_point_type import (
    FunPointTypeDifficultyLevelInlineSerializer,
    FunPointTypeInlineSerializer
)

__all__ = [
    'ModuleFunPointWriteSerializer',
    'ModuleFunPointReadSerializer',
    'ModuleFunPointInlineSerializer',
    'ModulePositionLaborEstimateWriteSerializer',
    'ModulePositionLaborEstimateReadSerializer',
    'ModulePositionLaborEstimateInlineSerializer',
    'ModuleWriteSerializer',
    'ModuleReadSerializer',
    'ModuleInlineSerializer',
    'ModulePositionLaborEstimateWorkersSerializer',
    'ModulePositionLaborEstimateWorkersAndHoursSerializer',
]


class ModuleFunPointWriteSerializer(ModelSerializerWithCallCleanMethod):
    fun_point_type_id = PrimaryKeyRelatedIdField(queryset=main_models.FunPointType.objects)
    module_id = PrimaryKeyRelatedIdField(queryset=main_models.Module.objects)
    difficulty_level_id = PrimaryKeyRelatedIdField(queryset=main_models.FunPointTypeDifficultyLevel.objects)

    class Meta:
        model = main_models.ModuleFunPoint
        fields = [
            'id', 'fun_point_type_id', 'module_id', 'difficulty_level_id', 'name', 'description',
            'created_at', 'updated_at', 'sorting',
        ]
        validators = [
            UniqueTogetherValidator(
                queryset=main_models.ModuleFunPoint.objects,
                fields=['module_id', 'name']
            )
        ]


class ModuleFunPointReadSerializer(ModuleFunPointWriteSerializer):
    fun_point_type = FunPointTypeInlineSerializer(read_only=True)
    difficulty_level = FunPointTypeDifficultyLevelInlineSerializer(read_only=True)

    class Meta(ModuleFunPointWriteSerializer.Meta):
        fields = ModuleFunPointWriteSerializer.Meta.fields + ['fun_point_type', 'difficulty_level']


class ModuleFunPointInlineSerializer(ModuleFunPointReadSerializer):
    ...


class ModulePositionLaborEstimateWriteSerializer(ModelSerializerWithCallCleanMethod):
    module_id = PrimaryKeyRelatedIdField(queryset=main_models.Module.objects)
    position_id = PrimaryKeyRelatedIdField(queryset=dictionary_models.Position.objects)

    class Meta:
        model = main_models.ModulePositionLaborEstimate
        fields = [
            'id', 'module_id', 'position_id', 'count', 'hours',
            'created_at', 'updated_at', 'sorting',
        ]
        validators = [
            UniqueTogetherValidator(
                queryset=main_models.ModulePositionLaborEstimate.objects,
                fields=['module_id', 'position_id']
            )
        ]


class ModulePositionLaborEstimateReadSerializer(ModulePositionLaborEstimateWriteSerializer):
    position = dictionary_serializers.PositionSerializer(read_only=True)

    class Meta(ModulePositionLaborEstimateWriteSerializer.Meta):
        fields = ModulePositionLaborEstimateWriteSerializer.Meta.fields + ['position']


class ModulePositionLaborEstimateInlineSerializer(ModulePositionLaborEstimateReadSerializer):
    ...


class ModuleWriteSerializer(ModelSerializerWithCallCleanMethod):
    organization_project_id = PrimaryKeyRelatedIdField(
        queryset=main_models.OrganizationProject.objects,
        label=main_models.Module._meta.get_field('organization_project').verbose_name,
    )

    class Meta:
        model = main_models.Module
        fields = [
            'id', 'organization_project_id', 'name', 'start_date', 'deadline_date',
            'work_days_count', 'work_days_hours_count', 'goals', 'description', 'created_at', 'updated_at', 'sorting',
        ]
        validators = [
            UniqueTogetherValidator(
                queryset=main_models.Module.objects,
                fields=['organization_project_id', 'name']
            )
        ]


class ModuleReadSerializer(ModuleWriteSerializer):
    organization_project = OrganizationProjectInlineSerializer(read_only=True)
    fun_points = ModuleFunPointInlineSerializer(many=True, read_only=True)
    positions_labor_estimates = ModulePositionLaborEstimateInlineSerializer(many=True, read_only=True)
    difficulty_factor = serializers.FloatField(allow_null=True, read_only=True)

    class Meta(ModuleWriteSerializer.Meta):
        fields = ModuleWriteSerializer.Meta.fields + [
            'difficulty_factor', 'organization_project', 'fun_points', 'positions_labor_estimates',
        ]


class ModuleInlineSerializer(ModuleReadSerializer):
    ...


class ModulePositionLaborEstimateWorkersSerializer(serializers.Serializer):
    position_id = PrimaryKeyRelatedIdField(queryset=dictionary_models.Position.objects)
    position_name = serializers.CharField()
    workers_count = serializers.IntegerField(default=1)


class ModulePositionLaborEstimateWorkersAndHoursSerializer(ModulePositionLaborEstimateWorkersSerializer):
    hours_count = serializers.FloatField(default=0, allow_null=True)
