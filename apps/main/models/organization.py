from typing import List

import reversion
from cacheops import invalidate_model
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from mptt import models as mptt_models
from mptt import querysets as mptt_querysets

from project.contrib.db import get_sql_from_queryset
from project.contrib.db.models import DatesModelBase, ModelDiffMixin
from acc.models import User, Role

__all__ = [
    'Organization',
    'OrganizationCustomer',
    'OrganizationContractor',
    'OrganizationContractorUserRole',
    'OrganizationProject',
    'OrganizationProjectUserRole',
    'OrganizationProjectCardItemTemplate',
    'OrganizationProjectCardItem',
]


@reversion.register(follow=['projects'])
class Organization(DatesModelBase):
    name = models.CharField(max_length=500, db_index=True, verbose_name=_('название'))
    description = models.TextField(null=True, blank=True, verbose_name=_('описание'))
    is_customer = models.BooleanField(default=False, verbose_name=_('это заказчик?'))
    is_contractor = models.BooleanField(default=False, verbose_name=_('это исполнитель?'))
    contractor = models.ForeignKey(
        'main.OrganizationContractor', blank=True, null=True, on_delete=models.SET_NULL,
        verbose_name=_('исполнитель для этого заказчика'),
        help_text=_('имеет значение только для организаций заказчиков')
    )

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


class OrganizationCustomer(Organization):
    class QuerySet(Organization.QuerySet):
        def filter_by_user(self, user: User) -> 'OrganizationCustomer.QuerySet':
            if user.is_superuser or user.is_staff:
                return self
            return self.filter(
                contractor__in=OrganizationContractorUserRole.objects
                    .filter(user=user)
                    .values('organization_contractor')
            )

    class Manager(models.Manager.from_queryset(QuerySet)):
        def get_queryset(self) -> 'OrganizationCustomer.QuerySet':
            return super().get_queryset().filter(is_customer=True)

    objects = Manager()

    class Meta:
        proxy = True
        ordering = ['name']
        verbose_name = _('организация заказчик')
        verbose_name_plural = _('организации заказчики')


class OrganizationContractor(Organization):
    class QuerySet(Organization.QuerySet):
        def filter_by_user(self, user: User) -> 'OrganizationContractor.QuerySet':
            if user.is_superuser or user.is_staff:
                return self
            return self.filter(
                id__in=OrganizationContractorUserRole.objects.filter(user=user).values('organization_contractor')
            )

    class Manager(models.Manager.from_queryset(QuerySet)):
        def get_queryset(self) -> 'OrganizationContractor.QuerySet':
            return super().get_queryset().filter(is_contractor=True)

    objects = Manager()

    class Meta:
        proxy = True
        ordering = ['name']
        verbose_name = _('организация исполнитель')
        verbose_name_plural = _('организации исполнители')


class OrganizationContractorUserRole(models.Model):
    organization_contractor = models.ForeignKey(
        'main.OrganizationContractor', related_name='users_roles', on_delete=models.CASCADE,
        verbose_name=_('организация исполнитель'),
    )
    user = models.ForeignKey(
        'acc.User', related_name='organizations_contractors_roles', on_delete=models.CASCADE,
        verbose_name=_('пользователь'),
    )
    role = models.CharField(max_length=50, choices=Role.choices, verbose_name=_('роль'))

    class Meta:
        unique_together = [
            ['organization_contractor', 'user', 'role']
        ]
        verbose_name = _('роль пользователя')
        verbose_name_plural = _('роли пользователей')


@reversion.register(follow=['organization'])
class OrganizationProject(ModelDiffMixin, DatesModelBase):
    organization = models.ForeignKey(
        'main.OrganizationCustomer', on_delete=models.RESTRICT, related_name='projects',
        verbose_name=_('заказчик')
    )
    name = models.CharField(max_length=500, verbose_name=_('название'))
    description = models.TextField(null=True, blank=True, verbose_name=_('описание'))
    goals = models.TextField(null=True, blank=True, verbose_name=_('цели'))
    plan_description = models.TextField(null=True, blank=True, verbose_name=_('ресурсный план'))
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

    class Meta:
        ordering = ['name']
        verbose_name = _('проект')
        verbose_name_plural = _('проекты')

    class QuerySet(models.QuerySet):
        def filter_by_user(self, user: User) -> 'OrganizationProject.QuerySet':
            if user.is_superuser or user.is_staff:
                return self
            return self.filter(
                models.Q(organization__contractor__in=OrganizationContractor.objects.filter_by_user(user))
                | models.Q(id__in=OrganizationProjectUserRole.objects.filter(user=user).values('organization_project'))
            )

    class Manager(models.Manager.from_queryset(QuerySet)):
        @classmethod
        def get_queryset_prefetch_related(cls) -> List[str]:
            return ['organization', 'industry_sector', 'manager', 'modules']

    objects = Manager()

    def __str__(self):
        return self.name

    @property
    def modules_count(self) -> int:
        return len(self.modules.all())


class OrganizationProjectUserRole(ModelDiffMixin, models.Model):
    organization_project = models.ForeignKey(
        'main.OrganizationProject', related_name='users_roles', on_delete=models.CASCADE,
        verbose_name=_('проект'),
    )
    user = models.ForeignKey(
        'acc.User', related_name='organizations_projects_roles', on_delete=models.CASCADE,
        verbose_name=_('пользователь'),
    )
    role = models.CharField(max_length=50, choices=Role.choices, verbose_name=_('роль'))

    class Meta:
        unique_together = [
            ['organization_project', 'user', 'role']
        ]
        verbose_name = _('роль пользователя')
        verbose_name_plural = _('роли пользователей')

    def clean(self):
        from main.models._signals_receivers.project import OrganizationProjectUserRoleSignalsReceiver
        OrganizationProjectUserRoleSignalsReceiver(self).validate()


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
