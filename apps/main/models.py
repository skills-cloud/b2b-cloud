from django.db import models
from django.utils.translation import gettext_lazy as _

from project.contrib.db.models import DatesModelBase


class Organization(DatesModelBase):
    name = models.CharField(max_length=500, verbose_name=_('название'))
    description = models.TextField(null=True, blank=True, verbose_name=_('описание'))

    class Meta:
        ordering = ['name']
        verbose_name = _('организация')
        verbose_name_plural = _('организации')

    def __str__(self):
        return self.name


class OrganizationProject(DatesModelBase):
    organization = models.ForeignKey('main.Organization', on_delete=models.CASCADE, verbose_name=_('организация'))
    name = models.CharField(max_length=500, verbose_name=_('название'))
    description = models.TextField(null=True, blank=True, verbose_name=_('описание'))

    class Meta:
        ordering = ['name']
        verbose_name = _('проект')
        verbose_name_plural = _('проекты')

    def __str__(self):
        return self.name
