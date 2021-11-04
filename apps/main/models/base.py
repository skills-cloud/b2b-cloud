from django.db import models
from django.utils.translation import gettext_lazy as _

__all__ = [
    'ExperienceYears',
    'WorkLocationType',
]


class ExperienceYears(models.IntegerChoices):
    ZERO = 1, _('Менее года')
    THREE = 3, _('1 – 3 года')
    FIVE = 5, _('3 - 5 лет')
    ONE_HUNDRED = 100, _('Более 5 лет')


class WorkLocationType(models.TextChoices):
    OFFICE = 'office', _('Офис')
    HOME = 'home', _('Удаленная работа')
    MIXED = 'mixed', _('Офис или удаленная')
