from django.db import models
from django.utils.translation import gettext_lazy as _

from project.contrib.db.models import DatesModelBase


class Customer(DatesModelBase):
    name = models.CharField(max_length=500, verbose_name=_('название'))
    description = models.TextField(null=True, blank=True, verbose_name=_('описание'))

    class Meta:
        ordering = ['name']
        verbose_name = _('заказчик')
        verbose_name_plural = _('заказчики')

    def __str__(self):
        return self.name


class Project(DatesModelBase):
    customer = models.ForeignKey('main.Customer', on_delete=models.RESTRICT, related_name='projects')
    name = models.CharField(max_length=500, verbose_name=_('название'))
    description = models.TextField(null=True, blank=True, verbose_name=_('описание'))

    class Meta:
        ordering = ['name']
        verbose_name = _('проект')
        verbose_name_plural = _('проекты')
