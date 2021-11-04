from typing import List

import reversion
from cacheops import invalidate_model
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.forms import model_to_dict
from django.utils.translation import gettext_lazy as _
from mptt import models as mptt_models
from mptt import querysets as mptt_querysets

from project.contrib.db.models import DatesModelBase
from acc.models import User

__all__ = [
    'Organization',
    'OrganizationProject',
    'OrganizationProjectCardItemTemplate',
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

    class QuerySet(models.QuerySet):
        def filter_by_user(self, user: User) -> 'Organization.QuerySet':
            return self

    class Manager(models.Manager.from_queryset(QuerySet)):
        pass

    objects = Manager()

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
        verbose_name = _('проект')
        verbose_name_plural = _('проекты')

    class QuerySet(models.QuerySet):
        def filter_by_user(self, user: User) -> 'OrganizationProject.QuerySet':
            return self

    class Manager(models.Manager.from_queryset(QuerySet)):
        @classmethod
        def get_queryset_prefetch_related(cls) -> List[str]:
            return ['organization', 'industry_sector', 'manager', 'resource_managers', 'recruiters', 'modules']

    objects = Manager()

    def __str__(self):
        return self.name

    @property
    def modules_count(self) -> int:
        return len(self.modules.all())


class OrganizationProjectCardItemAbstract(mptt_models.MPTTModel, DatesModelBase):
    parent = mptt_models.TreeForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='children',
        verbose_name=_('родительская карточка')
    )
    name = models.CharField(max_length=500, verbose_name=_('название'))
    description = models.TextField(null=True, blank=True, verbose_name=_('описание'))
    positions = models.ManyToManyField(
        'dictionary.Position', blank=True, related_name='+', verbose_name=_('должности'))

    class Meta:
        abstract = True

    class MPTTMeta:
        level_attr = 'mptt_level'
        order_insertion_by = ['name']

    def __str__(self):
        return f'{self.name} < {self.id} >'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        invalidate_model(self.__class__)

    # def clean(self):
    #     if self.parent and self.positions:
    #         raise ValidationError({
    #             'positions': _(' Должности можно задавать только для карточки верхнего уровня')
    #         })


class OrganizationProjectCardItemTemplate(OrganizationProjectCardItemAbstract):
    class TreeQuerySet(mptt_querysets.TreeQuerySet):
        def filter_by_user(self, user: User):
            return self

    class TreeManager(
        models.Manager.from_queryset(TreeQuerySet),
        mptt_models.TreeManager
    ):
        pass

    class FlatQuerySet(models.QuerySet):
        def filter_by_user(self, user: User):
            return self

    class FlatManager(models.Manager.from_queryset(FlatQuerySet)):
        pass

    objects = TreeManager()
    objects_flat = FlatManager()

    class Meta:
        verbose_name = _('организации / карточка-шаблон проекта организации')
        verbose_name_plural = _('организации / карточки-шаблоны проектов организаций')


class OrganizationProjectCardItem(OrganizationProjectCardItemAbstract):
    organization_project = models.ForeignKey(
        'main.OrganizationProject', on_delete=models.CASCADE, related_name='cards_items', null=True, blank=True,
        verbose_name=_('проект организации'),
        help_text=_('необходимо задавать только для корневой карточки')
    )

    class Meta:
        verbose_name = _('организации / карточка проекта организации')
        verbose_name_plural = _('организации / карточки проектов организаций')

    class TreeQuerySet(mptt_querysets.TreeQuerySet):
        def filter_by_user(self, user: User):
            return self

    class TreeManager(
        models.Manager.from_queryset(TreeQuerySet),
        mptt_models.TreeManager
    ):
        @transaction.atomic
        def create_tree_by_template(
                self,
                organization_project: OrganizationProject,
                template_root_card_item: OrganizationProjectCardItemTemplate
        ) -> 'OrganizationProjectCardItem':
            root_node = self.create(
                organization_project=organization_project,
                name=template_root_card_item.name,
                description=template_root_card_item.description,
            )
            root_node.positions.add(*template_root_card_item.positions.all())
            nodes_map = {template_root_card_item.id: root_node}

            def create_children(template_parent):
                for tpl_node in reversed(template_parent.get_children()):
                    node = self.create(
                        parent=nodes_map[tpl_node.parent_id],
                        name=tpl_node.name,
                        description=tpl_node.description,
                    )
                    nodes_map[tpl_node.id] = node
                    create_children(tpl_node)

            create_children(template_root_card_item)
            # self.rebuild()
            return root_node

    class FlatQuerySet(models.QuerySet):
        def filter_by_user(self, user: User):
            return self

    class FlatManager(models.Manager.from_queryset(FlatQuerySet)):
        pass

    objects = TreeManager()
    objects_flat = FlatManager()

    def save(self, *args, **kwargs):
        if self.parent and self.organization_project != self.parent.organization_project:
            self.organization_project = self.parent.organization_project
        super().save(*args, **kwargs)
        invalidate_model(OrganizationProjectCardItem)

    def clean(self):
        super().clean()
        if self.parent is None and self.organization_project_id is None:
            raise ValidationError({
                'organization_project': _('Для карточки верхнего уровня необходимо указать проект организации')
            })
