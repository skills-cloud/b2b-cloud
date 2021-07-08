import pytz
from django.conf import settings
from rest_framework import serializers

from acc.models import User
from api.serializers import ModelSerializer

__all__ = [
    'UserSerializer',
    'UserInlineSerializer',
    'UserSetPhotoSerializer',
    'WhoAmISerializer',
    'LoginSerializer',
]


class UserSerializer(ModelSerializer):
    is_host = serializers.BooleanField(read_only=True)
    host_id = serializers.IntegerField(read_only=True, allow_null=True)

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
