from django.db import models
from django.utils.translation import gettext_lazy as _

from project.contrib.db.models import DatesModelBase


class CurrencyReference(DatesModelBase):
    currency_name = models.CharField(
        max_length=40, verbose_name=_('Наименование валюты')
    )
    digital_code = models.CharField(
        max_length=5, verbose_name=_('Цифровой код')
    )
    designation = models.CharField(
        max_length=5, verbose_name=_('Обозначение')
    )

    class Meta:
        verbose_name = _('Справочник Валюты')
        verbose_name_plural = _('Справочники Валют')

    def __str__(self):
        return f'{self.currency_name} {self.designation}'
