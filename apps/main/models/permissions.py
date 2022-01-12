from typing import TYPE_CHECKING, Optional, Callable
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _

from project.contrib.middleware.request import get_current_user
from acc.models import User, Role

if TYPE_CHECKING:
    from main import models as main_models


class MainModelPermissionsMixin:
    permission_save: Optional[Callable] = None
    permission_delete: Optional[Callable] = None

    def clean(self):
        if self.permission_save and not self.permission_save():
            raise PermissionDenied(_('У вас нет прав'))
        return super().clean()

    def delete(self, **kwargs):
        if self.permission_delete and not self.permission_delete():
            raise PermissionDenied(_('У вас нет прав'))
        return super().delete(**kwargs)


def _get_user(user: User):
    return user or get_current_user()


########################################################################################################################
# OrganizationContractor
########################################################################################################################
def organization_contractor_save(instance: 'main_models.OrganizationContractor', user: Optional[User] = None) -> bool:
    user = _get_user(user)
    if not instance.id and not user.is_superuser:
        return False
    if user.is_superuser or instance.get_user_role(user) in [Role.ADMIN]:
        return True
    return False


def organization_contractor_delete(instance: 'main_models.OrganizationContractor', user: Optional[User] = None) -> bool:
    user = _get_user(user)
    if user.is_superuser:
        return True
    return False


def organization_contractor_nested_objects_save(
        instance: 'main_models.OrganizationContractor',
        user: Optional[User] = None
) -> bool:
    user = _get_user(user)
    if user.is_superuser or instance.get_user_role(user) in [
        Role.ADMIN,
        Role.PFM,
        Role.PM,
    ]:
        return True
    return False


def organization_contractor_nested_objects_delete(
        instance: 'main_models.OrganizationContractor',
        user: Optional[User] = None
) -> bool:
    return organization_contractor_nested_objects_save(instance, user)


def organization_contractor_user_role_save(
        instance: 'main_models.OrganizationContractorUserRole',
        user: Optional[User] = None
) -> bool:
    return organization_contractor_save(instance.organization_contractor, user)


def organization_contractor_user_role_delete(
        instance: 'main_models.OrganizationContractorUserRole',
        user: Optional[User] = None
) -> bool:
    return organization_contractor_user_role_save(instance, user)


########################################################################################################################
# OrganizationCustomer
########################################################################################################################
def organization_customer_save(instance: 'main_models.OrganizationCustomer', user: Optional[User] = None) -> bool:
    return organization_contractor_nested_objects_save(instance.contractor, user)


def organization_customer_delete(instance: 'main_models.OrganizationCustomer', user: Optional[User] = None) -> bool:
    return organization_customer_save(instance, user)


########################################################################################################################
# OrganizationProject
########################################################################################################################
def organization_project_save(instance: 'main_models.OrganizationProject', user: Optional[User] = None) -> bool:
    user = _get_user(user)
    if user.is_superuser or instance.get_user_role(user) in [
        Role.ADMIN,
        Role.PFM,
        Role.PM,
    ]:
        return True
    return False


def organization_project_delete(instance: 'main_models.OrganizationProject', user: Optional[User] = None) -> bool:
    return organization_project_save(instance, user)


def organization_project_nested_objects_save(
        instance: 'main_models.OrganizationProject',
        user: Optional[User] = None
) -> bool:
    return organization_project_save(instance, user)


def organization_project_nested_objects_delete(
        instance: 'main_models.OrganizationProject',
        user: Optional[User] = None
) -> bool:
    return organization_project_nested_objects_save(instance, user)


def organization_project_user_role_save(
        instance: 'main_models.OrganizationProjectUserRole',
        user: Optional[User] = None
) -> bool:
    return organization_project_nested_objects_save(instance.organization_project, user)


def organization_project_user_role_delete(
        instance: 'main_models.OrganizationProjectUserRole',
        user: Optional[User] = None
) -> bool:
    return organization_project_nested_objects_delete(instance.organization_project, user)
