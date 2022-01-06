from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from main import models as main_models
from main.models._signals_receivers._base import SignalsReceiver


class OrganizationProjectSignalsReceiver(SignalsReceiver):
    instance: main_models.OrganizationProject


class OrganizationProjectUserRoleSignalsReceiver(SignalsReceiver):
    instance: main_models.OrganizationProjectUserRole

    def validate(self):
        if not main_models.OrganizationContractorUserRole.objects.filter(user=self.instance.user).exists():
            raise ValidationError(_('Пользователю не назначена роль в организации исполнителе'))
