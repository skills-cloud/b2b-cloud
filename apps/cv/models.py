from django.core.exceptions import ValidationError
from typing import TYPE_CHECKING, Optional, List, Dict
from pathlib import Path

from django.db import models, transaction
from django.utils import timezone
from django.contrib.postgres.indexes import GinIndex
from django.utils.translation import gettext_lazy as _
import reversion

from project.contrib.db.models import DatesModelBase
from project.contrib.is_call_from_admin import is_call_from_admin
from acc.models import User
from main.models import OrganizationContractor
from cv import models_upload_to as upload_to

if TYPE_CHECKING:
    from main.models import OrganizationProject, RequestRequirement, Request


class FileModelAbstract(DatesModelBase):
    file_name = models.CharField(max_length=1000, null=True, blank=True, verbose_name=_('file name'))

    class Meta:
        abstract = True

    @property
    def file_ext(self) -> Optional[str]:
        if not self.file:
            return None
        return Path(self.file.path).suffix.lower()[1:]

    @property
    def file_size(self) -> Optional[int]:
        if not self.file:
            return None
        try:
            return Path(self.file.path).stat().st_size
        except FileNotFoundError:
            return None


class Gender(models.TextChoices):
    MALE = 'M', _('Male')
    FEMALE = 'F', _('Female')


class DaysToContact(models.TextChoices):
    ALL = 'all', _('All')
    WORKDAYS = 'workdays', _('Workdays')
    WEEKENDS = 'weekends', _('Weekends')


