import logging

from typing import TYPE_CHECKING, Optional, Callable
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _

from project.contrib.middleware.request import get_current_user
from acc.models import User, Role

if TYPE_CHECKING:
    from main import models as main_models

logger = logging.getLogger(__name__)


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


def _get_user(user: User) -> User:
    return user or get_current_user()


########################################################################################################################
# Organization Contractor
########################################################################################################################
def organization_contractor_save(instance: 'main_models.OrganizationContractor', user: Optional[User] = None) -> bool:
    user = _get_user(user)
    if set(instance.get_user_roles(user)) & set([Role.ADMIN]):
        return True
    return False


def organization_contractor_delete(instance: 'main_models.OrganizationContractor', user: Optional[User] = None) -> bool:
    return organization_contractor_save(instance, user)


def organization_contractor_nested_objects_save(
        instance: 'main_models.OrganizationContractor',
        user: Optional[User] = None
) -> bool:
    user = _get_user(user)
    if set(instance.get_user_roles(user)) & set([
        Role.ADMIN,
        Role.PFM,
        Role.PM,
    ]):
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
# Organization Customer
########################################################################################################################
def organization_customer_save(instance: 'main_models.OrganizationCustomer', user: Optional[User] = None) -> bool:
    user = _get_user(user)
    return user.is_superuser or user.is_staff


def organization_customer_delete(instance: 'main_models.OrganizationCustomer', user: Optional[User] = None) -> bool:
    return organization_customer_save(instance, user)


########################################################################################################################
# Fun Point
########################################################################################################################

def fun_point_type_save(instance: 'main_models.FunPointType', user: Optional[User] = None) -> bool:
    return organization_customer_save(instance.organization_customer, user)


def fun_point_type_delete(instance: 'main_models.FunPointType', user: Optional[User] = None) -> bool:
    return fun_point_type_save(instance, user)


def fun_point_type_difficulty_level_save(
        instance: 'main_models.FunPointTypeDifficultyLevel',
        user: Optional[User] = None
) -> bool:
    return fun_point_type_save(instance.fun_point_type, user)


def fun_point_type_difficulty_level_delete(
        instance: 'main_models.FunPointTypeDifficultyLevel',
        user: Optional[User] = None
) -> bool:
    return fun_point_type_difficulty_level_save(instance, user)


def fun_point_type_position_labor_estimate_save(
        instance: 'main_models.FunPointTypePositionLaborEstimate',
        user: Optional[User] = None
) -> bool:
    return fun_point_type_save(instance.fun_point_type, user)


def fun_point_type_position_labor_estimate_delete(
        instance: 'main_models.FunPointTypePositionLaborEstimate',
        user: Optional[User] = None
) -> bool:
    return fun_point_type_position_labor_estimate_save(instance, user)


########################################################################################################################
# Organization Project
########################################################################################################################
def organization_project_save(instance: 'main_models.OrganizationProject', user: Optional[User] = None) -> bool:
    user = _get_user(user)
    if set(instance.get_user_roles(user)) & set([
        Role.ADMIN,
        Role.PFM,
        Role.PM,
    ]):
        return True
    return False


def organization_project_delete(instance: 'main_models.OrganizationProject', user: Optional[User] = None) -> bool:
    return organization_project_save(instance, user)


def organization_project_nested_objects_save(
        instance: 'main_models.OrganizationProject',
        user: Optional[User] = None
) -> bool:
    user = _get_user(user)
    if set(instance.get_user_roles(user)) & set([
        Role.ADMIN,
        Role.PFM,
        Role.PM
    ]):
        return True
    return False


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


########################################################################################################################
# Organization Project / Module
########################################################################################################################

def module_save(instance: 'main_models.Module', user: Optional[User] = None) -> bool:
    return organization_project_nested_objects_save(instance.organization_project, user)


def module_delete(instance: 'main_models.Module', user: Optional[User] = None) -> bool:
    return organization_project_nested_objects_delete(instance.organization_project, user)


def module_fun_point_save(instance: 'main_models.ModuleFunPoint', user: Optional[User] = None) -> bool:
    return organization_project_nested_objects_save(instance.module.organization_project, user)


def module_fun_point_delete(instance: 'main_models.ModuleFunPoint', user: Optional[User] = None) -> bool:
    return organization_project_nested_objects_delete(instance.module.organization_project, user)


def module_position_labor_estimate_save(
        instance: 'main_models.ModulePositionLaborEstimate',
        user: Optional[User] = None
) -> bool:
    return organization_project_nested_objects_save(instance.module.organization_project, user)


def module_position_labor_estimate_delete(
        instance: 'main_models.ModulePositionLaborEstimate',
        user: Optional[User] = None
) -> bool:
    return organization_project_nested_objects_delete(instance.module.organization_project, user)


########################################################################################################################
# Organization Project / Module / Request
########################################################################################################################

def request_save(instance: 'main_models.Request', user: Optional[User] = None) -> bool:
    return organization_project_nested_objects_save(instance.module.organization_project, user)


def request_delete(instance: 'main_models.Request', user: Optional[User] = None) -> bool:
    return organization_project_nested_objects_delete(instance.module.organization_project, user)


########################################################################################################################
# Organization Project / Module / Request / TimeSheetRow
########################################################################################################################

def request_time_sheet_row_save(instance: 'main_models.TimeSheetRow', user: Optional[User] = None) -> bool:
    user = _get_user(user)
    if set(instance.request.module.organization_project.get_user_roles(user)) & set([
        Role.ADMIN,
        Role.PFM,
        Role.PM,
        Role.RM,
    ]):
        return True
    return False


def request_time_sheet_row_delete(instance: 'main_models.TimeSheetRow', user: Optional[User] = None) -> bool:
    return request_time_sheet_row_save(instance, user)


########################################################################################################################
# Organization Project / Module / Request / Requirement
########################################################################################################################

def request_requirement_save(instance: 'main_models.RequestRequirement', user: Optional[User] = None) -> bool:
    return organization_project_nested_objects_save(instance.request.module.organization_project, user)


def request_requirement_delete(instance: 'main_models.RequestRequirement', user: Optional[User] = None) -> bool:
    return organization_project_nested_objects_delete(instance.request.module.organization_project, user)


def request_requirement_competence_save(
        instance: 'main_models.RequestRequirementCompetence',
        user: Optional[User] = None
) -> bool:
    return request_requirement_save(instance.request_requirement, user)


def request_requirement_competence_delete(
        instance: 'main_models.RequestRequirementCompetence',
        user: Optional[User] = None
) -> bool:
    return request_requirement_cv_delete(instance.request_requirement, user)


########################################################################################################################
# Organization Project / Module / Request / Requirement / CV
########################################################################################################################

def request_requirement_cv_save(instance: 'main_models.RequestRequirementCv', user: Optional[User] = None) -> bool:
    user = _get_user(user)
    if set(instance.request_requirement.request.module.organization_project.get_user_roles(user)) & set([
        Role.ADMIN,
        Role.PFM,
        Role.PM,
        Role.RM,
    ]):
        return True
    return False


def request_requirement_cv_delete(instance: 'main_models.RequestRequirementCv', user: Optional[User] = None) -> bool:
    return request_requirement_cv_save(instance, user)
