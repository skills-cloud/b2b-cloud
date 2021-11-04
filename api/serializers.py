import copy
from typing import Dict

from django.core.exceptions import ValidationError, FieldDoesNotExist
from django.db.models import ManyToManyField
from rest_framework import serializers

from api.fields import PrimaryKeyRelatedIdField

__all__ = [
    'ModelSerializer', 'ModelSerializerWithCallCleanMethod', 'StatusSerializer', 'EmptySerializer',
]


class EmptySerializer(serializers.Serializer):
    pass


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
                if isinstance(instance, Dict):
                    field_value = instance.get(field.field_name)
                else:
                    field_value = getattr(instance, field.field_name)
                result[field.field_name] = field_value
        return result


class ModelSerializerWithCallCleanMethod(ModelSerializer):
    def is_valid(self, raise_exception=False):
        if not super().is_valid(raise_exception=raise_exception):
            return False
        validated_data = {}
        for field_name, field_value in self.validated_data.items():
            try:
                field = self.Meta.model._meta.get_field(field_name)
            except FieldDoesNotExist:
                continue
            if isinstance(field, ManyToManyField):
                continue
            validated_data[field_name] = field_value
        instance = copy.copy(self.instance)
        if not instance:
            instance = self.Meta.model(**validated_data)
        else:
            for k, v in validated_data.items():
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
