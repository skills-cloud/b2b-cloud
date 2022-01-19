from rest_framework.validators import UniqueTogetherValidator

from dictionary import models as dictionary_models
from main import models as main_models
from api.fields import PrimaryKeyRelatedIdField
from api.serializers import ModelSerializerWithCallCleanMethod
from api.handlers.dictionary import serializers as dictionary_serializers
from api.handlers.main.serializers.organization import MainOrganizationSerializer

__all__ = [
    'FunPointTypeDifficultyLevelWriteSerializer',
    'FunPointTypeDifficultyLevelInlineSerializer',
    'FunPointTypePositionLaborEstimateWriteSerializer',
    'FunPointTypePositionLaborEstimateInlineSerializer',
    'FunPointTypeWriteSerializer',
    'FunPointTypeReadSerializer',
    'FunPointTypeInlineSerializer',
]


class FunPointTypeDifficultyLevelWriteSerializer(ModelSerializerWithCallCleanMethod):
    fun_point_type_id = PrimaryKeyRelatedIdField(
        queryset=main_models.FunPointType.objects,
    )

    class Meta:
        model = main_models.FunPointTypeDifficultyLevel
        fields = [
            'id', 'fun_point_type_id', 'name', 'factor', 'created_at', 'updated_at', 'sorting',
        ]
        validators = [
            UniqueTogetherValidator(
                queryset=main_models.FunPointTypeDifficultyLevel.objects,
                fields=['fun_point_type_id', 'name']
            )
        ]


class FunPointTypeDifficultyLevelInlineSerializer(FunPointTypeDifficultyLevelWriteSerializer):
    ...


class FunPointTypePositionLaborEstimateWriteSerializer(ModelSerializerWithCallCleanMethod):
    fun_point_type_id = PrimaryKeyRelatedIdField(queryset=main_models.FunPointType.objects)
    position_id = PrimaryKeyRelatedIdField(queryset=dictionary_models.Position.objects)

    class Meta:
        model = main_models.FunPointTypePositionLaborEstimate
        fields = [
            'id', 'fun_point_type_id', 'position_id', 'hours', 'created_at', 'updated_at', 'sorting',
        ]
        validators = [
            UniqueTogetherValidator(
                queryset=main_models.FunPointTypePositionLaborEstimate.objects,
                fields=['fun_point_type_id', 'position_id']
            )
        ]


class FunPointTypePositionLaborEstimateInlineSerializer(FunPointTypePositionLaborEstimateWriteSerializer):
    position = dictionary_serializers.PositionSerializer(read_only=True)

    class Meta(FunPointTypePositionLaborEstimateWriteSerializer.Meta):
        fields = FunPointTypePositionLaborEstimateWriteSerializer.Meta.fields + ['position']


class FunPointTypeWriteSerializer(ModelSerializerWithCallCleanMethod):
    organization_customer_id = PrimaryKeyRelatedIdField(
        queryset=main_models.OrganizationCustomer.objects, required=False,
        label=main_models.FunPointType._meta.get_field('organization_customer').verbose_name,
    )

    class Meta:
        model = main_models.FunPointType
        fields = [
            'id', 'organization_customer_id', 'name', 'description', 'created_at', 'updated_at',
        ]
        validators = [
            UniqueTogetherValidator(
                queryset=main_models.FunPointType.objects,
                fields=['organization_customer_id', 'name']
            )
        ]


class FunPointTypeReadSerializer(FunPointTypeWriteSerializer):
    organization_customer = MainOrganizationSerializer(read_only=True)
    difficulty_levels = FunPointTypeDifficultyLevelInlineSerializer(many=True, read_only=True)
    positions_labor_estimates = FunPointTypePositionLaborEstimateInlineSerializer(many=True, read_only=True)

    class Meta(FunPointTypeWriteSerializer.Meta):
        fields = FunPointTypeWriteSerializer.Meta.fields + [
            'organization_customer', 'difficulty_levels', 'positions_labor_estimates',
        ]


class FunPointTypeInlineSerializer(FunPointTypeReadSerializer):
    ...
