from typing import List, Dict, Any

import reversion
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _

from project.contrib.db.models import DatesModelBase
from acc.models import User
from cv.models import CV
from main.models.base import Project, ExperienceYears
from main.models.organization import OrganizationProject

__all__ = [
    'RequestType',
    'RequestStatus',
    'RequestPriority',
    'Request',
    'RequestRequirement',
    'RequestRequirementCvStatus',
    'RequestRequirementCv',
    'RequestRequirementCompetence',
]


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
    organization_project = models.ForeignKey(
        'main.OrganizationProject', related_name='requests', on_delete=models.RESTRICT,
        verbose_name=_('проект заказчика')
    )
    type = models.ForeignKey(
        'main.RequestType', related_name='requests', null=True, blank=True, on_delete=models.CASCADE,
        verbose_name=_('тип запроса')
    )
    title = models.TextField(null=True, blank=True, verbose_name=_('заголовок (название или номер)'))
    description = models.TextField(null=True, blank=True, verbose_name=_('описание'))
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
        verbose_name=_('внутренний проект'),
        help_text=_('На текущий момент не используется.<br>Надо задавать связку с проектом заказчика')
    )
    start_date = models.DateField(null=True, blank=True, verbose_name=_('дата начала'))
    deadline_date = models.DateField(null=True, blank=True, verbose_name=_('срок'))
    manager = models.ForeignKey(
        'acc.User', related_name='requests_as_manager', null=True, blank=True,
        on_delete=models.RESTRICT, verbose_name=_('руководитель проекта')
    )
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
                *cls.get_queryset_prefetch_related_project(),
                *cls.get_queryset_prefetch_related_organization_project(),
            ]

        @classmethod
        def get_queryset_prefetch_related_self(cls) -> List[str]:
            return [
                'organization_project', 'type', 'industry_sector', 'project', 'resource_manager', 'recruiter',
                'requirements',
            ]

        @classmethod
        def get_queryset_prefetch_related_requirements(cls) -> List[str]:
            return [
                f'requirements__{f}'
                for f in RequestRequirement.objects.get_queryset_prefetch_related()
            ]

        @classmethod
        def get_queryset_prefetch_related_project(cls) -> List[str]:
            return [
                f'project__{f}'
                for f in Project.objects.get_queryset_prefetch_related()
            ]

        @classmethod
        def get_queryset_prefetch_related_organization_project(cls) -> List[str]:
            return [
                f'organization_project__{f}'
                for f in OrganizationProject.objects.get_queryset_prefetch_related()
            ]

    objects = Manager()

    def __str__(self):
        return f'{self.id_verbose} < {self.id} / {self.organization_project_id} >'

    @property
    def id_verbose(self) -> str:
        return str(self.id).zfill(7)

    @property
    def requirements_count(self) -> int:
        return len(self.requirements.all())


@reversion.register(follow=['request', 'competencies', 'cv_links'])
class RequestRequirement(DatesModelBase):
    request = models.ForeignKey(
        'main.Request', on_delete=models.CASCADE, related_name='requirements',
        verbose_name=_('проектный запрос')
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
    date_from = models.DateField(null=True, blank=True, verbose_name=_('дата с'))
    date_to = models.DateField(null=True, blank=True, verbose_name=_('дата по'))

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
                'request', 'position', 'type_of_employment', 'work_location_city', 'work_location_city__country',
                'competencies', 'competencies__competence',
            ]

        @classmethod
        def get_queryset_prefetch_related_cv_list(cls) -> List[str]:
            return [
                'cv_links', 'cv_links__organization_project_card_items', 'cv_links__cv',
                *[
                    f'cv_links__cv__{f}'
                    for f in CV.objects.get_queryset_prefetch_related()
                ]
            ]

    objects = Manager()

    def __str__(self):
        return f'{self.name} < {self.id} / {self.request_id} >'

    @property
    def cv_list_ids(self) -> List[int]:
        return [cv_link.cv_id for cv_link in self.cv_links.all()]


class RequestRequirementCvStatus(models.TextChoices):
    PRE_CANDIDATE = 'pre-candidate'
    CANDIDATE = 'candidate'
    CANCELED = 'canceled'
    WORKER = 'worker'


@reversion.register(follow=['request_requirement'])
class RequestRequirementCv(DatesModelBase):
    """
    Есть сигналы
    """
    request_requirement = models.ForeignKey(
        'main.RequestRequirement', on_delete=models.CASCADE, related_name='cv_links',
        verbose_name=_('требование проектного запроса')
    )
    cv = models.ForeignKey(
        'cv.CV', on_delete=models.CASCADE, related_name='requests_requirements_links',
        verbose_name=_('анкета')
    )
    status = models.CharField(
        max_length=50, choices=RequestRequirementCvStatus.choices, default=RequestRequirementCvStatus.CANDIDATE,
        verbose_name=_('статус')
    )
    date_from = models.DateField(null=True, blank=True, verbose_name=_('участие в проекте с'))
    date_to = models.DateField(null=True, blank=True, verbose_name=_('участие в проекте по'))

    organization_project_card_items = models.ManyToManyField(
        'main.OrganizationProjectCardItem', blank=True,
        verbose_name=_('карточки проекта организации')
    )

    class Meta:
        ordering = ['-id']
        unique_together = [
            ['request_requirement', 'cv']
        ]
        verbose_name = _('анкета требования проектного запроса')
        verbose_name_plural = _('анкеты требования проектного запроса')

    def __str__(self):
        return f'{self.id} < {self.cv_id} / {self.request_requirement_id} >'


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
