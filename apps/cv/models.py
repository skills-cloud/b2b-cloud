from typing import Optional, List, Dict, Any
from typing import Optional
from pathlib import Path
from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import reversion

from project.contrib.db.models import DatesModelBase
from acc.models import User
from cv import models_upload_to as upload_to


class FileModelAbstract(DatesModelBase):
    file_name = models.CharField(max_length=1000, null=True, blank=True, verbose_name=_('название файла'))

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


@reversion.register(follow=['contacts', 'positions', 'career', 'education', 'certificates', 'files', 'competencies'])
class CV(DatesModelBase):
    class Gender(models.TextChoices):
        MALE = 'M', _('Мужской')
        FEMALE = 'F', _('Женский')

    class DaysToContact(models.TextChoices):
        ALL = 'all', _('Все дни')
        WORKDAYS = 'workdays', _('Будние дни')
        WEEKENDS = 'weekends', _('Выходные дни')

    UPLOAD_TO = 'cv'

    user = models.ForeignKey(
        'acc.User', null=True, blank=True, on_delete=models.SET_NULL, related_name='cv_list',
        verbose_name=_('пользователь')
    )
    last_name = models.CharField(max_length=500, null=True, blank=True, verbose_name=_('фамилия'))
    first_name = models.CharField(max_length=500, null=True, blank=True, verbose_name=_('имя'))
    middle_name = models.CharField(max_length=500, null=True, blank=True, verbose_name=_('отчество'))
    photo = models.ImageField(upload_to=upload_to.cv_photo_upload_to, null=True, blank=True)
    gender = models.CharField(max_length=1, null=True, blank=True, choices=Gender.choices, verbose_name=_('пол'))
    birth_date = models.DateField(null=True, blank=True, verbose_name=_('дата рождения'))
    country = models.ForeignKey(
        'dictionary.Country', on_delete=models.RESTRICT, null=True, blank=True,
        verbose_name=_('страна')
    )
    city = models.ForeignKey(
        'dictionary.City', on_delete=models.RESTRICT, null=True, blank=True,
        verbose_name=_('город')
    )
    citizenship = models.ForeignKey(
        'dictionary.Citizenship', on_delete=models.RESTRICT, null=True, blank=True,
        verbose_name=_('гражданство')
    )
    physical_limitations = models.ManyToManyField(
        'dictionary.PhysicalLimitation', blank=True,
        verbose_name=_('физические особенности')
    )
    days_to_contact = models.CharField(
        max_length=50, choices=DaysToContact.choices, null=True, blank=True,
        verbose_name=_('дни для связи')
    )
    time_to_contact_from = models.TimeField(null=True, blank=True, verbose_name=_('время для связи / с'))
    time_to_contact_to = models.TimeField(null=True, blank=True, verbose_name=_('время для связи / по'))
    is_resource_owner = models.BooleanField(default=False, verbose_name=_('владелец ресурса'))
    is_verified = models.BooleanField(default=False, verbose_name=_('подтверждено'))
    about = models.TextField(null=True, blank=True, verbose_name=_('доп. информация'))

    class Meta:
        ordering = ['-id']
        verbose_name = _('анкета')
        verbose_name_plural = _('анкеты')

    class QuerySet(models.QuerySet):
        def filter_by_user(self, user: User):
            return self

    class Manager(models.Manager.from_queryset(QuerySet)):
        @classmethod
        def get_queryset_prefetch_related(cls) -> List[str]:
            return [
                'user', 'country', 'city', 'citizenship', 'physical_limitations', 'files',

                'competencies', 'competencies__competence',

                'contacts', 'contacts__contact_type',

                'time_slots', 'time_slots__country', 'time_slots__city', 'time_slots__type_of_employment',

                'positions', 'positions__position', 'positions__files', 'positions__competencies',

                'career', 'career__files', 'career__organization', 'career__projects', 'career__projects__organization',
                'career__position', 'career__competencies',

                'projects', 'projects__organization', 'projects__position', 'projects__industry_sector',
                'projects__competencies',

                'education', 'education__education_place', 'education__education_graduate',
                'education__education_speciality', 'education__competencies',

                'certificates', 'certificates__education_place', 'certificates__education_graduate',
                'certificates__education_speciality', 'certificates__competencies',

            ]

    objects = Manager()

    def __str__(self):
        return f'%s < {self.id_verbose} >' % ' '.join(
            getattr(self, k)
            for k in ['last_name', 'first_name', 'middle_name']
            if getattr(self, k)
        ).strip()

    @property
    def id_verbose(self) -> str:
        return str(self.id).zfill(7)

    @property
    def competence_count(self) -> int:
        return len(self.competencies.all())

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
        return super().get_queryset().prefetch_related('cv')


