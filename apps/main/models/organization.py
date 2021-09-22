from typing import List, Dict, Any

import reversion
from django.db import models
from django.utils.translation import gettext_lazy as _

from project.contrib.db.models import DatesModelBase

__all__ = [
    'Organization',
    'OrganizationProject'
]


@reversion.register(follow=['projects'])
class Organization(DatesModelBase):
    name = models.CharField(max_length=500, verbose_name=_('название'))
    description = models.TextField(null=True, blank=True, verbose_name=_('описание'))
    is_customer = models.BooleanField(default=False, verbose_name=_('заказчик?'))

    class Meta:
        ordering = ['name']
        verbose_name = _('организация')
        verbose_name_plural = _('организации')

    def __str__(self):
        return self.name


@reversion.register(follow=['organization'])
class OrganizationProject(DatesModelBase):
    organization = models.ForeignKey(
        'main.Organization', on_delete=models.CASCADE, related_name='projects',
        verbose_name=_('организация')
    )
    name = models.CharField(max_length=500, verbose_name=_('название'))
    description = models.TextField(null=True, blank=True, verbose_name=_('описание'))
    date_from = models.DateField(null=True, blank=True, verbose_name=_('дата с'))
    date_to = models.DateField(null=True, blank=True, verbose_name=_('дата по'))
    industry_sector = models.ForeignKey(
        'dictionary.IndustrySector', related_name='organizations_projects', null=True, blank=True,
        on_delete=models.RESTRICT, verbose_name=_('отрасль')
    )
    manager = models.ForeignKey(
        'acc.User', related_name='organizations_projects_as_manager', null=True, blank=True,
        on_delete=models.RESTRICT, verbose_name=_('руководитель проекта')
    )
    resource_managers = models.ManyToManyField(
        'acc.User', related_name='organizations_projects_as_resource_manager',
        verbose_name=_('ресурсные менеджеры')
    )
    recruiters = models.ManyToManyField(
        'acc.User', related_name='organizations_projects_as_recruiter',
        verbose_name=_('рекрутеры')
    )

    class Meta:
        ordering = ['name']
        verbose_name = _('проект организации')
        verbose_name_plural = _('проекты организаций')

    class Manager(models.Manager):
        @classmethod
        def get_queryset_prefetch_related(cls) -> List[str]:
            return ['organization', 'industry_sector', 'manager', 'resource_managers', 'recruiters']

    objects = Manager()

    def __str__(self):
        return self.name
