from django.db import models
from django.utils.translation import gettext_lazy as _
import reversion

from acc.models import User
from project.contrib.db.models import DatesModelBase


@reversion.register()
class CV(DatesModelBase):
    class Gender(models.TextChoices):
        MALE = 'М', _('Мужской')
        FEMALE = 'F', _('Женский')

    user = models.ForeignKey(
        'acc.User', null=True, blank=True, on_delete=models.SET_NULL, related_name='cv_list',
        verbose_name=_('пользователь')
    )
    last_name = models.CharField(max_length=500, null=True, blank=True, verbose_name=_('фамилия'))
    first_name = models.CharField(max_length=500, null=True, blank=True, verbose_name=_('имя'))
    middle_name = models.CharField(max_length=500, null=True, blank=True, verbose_name=_('отчество'))
    photo = models.ImageField(null=True, blank=True)
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
    competencies = models.ManyToManyField('dictionary.Competence', blank=True, verbose_name=_('компетенции'))
    is_with_disabilities = models.BooleanField(default=False, verbose_name=_('ограниченные возможности'))
    is_resource_owner = models.BooleanField(default=False, verbose_name=_('владелец ресурса'))
    is_verified = models.BooleanField(default=False, verbose_name=_('подтверждено'))

    class Meta:
        ordering = ['id']
        verbose_name = _('анкета')
        verbose_name_plural = _('анкеты')

    class QuerySet(models.QuerySet):
        def filter_by_user(self, user: User):
            return self

    class Manager(models.Manager.from_queryset(QuerySet)):
        pass

    objects = Manager()

    def __str__(self):
        return f'%s < {self.id} >' % ' '.join(
            getattr(self, k)
            for k in ['last_name', 'first_name', 'middle_name']
            if getattr(self, k)
        ).strip()


class CvLinkedObjectQuerySet(models.QuerySet):
    def filter_by_user(self, user: User):
        return self.filter(cv__in=CV.objects.filter_by_user(user))


class CvLinkedObjectManager(models.Manager.from_queryset(CvLinkedObjectQuerySet)):
    def get_queryset(self):
        return super().get_queryset().prefetch_related('cv')


@reversion.register()
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
        ordering = ['id']
        unique_together = [
            'cv', 'contact_type', 'value',
        ]
        verbose_name = _('контактные данные')
        verbose_name_plural = _('контактные данные')

    objects = CvLinkedObjectManager()

    def __str__(self):
        return f'{self.contact_type_id} :: {self.value} < {self.id} >'


@reversion.register()
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
        ordering = ['id']
        verbose_name = _('таймслот')
        verbose_name_plural = _('таймслоты')

    objects = CvLinkedObjectManager()

    def __str__(self):
        return f'{self.date_from} – {self.date_to}'


@reversion.register()
class CvPosition(DatesModelBase):
    cv = models.ForeignKey('cv.CV', on_delete=models.CASCADE, related_name='positions', verbose_name=_('анкета'))
    position = models.ForeignKey(
        'dictionary.Position', on_delete=models.RESTRICT,
        verbose_name=_('должность')
    )
    competencies = models.ManyToManyField('dictionary.Competence', blank=True, verbose_name=_('компетенции'))

    class Meta:
        ordering = ['id']
        verbose_name = _('должность / роль')
        verbose_name_plural = _('должности / роли')

    objects = CvLinkedObjectManager()


@reversion.register()
class CvPositionFile(DatesModelBase):
    cv_position = models.ForeignKey(
        'cv.CvPosition', on_delete=models.CASCADE, related_name='files', verbose_name=_('роль'))
    file = models.FileField(verbose_name=_('файл'))

    class Meta:
        ordering = ['id']
        verbose_name = _('файл роли')
        verbose_name_plural = _('файлы роли')