@reversion.register(follow=['cv'])
class CvCompetence(DatesModelBase):
    cv = models.ForeignKey('cv.CV', on_delete=models.CASCADE, related_name='competencies', verbose_name=_('анкета'))
    competence = models.ForeignKey('dictionary.Competence', on_delete=models.RESTRICT, verbose_name=_('компетенция'))
    year_started = models.IntegerField(null=True, blank=True, verbose_name=_('год начала практики'))

    class Meta:
        ordering = ['-year_started', 'id']
        unique_together = [
            ['cv', 'competence']
        ]
        verbose_name = _('компетенция')
        verbose_name_plural = _('компетенции')

    class Manager(CvLinkedObjectManager):
        @transaction.atomic
        def replace_for_cv(self, cv: CV, bulk_rows_data: List[Dict[str, Any]]) -> List['CvCompetence']:
            self.filter(cv=cv).delete()
            field_names = ['cv', 'cv_id', 'competence', 'competence_id', 'year_started']
            return self.bulk_create(
                CvCompetence(
                    cv=cv,
                    **{k: v for k, v in row.items() if k in field_names}
                )
                for row in bulk_rows_data
            )

    objects = Manager()

    def __str__(self):
        return f'{self.cv_id} / {self.competence_id} < {self.id} >'

    @property
    def years(self) -> Optional[int]:
        if not self.year_started:
            return
        return timezone.now().year - self.year_started


@reversion.register(follow=['cv'])
class CvContact(DatesModelBase):
    cv = models.ForeignKey('cv.CV', on_delete=models.CASCADE, related_name='contacts', verbose_name=_('анкета'))
    contact_type = models.ForeignKey(
        'dictionary.ContactType', on_delete=models.RESTRICT,
        verbose_name=_('тип')
    )
    value = models.CharField(max_length=1000, verbose_name=_('значение'))
    is_primary = models.BooleanField(default=False, verbose_name=_('основной'))
    comment = models.TextField(max_length=1000, null=True, blank=True, verbose_name=_('комментарий'))

    class Meta:
        ordering = ['is_primary', '-id']
        index_together = [
            [v.replace('-', '') for v in ordering]
        ]
        unique_together = [
            'cv', 'contact_type', 'value',
        ]
        verbose_name = _('контактные данные')
        verbose_name_plural = _('контактные данные')

    objects = CvLinkedObjectManager()

    def __str__(self):
        return f'{self.contact_type_id} :: {self.value} < {self.cv_id} / {self.id} >'


@reversion.register(follow=['cv'])
class CvTimeSlot(DatesModelBase):
    cv = models.ForeignKey('cv.CV', on_delete=models.CASCADE, related_name='time_slots', verbose_name=_('анкета'))
    date_from = models.DateField(null=True, blank=True, verbose_name=_('период с'))
    date_to = models.DateField(null=True, blank=True, verbose_name=_('период по'))
    country = models.ForeignKey(
        'dictionary.Country', on_delete=models.RESTRICT, null=True, blank=True,
        verbose_name=_('страна')
    )
    city = models.ForeignKey(
        'dictionary.City', on_delete=models.RESTRICT, null=True, blank=True,
        verbose_name=_('город')
    )
    type_of_employment = models.ForeignKey(
        'dictionary.TypeOfEmployment', on_delete=models.RESTRICT, null=True, blank=True,
        verbose_name=_('тип занятости')
    )
    price = models.FloatField(null=True, blank=True, verbose_name=_('ставка'))
    is_work_permit_required = models.BooleanField(default=False, verbose_name=_('требуется разрешение на работу'))
    description = models.TextField(null=True, blank=True, verbose_name=_('описание'))

    class Meta:
        ordering = ['-date_from', '-id']
        index_together = [
            [v.replace('-', '') for v in ordering]
        ]
        verbose_name = _('таймслот')
        verbose_name_plural = _('таймслоты')

    objects = CvLinkedObjectManager()

    def __str__(self):
        return f'{self.date_from} – {self.date_to} < {self.cv_id} / {self.id} >'