@reversion.register(follow=['contacts', 'positions', 'career', 'projects', 'education', 'certificates', 'files'])
class CV(DatesModelBase):
    UPLOAD_TO = 'cv'

    organization_contractor = models.ForeignKey(
        'main.OrganizationContractor', related_name='cv_list', null=True, blank=True, on_delete=models.SET_NULL,
        verbose_name=_('Contractor Organization')
    )
    manager_rm = models.ForeignKey(
        'acc.User', related_name='cv_list_as_rm', null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name=_('RM')
    )
    user = models.ForeignKey(
        'acc.User', null=True, blank=True, on_delete=models.SET_NULL, related_name='cv_list',
        verbose_name=_('user')
    )
    last_name = models.CharField(max_length=500, null=True, blank=True, verbose_name=_('last name'))
    first_name = models.CharField(max_length=500, null=True, blank=True, verbose_name=_('first name'))
    middle_name = models.CharField(max_length=500, null=True, blank=True, verbose_name=_('middle name'))
    photo = models.ImageField(upload_to=upload_to.cv_photo_upload_to, null=True, blank=True)
    gender = models.CharField(max_length=1, null=True, blank=True, choices=Gender.choices, verbose_name=_('gender'))
    birth_date = models.DateField(null=True, blank=True, verbose_name=_('birth date'))
    country = models.ForeignKey(
        'dictionary.Country', on_delete=models.RESTRICT, null=True, blank=True,
        verbose_name=_('country')
    )
    city = models.ForeignKey(
        'dictionary.City', on_delete=models.RESTRICT, null=True, blank=True,
        verbose_name=_('city')
    )
    citizenship = models.ForeignKey(
        'dictionary.Citizenship', on_delete=models.RESTRICT, null=True, blank=True,
        verbose_name=_('citizenship')
    )
    physical_limitations = models.ManyToManyField(
        'dictionary.PhysicalLimitation', blank=True,
        verbose_name=_('physical limitations')
    )
    days_to_contact = models.CharField(
        max_length=50, choices=DaysToContact.choices, null=True, blank=True,
        verbose_name=_('contact days')
    )
    time_to_contact_from = models.TimeField(null=True, blank=True, verbose_name=_('contact time / from'))
    time_to_contact_to = models.TimeField(null=True, blank=True, verbose_name=_('contact time / to'))
    is_verified = models.BooleanField(default=False, verbose_name=_('verified'))
    about = models.TextField(null=True, blank=True, verbose_name=_('additional information'))
    price = models.FloatField(null=True, blank=True, verbose_name=_('rate'))
    types_of_employment = models.ManyToManyField(
        'dictionary.TypeOfEmployment', blank=True,
        verbose_name=_('type of employment')
    )
    linked = models.ManyToManyField('self', blank=True, symmetrical=True, verbose_name=_('linked CVs'))

    attributes = models.JSONField(
        default=dict, verbose_name=_('additional attributes'), editable=False,
        help_text=_('avoid editing if you do not know the purpose of this field')
    )

    class Meta:
        ordering = ['-id']
        indexes = [
            GinIndex(fields=['attributes'])
        ]
        verbose_name = _('CV')
        verbose_name_plural = _('CVs')

    class QuerySet(models.QuerySet):
        def filter_by_user(self, user: User):
            if user.is_superuser or user.is_staff:
                return self
            return self.filter(organization_contractor__in=OrganizationContractor.objects.filter_by_user(user))

        def filter_by_position_years(self, years: int) -> 'CV.QuerySet':
            return self.filter(positions__year_started__lte=timezone.now().year - years)

    class Manager(models.Manager.from_queryset(QuerySet)):
        @classmethod
        def get_queryset_prefetch_related(cls) -> List[str]:
            return [
                'info', 'organization_contractor', 'manager_rm',
                'user', 'country', 'city', 'citizenship', 'physical_limitations', 'types_of_employment', 'linked',

                'files',

                'contacts', 'contacts__contact_type',

                'time_slots', 'time_slots__country', 'time_slots__city', 'time_slots__type_of_employment',
                'time_slots__request_requirement_link', 'time_slots__request_requirement_link__request_requirement',
                'time_slots__request_requirement_link__request_requirement__request',
                'time_slots__request_requirement_link__request_requirement__request__organization_project',

                'positions', 'positions__position', 'positions__files', 'positions__competencies',
                'positions__competencies__competence',

                'career', 'career__files', 'career__organization', 'career__projects',
                'career__projects__organization_customer', 'career__position', 'career__competencies',

                'projects',
                'projects__organization',
                'projects__position', 'projects__industry_sector',
                'projects__competencies',

                'education', 'education__education_place', 'education__education_graduate',
                'education__education_speciality', 'education__competencies',

                'certificates', 'certificates__education_place', 'certificates__education_graduate',
                'certificates__education_speciality', 'certificates__competencies',
            ]

        @classmethod
        def get_queryset_request_requirements_prefetch_related(cls) -> List[str]:
            from main.models import Request, RequestRequirement
            prefix = 'requests_requirements_links__request_requirement'
            return [
                *[
                    f'{prefix}__{f}'
                    for f in RequestRequirement.objects.get_queryset_prefetch_related_self()
                ],
                *[
                    f'{prefix}__request__{f}'
                    for f in Request.objects.get_queryset_prefetch_related_self()
                ],
            ]

    objects = Manager()

    def clean(self):
        super().clean()
        errors = {}
        if self.manager_rm:
            if not self.organization_contractor:
                errors['organization_contractor'] = _('To set a resource manager, you need to set a contractor organization')
            if not self.organization_contractor.get_user_roles(self.manager_rm):
                errors['manager_rm'] = _('This user cannot be set as the resource manager for this CV')
        if errors:
            if not is_call_from_admin():
                errors = {f'{k}_id': v for k, v in errors.items()}
            raise ValidationError(errors)

    def __str__(self):
        return f'%s < {self.id_verbose} >' % ' '.join(
            getattr(self, k)
            for k in ['last_name', 'first_name', 'middle_name']
            if getattr(self, k)
        ).strip()

    @property
    def id_verbose(self) -> str:
        return str(self.id).zfill(7) if self.id else None

    @property
    def contact_count(self) -> int:
        return len(self.contacts.all())

    @property
    def time_slot_count(self) -> int:
        return len(self.time_slots.all())

    @property
    def position_count(self) -> int:
        return len(self.positions.all())

    @property
    def career_count(self) -> int:
        return len(self.career.all())

    @property
    def projects_count(self) -> int:
        return len(self.projects.all())

    @property
    def education_count(self) -> int:
        return len(self.education.all())

    @property
    def file_count(self) -> int:
        return len(self.files.all())


