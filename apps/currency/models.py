from django.db import models
from django.utils.translation import gettext_lazy as _

from project.contrib.db.models import DatesModelBase


class CurrencyReference(DatesModelBase):
    currency_name = models.CharField(
        max_length=40, verbose_name=_('Currency name')
    )
    digital_code = models.CharField(
        max_length=5, verbose_name=_('Digital code')
    )
    designation = models.CharField(
        max_length=5, verbose_name=_('Designation')
    )
    # ссылки валют

    class Meta:
        verbose_name = _('Currency reference')
        verbose_name_plural = _('Currency references')

    def __str__(self):
        return f'{self.currency_name} {self.designation}'
