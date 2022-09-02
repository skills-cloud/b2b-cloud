from typing import List, Dict, Any, Union

import reversion
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

from project.contrib.db.models import DatesModelBase, ModelDiffMixin
from project.contrib.is_call_from_admin import is_call_from_admin
from acc.models import User
from cv.models import CV
from main.models.base import ExperienceYears
from main.models.module import Module
from main.models.organization import OrganizationProjectCardItem
from main.models import permissions as main_permissions

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
    name = models.CharField(max_length=500, verbose_name=_('name'))

    class Meta:
        ordering = ['name']
        verbose_name = _('requests / request type')
        verbose_name_plural = _('requests / request types')

    def __str__(self):
        return self.name


class RequestStatus(models.TextChoices):
    DRAFT = 'draft', _('Draft')
    IN_PROGRESS = 'in_progress', _('In progress')
    DONE = 'done', _('Successfully completed')
    CLOSED = 'closed', _('Closed')


class RequestPriority(models.IntegerChoices):
    MAJOR = 10, _('Major')
    DEFAULT = 20, _('Default')
    MINOR = 30, _('Minor')


@reversion.register(follow=['requirements'])
class Request(main_permissions.MainModelPermissionsMixin, DatesModelBase):
    permission_save = main_permissions.request_save
    permission_delete = main_permissions.request_delete

    module = models.ForeignKey(
        'main.Module', related_name='requests', on_delete=models.CASCADE,
        verbose_name=_('module')
    )
    type = models.ForeignKey(
        'main.RequestType', related_name='requests', null=True, blank=True, on_delete=models.CASCADE,
        verbose_name=_('request type')
    )
    title = models.TextField(null=True, blank=True, verbose_name=_('header (name or number)'))
    description = models.TextField(null=True, blank=True, verbose_name=_('description'))
    status = models.CharField(
        max_length=50, default=RequestStatus.DRAFT, choices=RequestStatus.choices,
        verbose_name=_('status')
    )
    priority = models.IntegerField(
        default=RequestPriority.DEFAULT, choices=RequestPriority.choices,
        verbose_name=_('priority')
    )
    industry_sector = models.ForeignKey(
        'dictionary.IndustrySector', related_name='requests', null=True, blank=True, on_delete=models.RESTRICT,
        verbose_name=_('industry')
    )
    start_date = models.DateField(null=True, blank=True, verbose_name=_('start date'))
    deadline_date = models.DateField(null=True, blank=True, verbose_name=_('deadline'))
    manager_rm = models.ForeignKey(
        'acc.User', related_name='requests_as_rm', null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name=_('RM')
    )

    class Meta:
        ordering = ['priority', '-id']
        verbose_name = _('request')
        verbose_name_plural = _('requests')

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
        super().clean()
        errors = {}
        if self.manager_rm:
            if not self.module.organization_project.organization_contractor.get_user_roles(self.manager_rm):
                errors['manager_rm'] = _('This user cannot be set as resource manager of this request')
        if errors:
            if not is_call_from_admin():
                errors = {f'{k}_id': v for k, v in errors.items()}
            raise ValidationError(errors)

    def __str__(self):
        return f'{self.title} <{self.id}> / {self.module.name} /  {self.module.organization_project.name}'

    @property
    def id_verbose(self) -> str:
        return str(self.id).zfill(7) if self.id else None

    @property
    def requirements_count(self) -> int:
        return len(self.requirements.all())


class RequestRequirementStatus(models.TextChoices):
    OPEN = 'open', _('Open')
    CLOSED = 'closed', _('Closed')
    IN_PROGRESS = 'in_progress', _('In progress')
    DONE = 'done', _('Successfully completed')


@reversion.register(follow=['request', 'competencies', 'cv_links'])
class RequestRequirement(main_permissions.MainModelPermissionsMixin, DatesModelBase):
    permission_save = main_permissions.request_requirement_save
    permission_delete = main_permissions.request_requirement_delete

    request = models.ForeignKey(
        'main.Request', on_delete=models.CASCADE, related_name='requirements',
        verbose_name=_('request')
    )
    status = models.CharField(
        max_length=50, default=RequestRequirementStatus.OPEN, choices=RequestRequirementStatus.choices,
        verbose_name=_('status')
    )
    sorting = models.IntegerField(default=0, verbose_name=_('sorting'))
    name = models.CharField(max_length=1000, null=True, blank=True, verbose_name=_('name'))
    description = models.TextField(null=True, blank=True, verbose_name=_('description'))
    position = models.ForeignKey(
        'dictionary.Position', related_name='requests_requirements', null=True, blank=True, on_delete=models.CASCADE,
        verbose_name=_('position')
    )
    experience_years = models.FloatField(null=True, blank=True, verbose_name=_('experience years'), help_text='float')
    count = models.IntegerField(null=True, blank=True, verbose_name=_('count'))
    type_of_employment = models.ForeignKey(
        'dictionary.TypeOfEmployment', related_name='requests_requirements', null=True, blank=True,
        on_delete=models.RESTRICT, verbose_name=_('type of employment')
    )
    work_location_city = models.ForeignKey(
        'dictionary.City', related_name='requests_requirements', null=True, blank=True, on_delete=models.SET_NULL,
        verbose_name=_('city')
    )
    work_location_address = models.CharField(max_length=1000, null=True, blank=True, verbose_name=_('address'))
    max_price = models.FloatField(null=True, blank=True, verbose_name=_('max rate'))
    date_from = models.DateField(null=True, blank=True, verbose_name=_('date from'))
    date_to = models.DateField(null=True, blank=True, verbose_name=_('date to'))

    class Meta:
        ordering = ['sorting', 'name']
        verbose_name = _('requests / requirement')
        verbose_name_plural = _('requests / requirements')

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


