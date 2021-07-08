from django.core.exceptions import ValidationError
from rest_framework import serializers

from api.fields import PrimaryKeyRelatedIdField

__all__ = ['ModelSerializer', 'ModelSerializerWithCallCleanMethod', 'StatusSerializer']


class StatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=[
        [k, k] for k in ['ok', 'error', 'warning']
    ])
    details = serializers.CharField(allow_blank=True, allow_null=True, default=None)


class ModelSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        result = super().to_representation(instance)
        for field in self._readable_fields:
            if isinstance(field, PrimaryKeyRelatedIdField):
                result[field.field_name] = getattr(instance, field.field_name)
        return result


class ModelSerializerWithCallCleanMethod(ModelSerializer):
    def is_valid(self, raise_exception=False):
        if not super().is_valid(raise_exception=raise_exception):
            return False
        instance = self.instance
        if not instance:
            instance = self.Meta.model(**self.validated_data)
        else:
            for k, v in self.validated_data.items():
                setattr(instance, k, v)
        self._clean(instance)
        return True

    @classmethod
    def _clean(cls, instance):
        cls._catch(lambda: instance.clean())

    @classmethod
    def _catch(cls, action: callable):
        try:
            return action()
        except ValidationError as e:
            raise serializers.ValidationError(e.args[0])
