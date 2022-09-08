from typing import TYPE_CHECKING, Optional
from project.contrib.middleware.request import get_current_user

if TYPE_CHECKING:
    from acc.models import User, Role


def _get_user(user: 'User') -> 'User':
    return user or get_current_user()


def user_save(instance: 'User', user: Optional['User'] = None) -> bool:
    from acc.models import Role
    from main.models import OrganizationContractorUserRole
    user = _get_user(user)
    if not user:
        return True
    if user.is_superuser or user.is_staff:
        return True
    return OrganizationContractorUserRole.objects.filter(
        user=instance,
        organization_contractor__in=[
            row.organization_contractor
            for row in user.organizations_contractors_roles.all()
            if row.role in [
                Role.ADMIN
            ]
        ]
    ).exists()


def user_delete(instance: 'User', user: Optional['User'] = None) -> bool:
    user = _get_user(user)
    if user.is_superuser or user.is_staff:
        return True
    return False
