from django.db import models
from django.utils.translation import gettext_lazy as _

__all__ = [
    'ExperienceYears',
    'WorkLocationType',
    'ServicesType'
]


class ExperienceYears(models.IntegerChoices):
    ZERO = 1, _('Less than a year')
    THREE = 3, _('1 – 3 years')
    FIVE = 5, _('3 - 5 years')
    ONE_HUNDRED = 100, _('More than 5 years')


class WorkLocationType(models.TextChoices):
    OFFICE = 'office', _('Office')
    HOME = 'home', _('Remote')
    MIXED = 'mixed', _('Office or remote')


class ServicesType(models.TextChoices):
    OUTSOURCE = 'OUTSOURCE', _('Outsource')
    OUTSTAFF = 'OUTSTAFF', _('Outstaff')
