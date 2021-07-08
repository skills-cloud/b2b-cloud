from django.db import models
from rest_framework.fields import CurrentUserDefault
from rest_framework.relations import PrimaryKeyRelatedField


class CurrentUserIdDefault(CurrentUserDefault):
    def __call__(self, serializer_field):
        return serializer_field.context['request'].user.id


class PrimaryKeyRelatedIdField(PrimaryKeyRelatedField):
    def get_default(self):
        default = super().get_default()
        if default and isinstance(default, models.Model):
            return default.id
        return default

    def to_internal_value(self, data):
        value = super().to_internal_value(data)
        try:
            return value.id
        except Exception:
            return int(data)