class CvLinkedObjectQuerySet(models.QuerySet):
    def filter_by_user(self, user: User):
        return self.filter(cv__in=CV.objects.filter_by_user(user))


class CvLinkedObjectManager(models.Manager.from_queryset(CvLinkedObjectQuerySet)):
    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            *self.get_queryset_prefetch_related()
        )

    @classmethod
    def get_queryset_prefetch_related(cls) -> List[str]:
        return ['cv']


@reversion.register(follow=['cv'])
class CvContact(DatesModelBase):
    cv = models.ForeignKey('cv.CV', on_delete=models.CASCADE, related_name='contacts', verbose_name=_('CV'))
    contact_type = models.ForeignKey(
        'dictionary.ContactType', on_delete=models.RESTRICT,
        verbose_name=_('type')
    )
    value = models.CharField(max_length=1000, verbose_name=_('value'))
    is_primary = models.BooleanField(default=False, verbose_name=_('primary'))
    comment = models.TextField(max_length=1000, null=True, blank=True, verbose_name=_('comment'))

    class Meta:
        ordering = ['is_primary', '-id']
        index_together = [
            [v.replace('-', '') for v in ordering]
        ]
        unique_together = [
            'cv', 'contact_type', 'value',
        ]
        verbose_name = _('contact information')
        verbose_name_plural = _('contact information')

    objects = CvLinkedObjectManager()

    def __str__(self):
        return f'{self.contact_type_id} :: {self.value} < {self.cv_id} / {self.id} >'


class CvTimeSlotKind(models.TextChoices):
    MANUAL = 'manual'
    REQUEST_REQUIREMENT = 'request_requirement'


@reversion.register(follow=['cv'])
class CvTimeSlot(DatesModelBase):
    cv = models.ForeignKey('cv.CV', on_delete=models.CASCADE, related_name='time_slots', verbose_name=_('CV'))
    request_requirement_link = models.ForeignKey(
        'main.RequestRequirementCv', null=True, blank=True, on_delete=models.CASCADE, related_name='time_slots',
        verbose_name=_('linked to a request requirement'),
    )
    kind = models.CharField(
        max_length=50, choices=CvTimeSlotKind.choices, default=CvTimeSlotKind.MANUAL,
        verbose_name=_('slot type'),
    )
    date_from = models.DateField(null=True, blank=True, verbose_name=_('date from'))
    date_to = models.DateField(null=True, blank=True, verbose_name=_('date to'))
    country = models.ForeignKey(
        'dictionary.Country', on_delete=models.RESTRICT, null=True, blank=True,
        verbose_name=_('country')
    )
    city = models.ForeignKey(
        'dictionary.City', on_delete=models.RESTRICT, null=True, blank=True,
        verbose_name=_('city')
    )
    type_of_employment = models.ForeignKey(
        'dictionary.TypeOfEmployment', on_delete=models.RESTRICT, null=True, blank=True,
        verbose_name=_('type of employment')
    )
    price = models.FloatField(null=True, blank=True, verbose_name=_('rate'))
    is_work_permit_required = models.BooleanField(default=False, verbose_name=_('work permit required'))
    description = models.TextField(null=True, blank=True, verbose_name=_('description'))
    is_free = models.BooleanField(default=False, verbose_name=_('available?'))

    class Meta:
        ordering = ['-date_from', '-id']
        index_together = [
            [v.replace('-', '') for v in ordering]
        ]
        verbose_name = _('timeslot')
        verbose_name_plural = _('timeslots')

    class Manager(CvLinkedObjectManager):
        @classmethod
        def get_queryset_prefetch_related(cls) -> List[str]:
            return (
                super().get_queryset_prefetch_related()
                # + [
                #     'request_requirement_link', 'request_requirement_link__request_requirement',
                #     'request_requirement_link__request_requirement__request',
                #     'request_requirement_link__request_requirement__request__organization_project',
                # ]
            )

    objects = Manager()

    def __str__(self):
        return f'{self.date_from} – {self.date_to} < {self.cv_id} / {self.id} >'

    @property
    def request_requirement(self) -> Optional['RequestRequirement']:
        if self.request_requirement_link:
            return self.request_requirement_link.request_requirement

    @property
    def request(self) -> Optional['Request']:
        if self.request_requirement:
            return self.request_requirement.request

    @property
    def organization_project(self) -> Optional['OrganizationProject']:
        if self.request:
            return self.request.organization_project


