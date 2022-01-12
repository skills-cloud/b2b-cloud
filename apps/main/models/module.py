import reversion
from typing import Optional, List

from django.core.exceptions import ValidationError, PermissionDenied
from django.db import models
from django.utils.translation import gettext_lazy as _

from project.contrib.db.models import DatesModelBase, ModelDiffMixin
from acc.models import User
from main.models.organization import OrganizationCustomer
from main.models import permissions as main_permissions

__all__ = [
    'FunPointType',
    'FunPointTypeDifficultyLevel',
    'FunPointTypePositionLaborEstimate',
    'ModuleFunPoint',
    'Module',
    'ModulePositionLaborEstimate',
]

from project.contrib.middleware.request import get_current_user


@reversion.register(follow=['difficulty_levels', 'positions_labor_estimates'])
class FunPointType(main_permissions.MainModelPermissionsMixin, ModelDiffMixin, DatesModelBase):
    permission_save = main_permissions.fun_point_type_save
    permission_delete = main_permissions.fun_point_type_delete

    organization_customer = models.ForeignKey(
        'main.OrganizationCustomer', related_name='fun_points_types', null=True, blank=True, on_delete=models.CASCADE,
        verbose_name=_('заказчик'), help_text=_('глобальный тип, если оставить это поле пустым')
    )
    name = models.CharField(max_length=500, verbose_name=_('название'))
    description = models.TextField(null=True, blank=True, verbose_name=_('описание'))

    class Meta:
        ordering = ['name']
        unique_together = [
            ['organization_customer', 'name']
        ]
        verbose_name = _('модули / тип функциональной точки')
        verbose_name_plural = _('модули / типы функциональных точек')

    class QuerySet(models.QuerySet):
        def filter_by_user(self, user: User) -> 'FunPointType.QuerySet':
            if user.is_superuser:
                return self
            return self.filter(
                models.Q(organization_customer__isnull=True)
                | models.Q(organization_customer__in=OrganizationCustomer.objects.filter_by_user(user))
            )

    class Manager(models.Manager.from_queryset(QuerySet)):
        @classmethod
        def get_queryset_prefetch_related(cls) -> List[str]:
            return [
                'organization_customer',
                'difficulty_levels', 'positions_labor_estimates', 'positions_labor_estimates__position'
            ]

    objects = Manager()

    def __str__(self):
        name = []
        if self.organization_customer:
            name.append(self.organization_customer.name)
        return ' / '.join([*name, self.name])


@reversion.register()
class FunPointTypeDifficultyLevel(main_permissions.MainModelPermissionsMixin, ModelDiffMixin, DatesModelBase):
    permission_save = main_permissions.fun_point_type_difficulty_level_save
    permission_delete = main_permissions.fun_point_type_difficulty_level_delete

    fun_point_type = models.ForeignKey(
        'main.FunPointType', related_name='difficulty_levels', on_delete=models.CASCADE,
        verbose_name=_('уровень сложности')
    )
    name = models.CharField(max_length=500, verbose_name=_('название'))
    factor = models.FloatField(default=1, verbose_name=_('коэффициент'))
    sorting = models.IntegerField(default=0, verbose_name=_('сортировка'))

    class Meta:
        ordering = ['sorting', 'id']
        unique_together = [
            ['fun_point_type', 'name']
        ]
        verbose_name = _('уровень сложности')
        verbose_name_plural = _('уровни сложности')

    class QuerySet(models.QuerySet):
        def filter_by_user(self, user: User):
            return self.filter(fun_point_type__in=FunPointType.objects.filter_by_user(user))

    class Manager(models.Manager.from_queryset(QuerySet)):
        ...

    objects = Manager()

    def __str__(self):
        return ' / '.join([
            self.fun_point_type.name,
            self.name,
        ])


@reversion.register()
class FunPointTypePositionLaborEstimate(main_permissions.MainModelPermissionsMixin, ModelDiffMixin, DatesModelBase):
    permission_save = main_permissions.fun_point_type_difficulty_level_save
    permission_delete = main_permissions.fun_point_type_difficulty_level_delete

    fun_point_type = models.ForeignKey(
        'main.FunPointType', related_name='positions_labor_estimates', on_delete=models.CASCADE,
        verbose_name=_('уровень сложности')
    )
    position = models.ForeignKey(
        'dictionary.Position', related_name='fun_points_types_labor_estimates', on_delete=models.CASCADE,
        verbose_name=_('должность')
    )
    hours = models.FloatField(default=1, verbose_name=_('норматив'), help_text=_('в часах'))
    sorting = models.IntegerField(default=0, verbose_name=_('сортировка'))

    class Meta:
        ordering = ['sorting', 'id']
        unique_together = [
            ['fun_point_type', 'position']
        ]
        verbose_name = _('норматив трудозатрат')
        verbose_name_plural = _('нормативы трудозатрат')

    class QuerySet(models.QuerySet):
        def filter_by_user(self, user: User):
            return self

    class Manager(models.Manager.from_queryset(QuerySet)):
        ...

    objects = Manager()


