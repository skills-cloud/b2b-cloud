from functools import partial
from rest_framework.permissions import (
    AllowAny as AllowAnyBase, IsAuthenticated as IsAuthenticatedBase, SAFE_METHODS
)


class CheckPermissionMethodMixin:
    @classmethod
    def get_check_permission_method(cls, instance, is_safe_method=True):
        if hasattr(instance, 'check_permission_api'):
            return partial(instance.check_permission_api, is_safe_method=is_safe_method)
        return instance.check_permission


class AllowAny(AllowAnyBase):
    pass


class IsAuthenticated(IsAuthenticatedBase):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class IsSuperUser(IsAuthenticated):
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser
