from typing import List, Dict, Any

import reversion
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _

from project.contrib.db.models import DatesModelBase
from acc.models import User
from cv.models import CV


class ExperienceYears(models.IntegerChoices):
    ZERO = 1, _('Менее года')
    THREE = 3, _('1 – 3 года')
    FIVE = 5, _('3 - 5 лет')
    ONE_HUNDRED = 100, _('Более 5 лет')


class WorkLocationType(models.TextChoices):
    OFFICE = 'office', _('Офис')
    HOME = 'home', _('Удаленная работа')
    MIXED = 'mixed', _('Офис или удаленная')


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

    class Meta:
        ordering = ['name']
        verbose_name = _('проект организации')
        verbose_name_plural = _('проекты организаций')

    def __str__(self):
        return self.name


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

    def __str__(self):
        return self.name


@reversion.register()
class RequestType(models.Model):
    name = models.CharField(max_length=500, verbose_name=_('название'))

    class Meta:
        ordering = ['name']
        verbose_name = _('тип проектного запроса')
        verbose_name_plural = _('типы проектных запросов')

    def __str__(self):
        return self.name


class RequestStatus(models.TextChoices):
    DRAFT = 'draft', _('Черновик')
    IN_PROGRESS = 'in_progress', _('В работе')
    DONE = 'done', _('Успешно завершен')
    CLOSED = 'closed', _('Закрыт')


class RequestPriority(models.IntegerChoices):
    MAJOR = 10, _('Высокий')
    DEFAULT = 20, _('Обычный')
    MINOR = 30, _('Низкий')


@reversion.register(follow=['requirements'])
class Request(DatesModelBase):
    type = models.ForeignKey(
        'main.RequestType', related_name='requests', null=True, blank=True, on_delete=models.CASCADE,
        verbose_name=_('тип запроса')
    )
    description = models.TextField(null=True, blank=True, verbose_name=_('описание'))
    customer = models.ForeignKey(
        'main.Organization', on_delete=models.CASCADE, related_name='requests',
        limit_choices_to={'is_customer': True},
        verbose_name=_('заказчик'), help_text=_('организации отмеченные как заказчики')
    )
    status = models.CharField(
        max_length=50, default=RequestStatus.DRAFT, choices=RequestStatus.choices,
        verbose_name=_('статус')
    )
    priority = models.IntegerField(
        default=RequestPriority.DEFAULT, choices=RequestPriority.choices,
        verbose_name=_('приоритет')
    )
    industry_sector = models.ForeignKey(
        'dictionary.IndustrySector', related_name='requests', null=True, blank=True, on_delete=models.RESTRICT,
        verbose_name=_('отрасль')
    )
    project = models.ForeignKey(
        'main.Project', related_name='requests', null=True, blank=True, on_delete=models.RESTRICT,
        verbose_name=_('проект')
    )
    start_date = models.DateField(null=True, blank=True, verbose_name=_('дата начала'))
    deadline_date = models.DateField(null=True, blank=True, verbose_name=_('срок'))
    resource_manager = models.ForeignKey(
        'acc.User', null=True, blank=True, on_delete=models.RESTRICT,
        related_name='requests_as_resource_manager', verbose_name=_('рес. менеджер')
    )
    recruiter = models.ForeignKey(
        'acc.User', null=True, blank=True, on_delete=models.RESTRICT,
        related_name='requests_as_recruiter', verbose_name=_('отв. рекрутер')
    )

    class Meta:
        ordering = ['priority', '-id']
        verbose_name = _('проектный запрос')
        verbose_name_plural = _('проектные запросы')

    class QuerySet(models.QuerySet):
        def filter_by_user(self, user: User):
            return self

    class Manager(models.Manager.from_queryset(QuerySet)):
        @classmethod
        def get_queryset_prefetch_related(cls) -> List[str]:
            return [
                *cls.get_queryset_prefetch_related_self(),
                *cls.get_queryset_prefetch_related_requirements(),
            ]

        @classmethod
        def get_queryset_prefetch_related_self(cls) -> List[str]:
            return [
                'type', 'customer', 'industry_sector', 'project', 'resource_manager', 'recruiter', 'requirements',
            ]

        @classmethod
        def get_queryset_prefetch_related_requirements(cls) -> List[str]:
            return [
                f'requirements__{f}'
                for f in RequestRequirement.objects.get_queryset_prefetch_related()
            ]

    objects = Manager()

    def __str__(self):
        return self.id_verbose

    @property
    def id_verbose(self) -> str:
        return str(self.id).zfill(7)

    @property
    def requirements_count(self) -> int:
        return len(self.requirements.all())


