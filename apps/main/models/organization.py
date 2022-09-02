from typing import List, Optional, TYPE_CHECKING

import reversion
from cacheops import invalidate_model
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from mptt import models as mptt_models
from mptt import querysets as mptt_querysets

from project.contrib.db.models import DatesModelBase, ModelDiffMixin
from project.contrib.is_call_from_admin import is_call_from_admin
from acc.models import User, Role
from main.models import permissions as main_permissions

if TYPE_CHECKING:
    from main.models.request import Request, RequestStatus, RequestRequirement, RequestRequirementStatus

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


@reversion.register()
class Organization(main_permissions.MainModelPermissionsMixin, ModelDiffMixin, DatesModelBase):
    name = models.CharField(max_length=500, db_index=True, verbose_name=_('название'))
    description = models.TextField(null=True, blank=True, verbose_name=_('описание'))
    is_customer = models.BooleanField(default=False, verbose_name=_('это заказчик?'))
    is_contractor = models.BooleanField(default=False, verbose_name=_('это исполнитель?'))

    class Meta:
        ordering = ['name']
        verbose_name = _('организация')
        verbose_name_plural = _('организации')

    class QuerySet(models.QuerySet):
        def filter_by_user(self, user: User):
            return self

    class Manager(models.Manager.from_queryset(QuerySet)):
        pass

    objects = Manager()

    def __str__(self):
        return self.name


@reversion.register(follow=['projects_as_customer'])
class OrganizationCustomer(Organization):
    permission_save = main_permissions.organization_customer_save
    permission_delete = main_permissions.organization_customer_delete

    class QuerySet(Organization.QuerySet):
        def filter_by_user(self, user: User):
            return self
            # TODO OrganizationCustomer.QuerySet.filter_by_user
            if user.is_superuser or user.is_staff:
                return self
            return self.filter(projects_as_customer__in=OrganizationProject.objects.filter_by_user(user))

    class Manager(models.Manager.from_queryset(QuerySet)):
        def get_queryset(self):
            return super().get_queryset().filter(is_customer=True)

    class Meta:
        proxy = True
        ordering = ['name']
        verbose_name = _('организация заказчик')
        verbose_name_plural = _('организации заказчики')

    objects = Manager()


@reversion.register(follow=['projects_as_contractor'])
class OrganizationContractor(Organization):
    permission_save = main_permissions.organization_contractor_save
    permission_delete = main_permissions.organization_contractor_delete

    class QuerySet(Organization.QuerySet):
        def filter_by_user(self, user: User):
            if user.is_superuser or user.is_staff:
                return self
            return self.filter(
                id__in=[
                    row.organization_contractor.id
                    for row in OrganizationContractorUserRole.objects.filter(user=user)
                ]
            )

    class Manager(models.Manager.from_queryset(QuerySet)):
        def get_queryset(self):
            return super().get_queryset().filter(is_contractor=True)

    class Meta:
        proxy = True
        ordering = ['name']
        verbose_name = _('организация исполнитель')
        verbose_name_plural = _('организации исполнители')

    objects = Manager()

    def get_user_roles(self, user: User) -> List[str]:
        if user.is_superuser or user.is_staff:
            return [Role.ADMIN.value]
        return [row.role for row in self.users_roles.filter(user=user)]


class OrganizationContractorUserRole(main_permissions.MainModelPermissionsMixin, models.Model):
    permission_save = main_permissions.organization_contractor_user_role_save
    permission_delete = main_permissions.organization_contractor_user_role_delete

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

    # def clean(self):
    #     if self.role == Role.ADMIN:
    #         raise ValidationError({'role': _('Вы не можете назначить администратора таким образом')})
    #     super().clean()


class OrganizationProjectStatus(models.TextChoices):
    DRAFT = 'draft', _('Черновик')
    IN_PROGRESS = 'in_progress', _('В работе')
    DONE = 'done', _('Успешно завершен')
    CLOSED = 'closed', _('Закрыт')