@reversion.register(follow=['cv', 'files'])
class CvPosition(DatesModelBase):
    cv = models.ForeignKey('cv.CV', on_delete=models.CASCADE, related_name='positions', verbose_name=_('анкета'))
    title = models.CharField(max_length=2000, null=True, blank=True, verbose_name=_('произвольное название'))
    position = models.ForeignKey(
        'dictionary.Position', on_delete=models.RESTRICT, null=True, blank=True,
        verbose_name=_('должность')
    )
    competencies = models.ManyToManyField('dictionary.Competence', blank=True, verbose_name=_('компетенции'))

    class Meta:
        ordering = ['-id']
        unique_together = [
            ['cv', 'position']
        ]
        verbose_name = _('должность / роль')
        verbose_name_plural = _('должности / роли')

    objects = CvLinkedObjectManager()

    def __str__(self):
        return f' < {self.cv_id} / {self.id} >'


@reversion.register(follow=['cv_position'])
class CvPositionFile(FileModelAbstract):
    UPLOAD_TO = 'position'

    cv_position = models.ForeignKey(
        'cv.CvPosition', on_delete=models.CASCADE, related_name='files', verbose_name=_('роль'))
    file = models.FileField(upload_to=upload_to.cv_position_file_upload_to, verbose_name=_('файл'))

    class Meta:
        ordering = ['-id']
        verbose_name = _('файл роли')
        verbose_name_plural = _('файлы роли')

    def __str__(self):
        return f'< {self.cv_position_id} / {self.id} >'


@reversion.register(follow=['cv', 'files'])
class CvCareer(DatesModelBase):
    cv = models.ForeignKey('cv.CV', on_delete=models.CASCADE, related_name='career', verbose_name=_('анкета'))
    date_from = models.DateField(null=True, blank=True, verbose_name=_('период с'))
    date_to = models.DateField(null=True, blank=True, verbose_name=_('период по'))
    organization = models.ForeignKey('main.Organization', on_delete=models.RESTRICT, verbose_name=_('заказчик'))
    title = models.CharField(max_length=2000, null=True, blank=True, verbose_name=_('произвольное название'))
    position = models.ForeignKey(
        'dictionary.Position', on_delete=models.RESTRICT, null=True, blank=True,
        verbose_name=_('должность / роль')
    )
    competencies = models.ManyToManyField('dictionary.Competence', blank=True, verbose_name=_('компетенции'))
    projects = models.ManyToManyField('main.OrganizationProject', blank=True, verbose_name=_('проекты'))
    description = models.TextField(null=True, blank=True, verbose_name=_('описание'))
    is_verified = models.BooleanField(default=False, verbose_name=_('подтверждено'))

    class Meta:
        ordering = ['-date_from', '-id']
        index_together = [
            [v.replace('-', '') for v in ordering]
        ]
        verbose_name = _('карьера')
        verbose_name_plural = _('карьера')

    objects = CvLinkedObjectManager()

    def __str__(self):
        return f'{self.date_from} – {self.date_to} < {self.cv_id} / {self.id} >'


@reversion.register(follow=['cv_career'])
class CvCareerFile(FileModelAbstract):
    UPLOAD_TO = 'career'

    cv_career = models.ForeignKey(
        'cv.CvCareer', on_delete=models.CASCADE, related_name='files', verbose_name=_('карьера'))
    file = models.FileField(upload_to=upload_to.cv_career_file_upload_to, verbose_name=_('файл'))

    class Meta:
        ordering = ['-id']
        verbose_name = _('файл карьеры')
        verbose_name_plural = _('файлы карьеры')

    def __str__(self):
        return f'< {self.cv_career_id} / {self.id} >'


@reversion.register(follow=['cv'])
class CvProject(DatesModelBase):
    cv = models.ForeignKey('cv.CV', on_delete=models.CASCADE, related_name='projects', verbose_name=_('анкета'))
    name = models.CharField(max_length=1000, verbose_name=_('название'))
    date_from = models.DateField(null=True, blank=True, verbose_name=_('период с'))
    date_to = models.DateField(null=True, blank=True, verbose_name=_('период по'))
    organization = models.ForeignKey('main.Organization', on_delete=models.RESTRICT, verbose_name=_('заказчик'))
    position = models.ForeignKey(
        'dictionary.Position', on_delete=models.RESTRICT,
        verbose_name=_('должность / роль')
    )
    industry_sector = models.ForeignKey(
        'dictionary.IndustrySector', on_delete=models.RESTRICT, null=True, blank=True,
        verbose_name=_('отрасль')
    )
    competencies = models.ManyToManyField('dictionary.Competence', blank=True, verbose_name=_('компетенции'))
    description = models.TextField(null=True, blank=True, verbose_name=_('описание'))
    is_verified = models.BooleanField(default=False, verbose_name=_('подтверждено'))

    class Meta:
        ordering = ['-date_from', '-id']
        index_together = [
            [v.replace('-', '') for v in ordering]
        ]
        verbose_name = _('проект')
        verbose_name_plural = _('проекты')

    objects = CvLinkedObjectManager()

    def __str__(self):
        return f'{self.date_from} – {self.date_to} < {self.cv_id} / {self.id} >'