@reversion.register(follow=['fun_points', 'positions_labor_estimates'])
class Module(ModelDiffMixin, DatesModelBase):
    organization_project = models.ForeignKey(
        'main.OrganizationProject', related_name='modules', on_delete=models.CASCADE,
        verbose_name=_('проект')
    )
    name = models.CharField(max_length=500, verbose_name=_('название'))
    start_date = models.DateField(null=True, blank=True, verbose_name=_('дата начала'))
    deadline_date = models.DateField(null=True, blank=True, verbose_name=_('срок'))
    work_days_count = models.IntegerField(
        null=True, blank=True, verbose_name=_('кол-во рабочих дней'),
        help_text=_('если пусто, заполнится автоматически из расчета пятидневной рабочей недели'
                    '<br>ПН-ПТ deadline_date-start_date')
    )
    work_days_hours_count = models.IntegerField(default=8, verbose_name=_('кол-во рабочих часов в рабочем дне'))
    manager = models.ForeignKey(
        'acc.User', related_name='modules', null=True, blank=True,
        on_delete=models.RESTRICT, verbose_name=_('руководитель')
    )
    goals = models.TextField(null=True, blank=True, verbose_name=_('цели'))
    description = models.TextField(null=True, blank=True, verbose_name=_('описание'))
    sorting = models.IntegerField(default=0, verbose_name=_('сортировка'))

    class Meta:
        ordering = ['sorting', 'id']
        unique_together = [
            ['organization_project', 'name']
        ]
        verbose_name = _('модуль')
        verbose_name_plural = _('модули')

    class QuerySet(models.QuerySet):
        def filter_by_user(self, user: User) -> 'Module.QuerySet':
            return self

    class Manager(models.Manager.from_queryset(QuerySet)):
        @classmethod
        def get_queryset_prefetch_related(cls) -> List[str]:
            return [
                'manager',
                'organization_project', 'organization_project__organization_customer',
                'positions_labor_estimates', 'positions_labor_estimates__position',
                *cls.get_queryset_fun_points_prefetch_related(),
            ]

        @classmethod
        def get_queryset_fun_points_prefetch_related(cls) -> List[str]:
            return [
                'fun_points', 'fun_points__difficulty_level',
                *[f'fun_points__fun_point_type__{f}' for f in FunPointType.objects.get_queryset_prefetch_related()]
            ]

    objects = Manager()

    def __str__(self):
        return ' / '.join([
            # self.organization_project.name,
            self.name,
        ])

    @property
    def difficulty_factor(self) -> Optional[float]:
        from main.services.module import get_module_difficulty_factor
        return get_module_difficulty_factor(self)


@reversion.register()
class ModuleFunPoint(ModelDiffMixin, DatesModelBase):
    fun_point_type = models.ForeignKey(
        'main.FunPointType', related_name='fun_points', on_delete=models.RESTRICT,
        verbose_name=_('тип')
    )
    module = models.ForeignKey(
        'main.Module', related_name='fun_points', on_delete=models.CASCADE,
        verbose_name=_('модуль')
    )
    difficulty_level = models.ForeignKey(
        'main.FunPointTypeDifficultyLevel', related_name='fun_points', null=True, blank=True, on_delete=models.SET_NULL,
        verbose_name=_('уровень сложности')
    )
    name = models.CharField(max_length=500, verbose_name=_('название'))
    description = models.TextField(null=True, blank=True, verbose_name=_('описание'))
    sorting = models.IntegerField(default=0, verbose_name=_('сортировка'))

    class Meta:
        ordering = ['sorting', 'id']
        unique_together = [
            ['module', 'name']
        ]
        verbose_name = _('функциональная точка')
        verbose_name_plural = _('функциональные точки')

    class QuerySet(models.QuerySet):
        def filter_by_user(self, user: User):
            return self

    class Manager(models.Manager.from_queryset(QuerySet)):
        ...

    objects = Manager()

    def clean(self):
        if (
                self.fun_point_type.organization_customer_id
                and self.fun_point_type.organization_customer_id !=
                self.module.organization_project.organization_customer_id
        ):
            raise ValidationError({'fun_point_type': _(
                'Ф-я точка должна принадлежать компании заказчику проекта модуля или быть общеупотребимой')})
        if self.difficulty_level and self.fun_point_type_id != self.difficulty_level.fun_point_type_id:
            raise ValidationError({'difficulty_level': _('Уровень сложности должен принадлежать этому типу ф-й точки')})

    @property
    def difficulty_factor(self) -> float:
        if self.difficulty_level:
            return self.difficulty_level.factor
        return 1.0


@reversion.register()
class ModulePositionLaborEstimate(DatesModelBase):
    module = models.ForeignKey(
        'main.Module', related_name='positions_labor_estimates', on_delete=models.CASCADE,
        verbose_name=_('модуль')
    )
    position = models.ForeignKey(
        'dictionary.Position', related_name='modules_positions_labor_estimates', on_delete=models.CASCADE,
        verbose_name=_('должность')
    )
    count = models.PositiveIntegerField(default=1, verbose_name=_('кол-во'))
    hours = models.FloatField(default=1, verbose_name=_('чел/часов'))
    sorting = models.IntegerField(default=0, verbose_name=_('сортировка'))

    class Meta:
        ordering = ['sorting', 'id']
        unique_together = [
            ['module', 'position']
        ]
        verbose_name = _('норматив трудозатрат')
        verbose_name_plural = _('нормативы трудозатрат')

    class QuerySet(models.QuerySet):
        def filter_by_user(self, user: User):
            return self

    class Manager(models.Manager.from_queryset(QuerySet)):
        ...

    objects = Manager()
