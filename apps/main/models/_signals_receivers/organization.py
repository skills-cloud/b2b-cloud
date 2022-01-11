from django.core.exceptions import ValidationError, PermissionDenied
from django.utils.translation import gettext_lazy as _

from acc.models import Role
from project.contrib.middleware.request import get_current_user
from main import models as main_models
from main.models._signals_receivers._base import SignalsReceiver


class OrganizationContractorSignalsReceiver(SignalsReceiver):
    instance: main_models.OrganizationContractor

    def validate(self):
        super().validate()


class OrganizationCustomerSignalsReceiver(SignalsReceiver):
    instance: main_models.OrganizationCustomer

    def validate(self):
        super().validate()
        user = get_current_user()
        if not user.is_superuser and self.instance.contractor.get_user_role(user) not in [
            Role.ADMIN,
            Role.PFM,
            Role.PM,
        ]:
            raise PermissionDenied(_('У вас нет прав'))

    def pre_delete(self, **kwargs) -> None:
        self._log_signal('pre_delete', **kwargs)
        user = get_current_user()
        if not user.is_superuser and self.instance.contractor.get_user_role(user) not in [
            Role.ADMIN,
            Role.PFM,
            Role.PM,
        ]:
            raise PermissionDenied(_('У вас нет прав'))
