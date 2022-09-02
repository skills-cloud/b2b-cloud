import reversion
from typing import Optional, List

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from project.contrib.db.models import DatesModelBase, ModelDiffMixin
from acc.models import User
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
        verbose_name=_('customer'), help_text=_('general type if this field is left empty')
    )
    name = models.CharField(max_length=500, verbose_name=_('name'))
    description = models.TextField(null=True, blank=True, verbose_name=_('description'))

    class Meta:
        ordering = ['name']
        unique_together = [
            ['organization_customer', 'name']
        ]
        verbose_name = _('modules / fuctional point type')
        verbose_name_plural = _('modules / fuctional point types')

    class QuerySet(models.QuerySet):
        def filter_by_user(self, user: User):
            from main.models.organization import OrganizationCustomer
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
        verbose_name=_('difficulty level')
    )
    name = models.CharField(max_length=500, verbose_name=_('name'))
    factor = models.FloatField(default=1, verbose_name=_('factor'))
    sorting = models.IntegerField(default=0, verbose_name=_('sorting'))

    class Meta:
        ordering = ['sorting', 'id']
        unique_together = [
            ['fun_point_type', 'name']
        ]
        verbose_name = _('difficulty level')
        verbose_name_plural = _('difficulty levels')

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
        verbose_name=_('difficulty level')
    )
    position = models.ForeignKey(
        'dictionary.Position', related_name='fun_points_types_labor_estimates', on_delete=models.CASCADE,
        verbose_name=_('position')
    )
    hours = models.FloatField(default=1, verbose_name=_('standard'), help_text=_('in hours'))
    sorting = models.IntegerField(default=0, verbose_name=_('sorting'))

    class Meta:
        ordering = ['sorting', 'id']
        unique_together = [
            ['fun_point_type', 'position']
        ]
        verbose_name = _('labor standard')
        verbose_name_plural = _('labor standards')

    class QuerySet(models.QuerySet):
        def filter_by_user(self, user: User):
            return self.filter(fun_point_type__in=FunPointType.objects.filter_by_user(user))

    class Manager(models.Manager.from_queryset(QuerySet)):
        ...

    objects = Manager()


@reversion.register(follow=['fun_points', 'positions_labor_estimates'])
class Module(main_permissions.MainModelPermissionsMixin, ModelDiffMixin, DatesModelBase):
    permission_save = main_permissions.module_save
    permission_delete = main_permissions.module_delete

    organization_project = models.ForeignKey(
        'main.OrganizationProject', related_name='modules', on_delete=models.CASCADE,
        verbose_name=_('project')
    )
    name = models.CharField(max_length=500, verbose_name=_('name'))
    start_date = models.DateField(null=True, blank=True, verbose_name=_('start date'))
    deadline_date = models.DateField(null=True, blank=True, verbose_name=_('deadline'))
    work_days_count = models.IntegerField(
        null=True, blank=True, verbose_name=_('workdays count'),
        help_text=_('filled automatically based on a five day work week if left empty'
                    '<br>Mon-Fri deadline_date-start_date')
    )
    work_days_hours_count = models.IntegerField(default=8, verbose_name=_('workday hours count'))
    goals = models.TextField(null=True, blank=True, verbose_name=_('goals'))
    description = models.TextField(null=True, blank=True, verbose_name=_('description'))
    sorting = models.IntegerField(default=0, verbose_name=_('sorting'))

    class Meta:
        ordering = ['sorting', 'id']
        unique_together = [
            ['organization_project', 'name']
        ]
        verbose_name = _('module')
        verbose_name_plural = _('modules')

    class QuerySet(models.QuerySet):
        def filter_by_user(self, user: User):
            from main.models.organization import OrganizationProject
            return self.filter(organization_project__in=OrganizationProject.objects.filter_by_user(user))

    class Manager(models.Manager.from_queryset(QuerySet)):
        @classmethod
        def get_queryset_prefetch_related(cls) -> List[str]:
            return [
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
class ModuleFunPoint(main_permissions.MainModelPermissionsMixin, ModelDiffMixin, DatesModelBase):
    permission_save = main_permissions.module_fun_point_save
    permission_delete = main_permissions.module_fun_point_delete

    fun_point_type = models.ForeignKey(
        'main.FunPointType', related_name='fun_points', on_delete=models.RESTRICT,
        verbose_name=_('type')
    )
    module = models.ForeignKey(
        'main.Module', related_name='fun_points', on_delete=models.CASCADE,
        verbose_name=_('module')
    )
    difficulty_level = models.ForeignKey(
        'main.FunPointTypeDifficultyLevel', related_name='fun_points', null=True, blank=True, on_delete=models.SET_NULL,
        verbose_name=_('difficulty level')
    )
    name = models.CharField(max_length=500, verbose_name=_('name'))
    description = models.TextField(null=True, blank=True, verbose_name=_('description'))
    sorting = models.IntegerField(default=0, verbose_name=_('sorting'))

    class Meta:
        ordering = ['sorting', 'id']
        unique_together = [
            ['module', 'name']
        ]
        verbose_name = _('functional point')
        verbose_name_plural = _('functional points')

    class QuerySet(models.QuerySet):
        def filter_by_user(self, user: User):
            return self.filter(module__in=Module.objects.filter_by_user(user))

    class Manager(models.Manager.from_queryset(QuerySet)):
        ...

    objects = Manager()

    def clean(self):
        super().clean()
        if (
                self.fun_point_type.organization_customer_id
                and self.fun_point_type.organization_customer_id !=
                self.module.organization_project.organization_customer_id
        ):
            raise ValidationError({'fun_point_type': _(
                'Functional point must belong to the company that ordered the module or be commonly used')})
        if self.difficulty_level and self.fun_point_type_id != self.difficulty_level.fun_point_type_id:
            raise ValidationError({'difficulty_level': _('Difficulty level must belong to this functional point type')})

    @property
    def difficulty_factor(self) -> float:
        if self.difficulty_level:
            return self.difficulty_level.factor
        return 1.0


@reversion.register()
class ModulePositionLaborEstimate(main_permissions.MainModelPermissionsMixin, DatesModelBase):
    permission_save = main_permissions.module_position_labor_estimate_save
    permission_delete = main_permissions.module_position_labor_estimate_delete

    module = models.ForeignKey(
        'main.Module', related_name='positions_labor_estimates', on_delete=models.CASCADE,
        verbose_name=_('module')
    )
    position = models.ForeignKey(
        'dictionary.Position', related_name='modules_positions_labor_estimates', on_delete=models.CASCADE,
        verbose_name=_('position')
    )
    count = models.PositiveIntegerField(default=1, verbose_name=_('count'))
    hours = models.FloatField(default=1, verbose_name=_('man-hours'))
    sorting = models.IntegerField(default=0, verbose_name=_('sorting'))

    class Meta:
        ordering = ['sorting', 'id']
        unique_together = [
            ['module', 'position']
        ]
        verbose_name = _('labor standard')
        verbose_name_plural = _('labor standards')

    class QuerySet(models.QuerySet):
        def filter_by_user(self, user: User):
            return self.filter(module__in=Module.objects.filter_by_user(user))

    class Manager(models.Manager.from_queryset(QuerySet)):
        ...

    objects = Manager()