@reversion.register(follow=['organization_customer'])
class OrganizationProject(main_permissions.MainModelPermissionsMixin, ModelDiffMixin, DatesModelBase):
    permission_save = main_permissions.organization_project_save
    permission_delete = main_permissions.organization_project_delete

    organization_customer = models.ForeignKey(
        'main.OrganizationCustomer', on_delete=models.CASCADE, related_name='projects_as_customer',
        verbose_name=_('заказчик')
    )
    organization_contractor = models.ForeignKey(
        'main.OrganizationContractor', on_delete=models.CASCADE, related_name='projects_as_contractor',
        verbose_name=_('исполнитель')
    )
    status = models.CharField(
        max_length=50, default=OrganizationProjectStatus.DRAFT, choices=OrganizationProjectStatus.choices,
        verbose_name=_('статус')
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
    manager_pfm = models.ForeignKey(
        'acc.User', related_name='organizations_projects_as_pfm', null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name=_('РПП')
    )
    manager_pm = models.ForeignKey(
        'acc.User', related_name='organizations_projects_as_pm', null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name=_('РП')
    )

    class Meta:
        ordering = ['name']
        verbose_name = _('проект')
        verbose_name_plural = _('проекты')

    class QuerySet(models.QuerySet):
        def filter_by_user(self, user: User):
            if user.is_superuser or user.is_staff:
                return self
            return self.filter(
                models.Q(organization_contractor__in=OrganizationContractor.objects.filter_by_user(user))
                | models.Q(id__in=[
                    row.organization_project.id
                    for row in OrganizationProjectUserRole.objects.filter(user=user)
                ])
            )

    class Manager(models.Manager.from_queryset(QuerySet)):
        @classmethod
        def get_queryset_prefetch_related(cls) -> List[str]:
            return [
                'organization_customer', 'organization_contractor', 'industry_sector', 'manager_pfm', 'manager_pm',
                'users_roles', 'modules', 'modules__requests',
            ]

    objects = Manager()

    def __str__(self):
        return f'{self.name} ({self.organization_customer.name} <{self.organization_customer_id}>)'

    def clean(self):
        super().clean()
        errors = {}
        if self.manager_pfm and Role.PFM not in self.organization_contractor.get_user_roles(self.manager_pfm):
            errors['manager_pfm'] = _('Этот пользователь не может быть РПП на этом проекте')
        if self.manager_pm and Role.PM not in self.organization_contractor.get_user_roles(self.manager_pm):
            errors['manager_pm'] = _('Этот пользователь не может быть РП на этом проекте')
        if errors:
            if not is_call_from_admin():
                errors = {f'{k}_id': v for k, v in errors.items()}
            raise ValidationError(errors)

    @property
    def modules_count(self) -> int:
        return len(self.modules.all())

    def get_user_roles(self, user: User) -> List[str]:
        if user.is_superuser or user.is_staff:
            return [Role.ADMIN.value]
        if role := self.users_roles.filter(user=user).first():
            return [role.role]
        return self.organization_contractor.get_user_roles(user)

    def get_requests(self, status: Optional['RequestStatus'] = None) -> List['Request']:
        requests = []
        for module in self.modules.all():
            for request in module.requests.all():
                if not status or status == request.status:
                    requests.append(request)
        return requests

    def get_requests_count(self, status: Optional['RequestStatus'] = None) -> int:
        return len(self.get_requests(status))

    def get_requests_requirements(
            self,
            status: Optional['RequestRequirementStatus'] = None
    ) -> List['RequestRequirement']:
        requirements = []
        for module in self.modules.all():
            for request in module.requests.all():
                for requirement in request.requirements.all():
                    if not status or status == requirement.status:
                        requirements.append(request)
        return requirements

    def get_requests_requirements_count(self, status: Optional['RequestRequirementStatus'] = None) -> int:
        return len(self.get_requests_requirements(status))


class OrganizationProjectUserRole(main_permissions.MainModelPermissionsMixin, ModelDiffMixin, models.Model):
    permission_save = main_permissions.organization_project_user_role_save
    permission_delete = main_permissions.organization_project_user_role_delete

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
        super().clean()
        # if self.role == Role.ADMIN:
        #     raise ValidationError({'role': _('Вы не можете назначить администратора таким образом')})
        if not OrganizationContractorUserRole.objects.filter(
                organization_contractor=self.organization_project.organization_contractor,
                user=self.user
        ).exists():
            raise ValidationError(_('Пользователю не назначена роль в организации исполнителе'))


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
    #     super().clean()
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

    def __str__(self):
        return f'{self.name} ({self.organization_project.name} <{self.organization_project_id} >)'