@reversion.register(follow=['cv'])
class CvEducation(DatesModelBase):
    cv = models.ForeignKey('cv.CV', on_delete=models.CASCADE, related_name='education', verbose_name=_('анкета'))
    date_from = models.DateField(null=True, blank=True, verbose_name=_('период с'))
    date_to = models.DateField(null=True, blank=True, verbose_name=_('период по'))
    is_verified = models.BooleanField(default=False, verbose_name=_('подтверждено'))
    description = models.TextField(null=True, blank=True, verbose_name=_('описание'))
    education_place = models.ForeignKey(
        'dictionary.EducationPlace', on_delete=models.RESTRICT, null=True, blank=True,
        verbose_name=_('место обучения')
    )
    education_speciality = models.ForeignKey(
        'dictionary.EducationSpecialty', on_delete=models.RESTRICT, null=True, blank=True,
        verbose_name=_('специальность')
    )
    education_graduate = models.ForeignKey(
        'dictionary.EducationGraduate', on_delete=models.RESTRICT, null=True, blank=True,
        verbose_name=_('степень')
    )
    competencies = models.ManyToManyField('dictionary.Competence', blank=True, verbose_name=_('компетенции'))

    class Meta:
        ordering = ['-date_from', '-id']
        index_together = [
            [v.replace('-', '') for v in ordering]
        ]
        verbose_name = _('образование')
        verbose_name_plural = _('образование')

    objects = CvLinkedObjectManager()

    def __str__(self):
        return f'{self.education_place_id} :: {self.date_from} – {self.date_to} < {self.cv_id} / {self.id} >'


@reversion.register(follow=['cv'])
class CvCertificate(DatesModelBase):
    cv = models.ForeignKey('cv.CV', on_delete=models.CASCADE, related_name='certificates', verbose_name=_('анкета'))
    date = models.DateField(null=True, blank=True, verbose_name=_('выдан'))
    is_verified = models.BooleanField(default=False, verbose_name=_('подтверждено'))
    name = models.CharField(max_length=1000, null=True, blank=True, verbose_name=_('наименование'))
    number = models.CharField(max_length=1000, null=True, blank=True, verbose_name=_('номер'))
    description = models.TextField(null=True, blank=True, verbose_name=_('описание'))
    education_place = models.ForeignKey(
        'dictionary.EducationPlace', on_delete=models.RESTRICT, null=True, blank=True,
        verbose_name=_('место обучения')
    )
    education_speciality = models.ForeignKey(
        'dictionary.EducationSpecialty', on_delete=models.RESTRICT, null=True, blank=True,
        verbose_name=_('специальность')
    )
    education_graduate = models.ForeignKey(
        'dictionary.EducationGraduate', on_delete=models.RESTRICT, null=True, blank=True,
        verbose_name=_('степень')
    )
    competencies = models.ManyToManyField('dictionary.Competence', blank=True, verbose_name=_('компетенции'))

    class Meta:
        ordering = ['-date', '-id']
        index_together = [
            [v.replace('-', '') for v in ordering]
        ]
        verbose_name = _('сертификат')
        verbose_name_plural = _('сертификаты')

    objects = CvLinkedObjectManager()

    def __str__(self):
        return f'{self.education_place_id} :: {self.date} < {self.cv_id} / {self.id} >'


@reversion.register(follow=['cv'])
class CvFile(FileModelAbstract):
    UPLOAD_TO = 'file'

    cv = models.ForeignKey('cv.CV', on_delete=models.CASCADE, related_name='files', verbose_name=_('анкета'))
    file = models.FileField(upload_to=upload_to.cv_file_file_upload_to, verbose_name=_('файл'))

    class Meta:
        ordering = ['-id']
        verbose_name = _('файл анкеты')
        verbose_name_plural = _('файлы анкеты')

    objects = CvLinkedObjectManager()

    def __str__(self):
        return f'< {self.cv_id} / {self.id} >'
