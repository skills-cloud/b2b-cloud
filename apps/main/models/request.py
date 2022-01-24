from typing import List, Dict, Any, Union

import reversion
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

from project.contrib.db.models import DatesModelBase, ModelDiffMixin
from acc.models import User
from cv.models import CV
from main.models.base import ExperienceYears
from main.models.organization import OrganizationProjectCardItem
from main.models.module import Module

__all__ = [
    'RequestType',
    'RequestStatus',
    'RequestPriority',
    'Request',
    'RequestRequirementStatus',
    'RequestRequirement',
    'RequestRequirementCvStatus',
    'RequestRequirementCv',
    'RequestRequirementCompetence',
    'TimeSheetRow',
]


@reversion.register()
class RequestType(models.Model):
    name = models.CharField(max_length=500, verbose_name=_('название'))

    class Meta:
        ordering = ['name']
        verbose_name = _('запросы / тип запроса')
        verbose_name_plural = _('запросы / типы запросов')

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
    module = models.ForeignKey(
        'main.Module', related_name='requests', on_delete=models.CASCADE,
        verbose_name=_('модуль')
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
    start_date = models.DateField(null=True, blank=True, verbose_name=_('дата начала'))
    deadline_date = models.DateField(null=True, blank=True, verbose_name=_('срок'))
    manager_rm = models.ForeignKey(
        'acc.User', related_name='requests_as_rm', null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name=_('РМ')
    )

    class Meta:
        ordering = ['priority', '-id']
        verbose_name = _('запрос')
        verbose_name_plural = _('запросы')

    class QuerySet(models.QuerySet):
        def filter_by_user(self, user: User):
            return self.filter(module__in=Module.objects.filter_by_user(user))

    class Manager(models.Manager.from_queryset(QuerySet)):
        @classmethod
        def get_queryset_prefetch_related(cls) -> List[str]:
            return [
                *cls.get_queryset_prefetch_related_self(),
                *cls.get_queryset_prefetch_related_requirements(),
                *cls.get_queryset_prefetch_related_module(),
            ]

        @classmethod
        def get_queryset_prefetch_related_self(cls) -> List[str]:
            return [
                'type', 'industry_sector', 'manager_rm',
            ]

        @classmethod
        def get_queryset_prefetch_related_requirements(cls) -> List[str]:
            return [
                'requirements',
                *[
                    f'requirements__{f}'
                    for f in RequestRequirement.objects.get_queryset_prefetch_related()
                ]
            ]

        @classmethod
        def get_queryset_prefetch_related_module(cls) -> List[str]:
            return [
                'module',
                *[
                    f'module__{f}'
                    for f in Module.objects.get_queryset_prefetch_related()
                ]
            ]

    objects = Manager()

    def clean(self):
        if self.manager_rm:
            if not self.module.organization_project.organization_contractor.get_user_roles(self.manager_rm):
                raise ValidationError({
                    'manager_rm_id': _('Этот пользователь не может быть РМ для этого запроса')
                })

    def __str__(self):
        return f'{self.id_verbose} < {self.id} / {self.module_id} >'

    @property
    def id_verbose(self) -> str:
        return str(self.id).zfill(7) if self.id else None

    @property
    def requirements_count(self) -> int:
        return len(self.requirements.all())


class RequestRequirementStatus(models.TextChoices):
    IN_PROGRESS = 'in_progress', _('В работе')
    DONE = 'done', _('Успешно завершен')


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
        verbose_name = _('запросы / требование')
        verbose_name_plural = _('запросы / требования')

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
                'cv_links', 'cv_links__cv',
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

    def status(self) -> RequestRequirementStatus:
        cv_done_count = sum([
            1
            for self_cv in self.cv_links.all()
            if self_cv.status == RequestRequirementCvStatus.WORKER
        ])
        if self.count <= cv_done_count:
            return RequestRequirementStatus.DONE
        return RequestRequirementStatus.IN_PROGRESS


class RequestRequirementCvStatus(models.TextChoices):
    PRE_CANDIDATE = 'pre-candidate'
    CANDIDATE = 'candidate'
    CANCELED = 'canceled'
    WORKER = 'worker'


@reversion.register(follow=['request_requirement'])
class RequestRequirementCv(ModelDiffMixin, DatesModelBase):
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

    rating = models.IntegerField(
        null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_('рейтинг')
    )
    attributes = models.JSONField(
        default=dict, verbose_name=_('доп. атрибуты'),
        help_text=_('если вы не до конца понимаете назначение этого поля, вам лучше избежать редактирования')
    )

    class Meta:
        ordering = ['-id']
        unique_together = [
            ['request_requirement', 'cv']
        ]
        verbose_name = _('анкета')
        verbose_name_plural = _('анкеты')

    class QuerySet(models.QuerySet):
        def filter_by_user(self, user: User):
            return self.filter(request_requirement__in=RequestRequirement.objects.filter_by_user(user))

    class Manager(models.Manager.from_queryset(QuerySet)):
        ...

    objects = Manager()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.id} < {self.cv_id} / {self.request_requirement_id} >'

    @property
    def organization_project_card_items(self) -> List[Dict[str, Union[str, int]]]:
        return self.attributes.get('organization_project_card_items') or []

    def clean(self):
        organization_project_card_items = (self.attributes or {}).get('organization_project_card_items')
        if not organization_project_card_items:
            return
        cards_items_ids = [row['id'] for row in organization_project_card_items]
        cards_items_qs = OrganizationProjectCardItem.objects_flat.filter(
            id__in=cards_items_ids,
            module__organization_project_id=self.request_requirement.request.module.organization_project_id
        )
        if len(cards_items_ids) != cards_items_qs.workers_count():
            raise ValidationError({
                'attributes.organization_project_card_items': _('Неверно задана ID минимум одной карточки')
            })