@reversion.register(follow=['cv', 'files', 'competencies'])
class CvPosition(DatesModelBase):
    cv = models.ForeignKey('cv.CV', on_delete=models.CASCADE, related_name='positions', verbose_name=_('CV'))
    title = models.CharField(max_length=2000, null=True, blank=True, verbose_name=_('arbitrary title'))
    position = models.ForeignKey(
        'dictionary.Position', on_delete=models.RESTRICT, null=True, blank=True,
        verbose_name=_('position')
    )
    year_started = models.IntegerField(null=True, blank=True, verbose_name=_('year started'))

    class Meta:
        ordering = ['-id']
        unique_together = [
            ['cv', 'position']
        ]
        verbose_name = _('position / role')
        verbose_name_plural = _('positions / roles')

    objects = CvLinkedObjectManager()

    def __str__(self):
        return f' < {self.cv_id} / {self.id} >'

    @property
    def years(self) -> Optional[int]:
        if not self.year_started:
            return
        return timezone.now().year - self.year_started


@reversion.register(follow=['cv_position'])
class CvPositionCompetence(DatesModelBase):
    cv_position = models.ForeignKey(
        'cv.CvPosition', on_delete=models.CASCADE, related_name='competencies',
        verbose_name=_('position / role')
    )
    competence = models.ForeignKey('dictionary.Competence', on_delete=models.CASCADE, verbose_name=_('competence'))
    year_started = models.IntegerField(null=True, blank=True, verbose_name=_('year started'))

    class Meta:
        ordering = ['-year_started', 'id']
        unique_together = [
            ['cv_position', 'competence']
        ]
        verbose_name = _('role competence')
        verbose_name_plural = _('role competencies')

    class Manager(models.Manager):
        @transaction.atomic()
        def set_for_position(self, cv_position: CvPosition, data: List[Dict[str, int]]) -> List['CvPositionCompetence']:
            self.filter(cv_position=cv_position).delete()
            return self.bulk_create([
                self.model(
                    cv_position=cv_position,
                    **{k: v for k, v in row.items() if k not in ['years']}
                )
                for row in data
            ])

    objects = Manager()

    def __str__(self):
        return f'{self.cv_position_id} / {self.competence_id} < {self.id} >'

    @property
    def years(self) -> Optional[int]:
        if not self.year_started:
            return
        return timezone.now().year - self.year_started


@reversion.register(follow=['cv_position'])
class CvPositionFile(FileModelAbstract):
    UPLOAD_TO = 'position'

    cv_position = models.ForeignKey(
        'cv.CvPosition', on_delete=models.CASCADE, related_name='files', verbose_name=_('role'))
    file = models.FileField(upload_to=upload_to.cv_position_file_upload_to, verbose_name=_('file'))

    class Meta:
        ordering = ['-id']
        verbose_name = _('role file')
        verbose_name_plural = _('role files')

    def __str__(self):
        return f'< {self.cv_position_id} / {self.id} >'


