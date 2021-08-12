import reversion
from django.db import models
from django.utils.translation import gettext_lazy as _

from project.contrib.db.models import DatesModelBase


class ExperienceYears(models.IntegerChoices):
    ZERO = 1, _('Менее года')
    THREE = 3, _('1 – 3 года')
    FIVE = 5, _('3 - 5 лет')
    ONE_HUNDRED = 100, _('Более 5 лет')


class WorkLocation(models.IntegerChoices):
    OFFICE = 'office', _('Офис')
    HOME = 'home', _('Удаленная работа')
    MIXED = 'mixed', _('Смешанная')


@reversion.register(follow=['projects'])
class Organization(DatesModelBase):
    name = models.CharField(max_length=500, verbose_name=_('название'))
    description = models.TextField(null=True, blank=True, verbose_name=_('описание'))

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


class RequestStatus(models.TextChoices):
    DRAFT = 'draft', _('Черновик')


@reversion.register(follow=['requirements'])
class Request(DatesModelBase):
    description = models.TextField(null=True, blank=True, verbose_name=_('описание'))
    customer = models.ForeignKey(
        'main.Organization', on_delete=models.CASCADE, related_name='requests',
        verbose_name=_('заказчик')
    )
    status = models.CharField(
        max_length=50, default=RequestStatus.DRAFT, choices=RequestStatus.choices,
        verbose_name=_('статус')
    )
    industry_sector = models.ForeignKey(
        'dictionary.IndustrySector', on_delete=models.RESTRICT,
        verbose_name=_('отрасль')
    )
    project = models.ForeignKey(
        'main.Project', on_delete=models.RESTRICT,
        verbose_name=_('проект')
    )
    deadline_date = models.DateField(null=True, blank=True, verbose_name=_('срок'))

    class Meta:
        ordering = ['name']
        verbose_name = _('проектный запрос')
        verbose_name_plural = _('проектные запросы')


@reversion.register(follow=['request'])
class RequestRequirement(DatesModelBase):
    request = models.ForeignKey(
        'main.Request', on_delete=models.CASCADE, related_name='requirements',
        verbose_name=_('запрос')
    )
    name = models.CharField(max_length=1000, null=True, blank=True, verbose_name=_('название'))
    description = models.TextField(null=True, blank=True, verbose_name=_('описание'))
    position = models.ForeignKey(
        'dictionary.Position', on_delete=models.RESTRICT,
        verbose_name=_('должность')
    )
    years = models.FloatField(null=True, blank=True, verbose_name=_('опыт'), help_text='float')
    count = models.IntegerField(null=True, blank=True, verbose_name=_('количество'))
    work_location = models.CharField(
        max_length=100, choices=WorkLocation, default=WorkLocation.OFFICE,
        verbose_name=_('тип работы')
    )

    class Meta:
        ordering = ['name']
        verbose_name = _('требование проектного запроса')
        verbose_name_plural = _('требования проектного запроса')


@reversion.register(follow=['cv'])
class RequestRequirementCompetence(DatesModelBase):
    request_requirement = models.ForeignKey(
        'main.RequestRequirement', on_delete=models.CASCADE, related_name='competencies',
        verbose_name=_('требование проектного запроса')
    )
    competence = models.ForeignKey('dictionary.Competence', on_delete=models.RESTRICT, verbose_name=_('компетенция'))
    years = models.IntegerField(null=True, blank=True, choices=ExperienceYears, verbose_name=_('опыт лет'))

    class Meta:
        ordering = ['-years', 'id']
        unique_together = [
            ['request_requirement', 'competence']
        ]
        verbose_name = _('компетенция')
        verbose_name_plural = _('компетенции')

    def __str__(self):
        return f'< {self.request_requirement_id} / {self.id} >'
