from cv import models as cv_models
from main import models as main_models
from api.fields import PrimaryKeyRelatedIdField
from api.serializers import ModelSerializerWithCallCleanMethod
from api.handlers.cv.serializers import CvInlineShortSerializer
from api.handlers.main.serializers.request.request import RequestRequirementInlineSerializer

__all__ = [
    'TimeSheetRowSerializer',
    'TimeSheetRowReadSerializer',
]


class TimeSheetRowSerializer(ModelSerializerWithCallCleanMethod):
    request_requirement_id = PrimaryKeyRelatedIdField(
        queryset=main_models.RequestRequirement.objects,
        label=main_models.TimeSheetRow._meta.get_field('request_requirement').verbose_name,
    )
    cv_id = PrimaryKeyRelatedIdField(
        queryset=cv_models.CV.objects,
        label=main_models.TimeSheetRow._meta.get_field('cv').verbose_name,
    )

    class Meta:
        model = main_models.TimeSheetRow
        fields = [
            'id', 'request_requirement_id', 'cv_id',
            'date_from', 'date_to', 'task_name', 'task_description', 'work_time', 'created_at', 'updated_at',
        ]


class TimeSheetRowReadSerializer(TimeSheetRowSerializer):
    request_requirement = RequestRequirementInlineSerializer()
    cv = CvInlineShortSerializer()

    class Meta(TimeSheetRowSerializer.Meta):
        fields = TimeSheetRowSerializer.Meta.fields + [
            'request_requirement', 'cv',
        ]