@reversion.register()
class CvCareer(DatesModelBase):
    cv = models.ForeignKey('cv.CV', on_delete=models.CASCADE, related_name='career', verbose_name=_('анкета'))
    date_from = models.DateField(null=True, blank=True, verbose_name=_('период с'))
    date_to = models.DateField(null=True, blank=True, verbose_name=_('период по'))
    organization = models.ForeignKey('main.Organization', on_delete=models.RESTRICT, verbose_name=_('заказчик'))
    position = models.ForeignKey(
        'dictionary.Position', on_delete=models.RESTRICT,
        verbose_name=_('должность / роль')
    )
    competencies = models.ManyToManyField('dictionary.Competence', blank=True, verbose_name=_('компетенции'))
    projects = models.ManyToManyField('cv.CvProject', blank=True, verbose_name=_('проекты'))
    description = models.TextField(null=True, blank=True, verbose_name=_('описание'))
    is_verified = models.BooleanField(default=False, verbose_name=_('подтверждено'))

    class Meta:
        ordering = ['-date_from']
        verbose_name = _('карьера')
        verbose_name_plural = _('карьера')

    objects = CvLinkedObjectManager()


@reversion.register()
class CvCareerFile(DatesModelBase):
    cv_career = models.ForeignKey(
        'cv.CvCareer', on_delete=models.CASCADE, related_name='files', verbose_name=_('карьера'))
    file = models.FileField(verbose_name=_('файл'))

    class Meta:
        ordering = ['id']
        verbose_name = _('файл карьеры')
        verbose_name_plural = _('файлы карьеры')


@reversion.register()
class CvProject(DatesModelBase):
    cv = models.ForeignKey('cv.CV', on_delete=models.CASCADE, related_name='projects', verbose_name=_('анкета'))
    name = models.CharField(max_length=500, verbose_name=_('название'))
    date_from = models.DateField(null=True, blank=True, verbose_name=_('период с'))
    date_to = models.DateField(null=True, blank=True, verbose_name=_('период по'))
    organization = models.ForeignKey(
        'main.Organization', null=True, blank=True, on_delete=models.SET_NULL,
        verbose_name=_('заказчик')
    )
    position = models.ForeignKey(
        'dictionary.Position', on_delete=models.RESTRICT,
        verbose_name=_('должность / роль')
    )
    competencies = models.ManyToManyField('dictionary.Competence', blank=True, verbose_name=_('компетенции'))
    description = models.TextField(null=True, blank=True, verbose_name=_('описание'))
    is_verified = models.BooleanField(default=False, verbose_name=_('подтверждено'))

    class Meta:
        ordering = ['-date_from']
        verbose_name = _('проект')
        verbose_name_plural = _('проекты')

    objects = CvLinkedObjectManager()


@reversion.register()
class CvEducation(DatesModelBase):
    cv = models.ForeignKey('cv.CV', on_delete=models.CASCADE, related_name='education', verbose_name=_('анкета'))
    date_from = models.DateField(null=True, blank=True, verbose_name=_('период с'))
    date_to = models.DateField(null=True, blank=True, verbose_name=_('период по'))
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
    description = models.TextField(null=True, blank=True, verbose_name=_('описание'))
    is_verified = models.BooleanField(default=False, verbose_name=_('подтверждено'))

    class Meta:
        ordering = ['-date_from']
        verbose_name = _('образование')
        verbose_name_plural = _('образование')

    objects = CvLinkedObjectManager()


@reversion.register()
class CvCertificate(DatesModelBase):
    cv = models.ForeignKey('cv.CV', on_delete=models.CASCADE, related_name='certificates', verbose_name=_('анкета'))
    date = models.DateField(null=True, blank=True, verbose_name=_('выдан'))
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
    description = models.TextField(null=True, blank=True, verbose_name=_('описание'))
    is_verified = models.BooleanField(default=False, verbose_name=_('подтверждено'))

    class Meta:
        ordering = ['-date']
        verbose_name = _('сертификат')
        verbose_name_plural = _('сертификаты')

    objects = CvLinkedObjectManager()


@reversion.register()
class CvFile(DatesModelBase):
    cv = models.ForeignKey('cv.CV', on_delete=models.CASCADE, related_name='files', verbose_name=_('анкета'))
    name = models.CharField(max_length=500, null=True, blank=True, verbose_name=_('название'))
    file = models.FileField(verbose_name=_('файл'))

    class Meta:
        ordering = ['name']
        verbose_name = _('файл')
        verbose_name_plural = _('файлы')

    objects = CvLinkedObjectManager()