@reversion.register(follow=['request_requirement'])
class RequestRequirementCompetence(DatesModelBase):
    request_requirement = models.ForeignKey(
        'main.RequestRequirement', on_delete=models.CASCADE, related_name='competencies',
        verbose_name=_('требование проектного запроса')
    )
    competence = models.ForeignKey('dictionary.Competence', on_delete=models.CASCADE, verbose_name=_('компетенция'))
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


@reversion.register()
class TimeSheetRow(DatesModelBase):
    request = models.ForeignKey(
        'main.Request', on_delete=models.CASCADE, related_name='time_sheet_rows',
        verbose_name=_('проектный запрос')
    )
    cv = models.ForeignKey(
        'cv.CV', on_delete=models.RESTRICT, related_name='time_sheet_rows',
        verbose_name=_('анкета исполнителя')
    )
    date_from = models.DateField(default=timezone.now, db_index=True, verbose_name=_('дата начала работ'))
    date_to = models.DateField(null=True, blank=True, verbose_name=_('дата окончания работ'))
    task_name = models.CharField(max_length=1000, verbose_name=_('название задачи'))
    task_description = models.TextField(null=True, blank=True, verbose_name=_('описание задачи'))
    work_time = models.FloatField(verbose_name=_('затраченное время'))

    class QuerySet(models.QuerySet):
        def filter_by_user(self, user: User):
            return self.filter(request__in=Request.objects.filter_by_user(user))

    class Manager(models.Manager.from_queryset(QuerySet)):
        @transaction.atomic
        def create_for_cv(self, cv_ids: List[int], **kwargs) -> List['TimeSheetRow']:
            for_create = [
                self.model(cv_id=cv_id, **kwargs)
                for cv_id in cv_ids
            ]
            for o in for_create:
                o.clean()
            return self.bulk_create(for_create)

        @classmethod
        def get_queryset_prefetch_related(cls) -> List:
            return [
                'request', 'cv',
                *[
                    f'request__{f}'
                    for f in Request.objects.get_queryset_prefetch_related_self()
                ]
            ]

    class Meta:
        ordering = ['-date_from']
        index_together = [
            ['request', 'date_from'],
            ['request', 'task_name'],
        ]
        verbose_name = _('запросы / таймшиты')
        verbose_name_plural = _('запросы / таймшиты')

    objects = Manager()

    def __str__(self):
        return f'{self.task_name} < {self.id} / {self.request_id} >'

    def clean(self):
        if not CV.objects.filter(
                requests_requirements_links__request_requirement__request=self.request,
                id=self.cv_id,
        ).exists():
            raise ValidationError({
                'cv': _(f'Анкета <{self.cv_id}> не связана с требованием проектного запроса')
            })
