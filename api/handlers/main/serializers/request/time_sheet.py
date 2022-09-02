from cv import models as cv_models
from main import models as main_models
from api.fields import PrimaryKeyRelatedIdField
from api.serializers import ModelSerializer
from api.handlers.cv.serializers import CvInlineShortSerializer
from api.handlers.main.serializers.request.request import RequestInlineSerializer

__all__ = [
    'TimeSheetRowCreateSerializer',
    'TimeSheetRowUpdateSerializer',
    'TimeSheetRowReadSerializer',
]


class TimeSheetRowBaseSerializer(ModelSerializer):
    request_id = PrimaryKeyRelatedIdField(
        queryset=main_models.Request.objects,
        label=main_models.TimeSheetRow._meta.get_field('request').verbose_name,
    )

    class Meta:
        model = main_models.TimeSheetRow
        fields = [
            'request_id', 'date_from', 'date_to', 'task_name', 'task_description', 'work_time',
            'created_at', 'updated_at',
        ]


class TimeSheetRowCreateSerializer(TimeSheetRowBaseSerializer):
    cv_ids = PrimaryKeyRelatedIdField(
        queryset=cv_models.CV.objects,
        many=True, required=True,
        label=main_models.TimeSheetRow._meta.get_field('cv').verbose_name,
    )

    class Meta(TimeSheetRowBaseSerializer.Meta):
        fields = TimeSheetRowBaseSerializer.Meta.fields + [
            'cv_ids',
        ]


class TimeSheetRowUpdateSerializer(TimeSheetRowBaseSerializer):
    cv_id = PrimaryKeyRelatedIdField(
        queryset=cv_models.CV.objects,
        label=main_models.TimeSheetRow._meta.get_field('cv').verbose_name,
    )

    class Meta(TimeSheetRowBaseSerializer.Meta):
        fields = TimeSheetRowBaseSerializer.Meta.fields + ['cv_id', 'id']


class TimeSheetRowReadSerializer(TimeSheetRowUpdateSerializer):
    request = RequestInlineSerializer()
    cv = CvInlineShortSerializer()

    class Meta(TimeSheetRowUpdateSerializer.Meta):
        fields = TimeSheetRowUpdateSerializer.Meta.fields + [
            'request', 'cv',
        ]