@reversion.register(follow=['request', 'competencies'])
class RequestRequirement(DatesModelBase):
    request = models.ForeignKey(
        'main.Request', on_delete=models.CASCADE, related_name='requirements',
        verbose_name=_('запрос')
    )
    sorting = models.IntegerField(default=0, verbose_name=_('сортировка'))
    name = models.CharField(max_length=1000, null=True, blank=True, verbose_name=_('название'))
    description = models.TextField(null=True, blank=True, verbose_name=_('описание'))
    position = models.ForeignKey(
        'dictionary.Position', related_name='requests_requirements', null=True, blank=True, on_delete=models.RESTRICT,
        verbose_name=_('должность')
    )
    experience_years = models.FloatField(null=True, blank=True, verbose_name=_('опыт лет'), help_text='float')
    count = models.IntegerField(null=True, blank=True, verbose_name=_('количество'))
    type_of_employment = models.ForeignKey(
        'dictionary.TypeOfEmployment', related_name='requests_requirements', null=True, blank=True,
        on_delete=models.RESTRICT, verbose_name=_('тип занятости')
    )
    work_location_city = models.ForeignKey(
        'dictionary.City', related_name='requests_requirements', null=True, blank=True, on_delete=models.SET_NULL,
        verbose_name=_('город')
    )
    work_location_address = models.CharField(max_length=1000, null=True, blank=True, verbose_name=_('адрес'))
    max_price = models.FloatField(null=True, blank=True, verbose_name=_('макс. цена'))

    cv_list = models.ManyToManyField(
        'cv.CV', related_name='requests_requirements', blank=True,
        verbose_name=_('анкеты')
    )

    class Meta:
        ordering = ['sorting', 'name']
        verbose_name = _('требование проектного запроса')
        verbose_name_plural = _('требования проектного запроса')

    class QuerySet(models.QuerySet):
        def filter_by_user(self, user: User):
            return self.filter(request__in=Request.objects.filter_by_user(user))

    class Manager(models.Manager.from_queryset(QuerySet)):
        @classmethod
        def get_queryset_prefetch_related(cls) -> List[str]:
            return [
                *cls.get_queryset_prefetch_related_self(),
                *cls.get_queryset_prefetch_related_cv_list(),
            ]

        @classmethod
        def get_queryset_prefetch_related_self(cls) -> List[str]:
            return [
                'position', 'type_of_employment', 'work_location_city', 'work_location_city__country', 'competencies',
                'competencies__competence', 'cv_list',
            ]

        @classmethod
        def get_queryset_prefetch_related_cv_list(cls) -> List[str]:
            return [
                f'cv_list__{f}'
                for f in CV.objects.get_queryset_prefetch_related()
            ]

    objects = Manager()


@reversion.register(follow=['request_requirement'])
class RequestRequirementCompetence(DatesModelBase):
    request_requirement = models.ForeignKey(
        'main.RequestRequirement', on_delete=models.CASCADE, related_name='competencies',
        verbose_name=_('требование проектного запроса')
    )
    competence = models.ForeignKey('dictionary.Competence', on_delete=models.RESTRICT, verbose_name=_('компетенция'))
    experience_years = models.IntegerField(
        null=True, blank=True, choices=ExperienceYears.choices,
        verbose_name=_('опыт лет')
    )
    sorting = models.IntegerField(default=0, verbose_name=_('сортировка'))

    class Meta:
        ordering = ['sorting', '-experience_years', 'id']
        unique_together = [
            ['request_requirement', 'competence']
        ]
        verbose_name = _('компетенция')
        verbose_name_plural = _('компетенции')

    class QuerySet(models.QuerySet):
        def filter_by_user(self, user: User):
            return self.filter(request_requirement__in=RequestRequirement.objects.filter_by_user(user))

    class Manager(models.Manager.from_queryset(QuerySet)):
        @transaction.atomic
        def set_for_request_requirement(
                self,
                request_requirement: RequestRequirement,
                data: List[Dict[str, Any]]
        ) -> List['RequestRequirementCompetence']:
            self.filter(request_requirement=request_requirement).delete()
            return self.bulk_create([
                self.model(
                    request_requirement=request_requirement,
                    **{k: v for k, v in row.items() if k not in ['years']}
                )
                for row in data
            ])

    objects = Manager()

    def __str__(self):
        return f'< {self.request_requirement_id} / {self.id} >'