@reversion.register(follow=['cv', 'files'])
class CvCareer(DatesModelBase):
    cv = models.ForeignKey('cv.CV', on_delete=models.CASCADE, related_name='career', verbose_name=_('CV'))
    date_from = models.DateField(null=True, blank=True, verbose_name=_('date from'))
    date_to = models.DateField(null=True, blank=True, verbose_name=_('date to'))
    organization = models.ForeignKey(
        'dictionary.Organization', null=True, blank=True, on_delete=models.SET_NULL,
        verbose_name=_('customer')
    )
    title = models.CharField(max_length=2000, null=True, blank=True, verbose_name=_('arbitrary title'))
    position = models.ForeignKey(
        'dictionary.Position', on_delete=models.RESTRICT, null=True, blank=True,
        verbose_name=_('position / role')
    )
    competencies = models.ManyToManyField('dictionary.Competence', blank=True, verbose_name=_('competencies'))
    projects = models.ManyToManyField('main.OrganizationProject', blank=True, verbose_name=_('projects'))
    description = models.TextField(null=True, blank=True, verbose_name=_('description'))
    is_verified = models.BooleanField(default=False, verbose_name=_('verified'))

    class Meta:
        ordering = ['-date_from', '-id']
        index_together = [
            [v.replace('-', '') for v in ordering]
        ]
        verbose_name = _('career')
        verbose_name_plural = _('career')

    objects = CvLinkedObjectManager()

    def __str__(self):
        return f'{self.date_from} – {self.date_to} < {self.cv_id} / {self.id} >'


@reversion.register(follow=['cv_career'])
class CvCareerFile(FileModelAbstract):
    UPLOAD_TO = 'career'

    cv_career = models.ForeignKey(
        'cv.CvCareer', on_delete=models.CASCADE, related_name='files', verbose_name=_('career'))
    file = models.FileField(upload_to=upload_to.cv_career_file_upload_to, verbose_name=_('file'))

    class Meta:
        ordering = ['-id']
        verbose_name = _('career file')
        verbose_name_plural = _('career files')

    class QuerySet(models.QuerySet):
        def filter_by_user(self, user: User):
            return self.filter(cv_career__in=CvCareer.objects.filter_by_user(user))

    objects = QuerySet.as_manager()

    def __str__(self):
        return f'< {self.cv_career_id} / {self.id} >'


@reversion.register(follow=['cv'])
class CvProject(DatesModelBase):
    cv = models.ForeignKey('cv.CV', on_delete=models.CASCADE, related_name='projects', verbose_name=_('CV'))
    name = models.CharField(max_length=1000, verbose_name=_('title'))
    date_from = models.DateField(null=True, blank=True, verbose_name=_('date from'))
    date_to = models.DateField(null=True, blank=True, verbose_name=_('date to'))
    organization = models.ForeignKey(
        'dictionary.Organization', null=True, blank=True, on_delete=models.SET_NULL,
        verbose_name=_('customer'))
    position = models.ForeignKey(
        'dictionary.Position', on_delete=models.RESTRICT,
        verbose_name=_('position / role')
    )
    industry_sector = models.ForeignKey(
        'dictionary.IndustrySector', on_delete=models.RESTRICT, null=True, blank=True,
        verbose_name=_('industry')
    )
    competencies = models.ManyToManyField('dictionary.Competence', blank=True, verbose_name=_('competencies'))
    description = models.TextField(null=True, blank=True, verbose_name=_('description'))
    is_verified = models.BooleanField(default=False, verbose_name=_('verified'))

    class Meta:
        ordering = ['-date_from', '-id']
        index_together = [
            [v.replace('-', '') for v in ordering]
        ]
        verbose_name = _('project')
        verbose_name_plural = _('projects')

    objects = CvLinkedObjectManager()

    def __str__(self):
        return f'{self.date_from} – {self.date_to} < {self.cv_id} / {self.id} >'


