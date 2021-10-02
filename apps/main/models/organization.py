from typing import List

import reversion
from cacheops import invalidate_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey

from project.contrib.db.models import DatesModelBase

__all__ = [
    'Organization',
    'OrganizationProject',
    'OrganizationProjectCardItem',
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
        'main.Organization', on_delete=models.RESTRICT, related_name='projects',
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
            return ['organization', 'industry_sector', 'manager', 'resource_managers', 'recruiters', 'requests']

    objects = Manager()

    def __str__(self):
        return self.name

    @property
    def requests_count(self) -> int:
        return len(self.requests.all())


class OrganizationProjectCardItem(MPTTModel, DatesModelBase):
    organization_project = models.ForeignKey(
        'main.OrganizationProject', on_delete=models.CASCADE, related_name='cards_items', null=True, blank=True,
        verbose_name=_('проект организации'),
        help_text=_('необходимо задавать только для корневой карточки')
    )
    parent = TreeForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='children',
        verbose_name=_('родительская карточка')
    )
    name = models.CharField(max_length=500, verbose_name=_('название'))
    description = models.TextField(null=True, blank=True, verbose_name=_('описание'))

    class Meta:
        verbose_name = _('карточка проект организации')
        verbose_name_plural = _('карточки проектов организаций')

    class MPTTMeta:
        level_attr = 'mptt_level'
        order_insertion_by = ['name']

    class ManagerFlat(models.Manager):
        pass

    objects_flat = ManagerFlat()

    def __str__(self):
        return f'{self.name} < {self.id} >'

    def save(self, *args, **kwargs):
        if self.parent and self.organization_project != self.parent.organization_project:
            self.organization_project = self.parent.organization_project
        super().save(*args, **kwargs)
        invalidate_model(OrganizationProjectCardItem)

    def clean(self):
        if self.parent and self.organization_project_id is not None:
            raise ValidationError({
                'organization_project': _('Проект организации задается только для карточки верхнего уровня')
            })
        if self.parent is None and self.organization_project_id is None:
            raise ValidationError({
                'organization_project': _('Для карточки верхнего уровня необходимо указать проект организации')
            })
