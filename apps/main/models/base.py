from typing import List

import reversion
from django.db import models
from django.utils.translation import gettext_lazy as _

from project.contrib.db.models import DatesModelBase

__all__ = [
    'ExperienceYears',
    'WorkLocationType',
    'Project',
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


@reversion.register()
class Project(DatesModelBase):
    name = models.CharField(max_length=500, verbose_name=_('название'))
    description = models.TextField(null=True, blank=True, verbose_name=_('описание'))
    resource_managers = models.ManyToManyField(
        'acc.User', related_name='projects_as_resource_manager',
        verbose_name=_('ресурсные менеджеры')
    )
    recruiters = models.ManyToManyField(
        'acc.User', related_name='projects_as_recruiter',
        verbose_name=_('рекрутеры')
    )

    class Meta:
        ordering = ['name']
        verbose_name = _('проект')
        verbose_name_plural = _('проекты')

    class Manager(models.Manager):
        @classmethod
        def get_queryset_prefetch_related(cls) -> List[str]:
            return ['resource_managers', 'recruiters']

    objects = Manager()

    def __str__(self):
        return self.name