@reversion.register(follow=['cv'])
class CvEducation(DatesModelBase):
    cv = models.ForeignKey('cv.CV', on_delete=models.CASCADE, related_name='education', verbose_name=_('CV'))
    date_from = models.DateField(null=True, blank=True, verbose_name=_('date from'))
    date_to = models.DateField(null=True, blank=True, verbose_name=_('date to'))
    is_verified = models.BooleanField(default=False, verbose_name=_('verified'))
    diploma_number = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('diploma number'))
    description = models.TextField(null=True, blank=True, verbose_name=_('description'))
    education_place = models.ForeignKey(
        'dictionary.EducationPlace', on_delete=models.RESTRICT, null=True, blank=True,
        verbose_name=_('place of study')
    )
    education_speciality = models.ForeignKey(
        'dictionary.EducationSpecialty', on_delete=models.RESTRICT, null=True, blank=True,
        verbose_name=_('specialty')
    )
    education_graduate = models.ForeignKey(
        'dictionary.EducationGraduate', on_delete=models.RESTRICT, null=True, blank=True,
        verbose_name=_('degree')
    )
    competencies = models.ManyToManyField('dictionary.Competence', blank=True, verbose_name=_('competencies'))

    class Meta:
        ordering = ['-date_from', '-id']
        index_together = [
            [v.replace('-', '') for v in ordering]
        ]
        verbose_name = _('education')
        verbose_name_plural = _('education')

    objects = CvLinkedObjectManager()

    def __str__(self):
        return f'{self.education_place_id} :: {self.date_from} – {self.date_to} < {self.cv_id} / {self.id} >'


@reversion.register(follow=['cv'])
class CvCertificate(DatesModelBase):
    cv = models.ForeignKey('cv.CV', on_delete=models.CASCADE, related_name='certificates', verbose_name=_('CV'))
    date = models.DateField(null=True, blank=True, verbose_name=_('issued'))
    is_verified = models.BooleanField(default=False, verbose_name=_('verified'))
    name = models.CharField(max_length=1000, null=True, blank=True, verbose_name=_('title'))
    number = models.CharField(max_length=1000, null=True, blank=True, verbose_name=_('number'))
    description = models.TextField(null=True, blank=True, verbose_name=_('description'))
    education_place = models.ForeignKey(
        'dictionary.EducationPlace', on_delete=models.RESTRICT, null=True, blank=True,
        verbose_name=_('place of study')
    )
    education_speciality = models.ForeignKey(
        'dictionary.EducationSpecialty', on_delete=models.RESTRICT, null=True, blank=True,
        verbose_name=_('specialty')
    )
    education_graduate = models.ForeignKey(
        'dictionary.EducationGraduate', on_delete=models.RESTRICT, null=True, blank=True,
        verbose_name=_('degree')
    )
    competencies = models.ManyToManyField('dictionary.Competence', blank=True, verbose_name=_('competencies'))

    class Meta:
        ordering = ['-date', '-id']
        index_together = [
            [v.replace('-', '') for v in ordering]
        ]
        verbose_name = _('certificate')
        verbose_name_plural = _('certificate')

    objects = CvLinkedObjectManager()

    def __str__(self):
        return f'{self.education_place_id} :: {self.date} < {self.cv_id} / {self.id} >'


@reversion.register(follow=['cv'])
class CvFile(FileModelAbstract):
    UPLOAD_TO = 'file'

    cv = models.ForeignKey('cv.CV', on_delete=models.CASCADE, related_name='files', verbose_name=_('CV'))
    file = models.FileField(upload_to=upload_to.cv_file_file_upload_to, verbose_name=_('file'))

    class Meta:
        ordering = ['-id']
        verbose_name = _('CV file')
        verbose_name_plural = _('CV files')

    objects = CvLinkedObjectManager()

    def __str__(self):
        return f'< {self.cv_id} / {self.id} >'


class CvInfo(models.Model):
    cv = models.OneToOneField('cv.CV', primary_key=True, on_delete=models.DO_NOTHING, related_name='info')
    rating = models.IntegerField(null=True)

    class Meta:
        managed = False
        db_table = 'v_cv_info'