class RequestRequirementCvStatus(models.TextChoices):
    PRE_CANDIDATE = 'pre-candidate'
    CANDIDATE = 'candidate'
    CANCELED = 'canceled'
    WORKER = 'worker'


@reversion.register(follow=['request_requirement'])
class RequestRequirementCv(main_permissions.MainModelPermissionsMixin, ModelDiffMixin, DatesModelBase):
    permission_save = main_permissions.request_requirement_cv_save
    permission_delete = main_permissions.request_requirement_cv_delete

    """
    Есть сигналы
    """
    request_requirement = models.ForeignKey(
        'main.RequestRequirement', on_delete=models.CASCADE, related_name='cv_links',
        verbose_name=_('requiest requirement')
    )
    cv = models.ForeignKey(
        'cv.CV', on_delete=models.CASCADE, related_name='requests_requirements_links',
        verbose_name=_('CV')
    )
    status = models.CharField(
        max_length=50, choices=RequestRequirementCvStatus.choices, default=RequestRequirementCvStatus.CANDIDATE,
        verbose_name=_('status')
    )
    date_from = models.DateField(null=True, blank=True, verbose_name=_('working on project from'))
    date_to = models.DateField(null=True, blank=True, verbose_name=_('working on project to'))

    rating = models.IntegerField(
        null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_('rating')
    )
    attributes = models.JSONField(
        default=dict, verbose_name=_('additional attributes'),
        help_text=_('avoid editing if you do not know the purpose of this field')
    )

    class Meta:
        ordering = ['-id']
        unique_together = [
            ['request_requirement', 'cv']
        ]
        verbose_name = _('CV')
        verbose_name_plural = _('CVs')

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
        super().clean()
        organization_project_card_items = (self.attributes or {}).get('organization_project_card_items')
        if not organization_project_card_items:
            return
        cards_items_ids = [row['id'] for row in organization_project_card_items]
        cards_items_qs = OrganizationProjectCardItem.objects_flat.filter(
            id__in=cards_items_ids,
            organization_project_id=self.request_requirement.request.module.organization_project_id
        )
        if len(cards_items_ids) != cards_items_qs.count():
            raise ValidationError({
                'attributes.organization_project_card_items': _('At least one card has invalid ID')
            })


@reversion.register(follow=['request_requirement'])
class RequestRequirementCompetence(main_permissions.MainModelPermissionsMixin, DatesModelBase):
    permission_save = main_permissions.request_requirement_competence_save
    permission_delete = main_permissions.request_requirement_competence_delete

    request_requirement = models.ForeignKey(
        'main.RequestRequirement', on_delete=models.CASCADE, related_name='competencies',
        verbose_name=_('request requirement')
    )
    competence = models.ForeignKey('dictionary.Competence', on_delete=models.CASCADE, verbose_name=_('competence'))
    experience_years = models.IntegerField(
        null=True, blank=True, choices=ExperienceYears.choices,
        verbose_name=_('years of experience')
    )
    sorting = models.IntegerField(default=0, verbose_name=_('sorting'))

    class Meta:
        ordering = ['sorting', '-experience_years', 'id']
        unique_together = [
            ['request_requirement', 'competence']
        ]
        verbose_name = _('competence')
        verbose_name_plural = _('competencies')

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
class TimeSheetRow(main_permissions.MainModelPermissionsMixin, DatesModelBase):
    permission_save = main_permissions.request_time_sheet_row_save
    permission_delete = main_permissions.request_time_sheet_row_delete

    request = models.ForeignKey(
        'main.Request', on_delete=models.CASCADE, related_name='time_sheet_rows',
        verbose_name=_('request')
    )
    cv = models.ForeignKey(
        'cv.CV', on_delete=models.CASCADE, related_name='time_sheet_rows',
        verbose_name=_('contractor CV')
    )
    date_from = models.DateField(default=timezone.now, db_index=True, verbose_name=_('start date'))
    date_to = models.DateField(null=True, blank=True, verbose_name=_('end date'))
    task_name = models.CharField(max_length=1000, verbose_name=_('task name'))
    task_description = models.TextField(null=True, blank=True, verbose_name=_('task description'))
    work_time = models.FloatField(verbose_name=_('time spent'))

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
        verbose_name = _('requests / timesheets')
        verbose_name_plural = _('requests / timesheets')

    objects = Manager()

    def __str__(self):
        return f'{self.task_name} < {self.id} / {self.request_id} >'

    def clean(self):
        super().clean()
        if not CV.objects.filter(
                requests_requirements_links__request_requirement__request=self.request,
                id=self.cv_id,
        ).exists():
            raise ValidationError({
                'cv': _(f'CV <{self.cv_id}> is not linked to a request requirement')
            })
