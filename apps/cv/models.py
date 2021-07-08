from django.db import models
from django.utils.translation import gettext_lazy as _

from project.contrib.db.models import DatesModelBase


class CV(DatesModelBase):
    class Gender(models.TextChoices):
        MALE = 'М', _('Мужской')
        FEMALE = 'F', _('Женский')

    user = models.ForeignKey(
        'acc.User', null=True, blank=True, on_delete=models.SET_NULL, related_name='cv_list',
        verbose_name=_('пользователь')
    )
    first_name = models.CharField(max_length=500, null=True, blank=True, verbose_name=_('имя'))
    last_name = models.CharField(max_length=500, null=True, blank=True, verbose_name=_('фамилия'))
    middle_name = models.CharField(max_length=500, null=True, blank=True, verbose_name=_('отчество'))
    gender = models.CharField(max_length=1, null=True, blank=True, choices=Gender.choices, verbose_name=_('пол'))
    birth_date = models.DateField(null=True, blank=True, verbose_name=_('дата рождения'))
    country = models.ForeignKey('dictionary.Country', on_delete=models.RESTRICT, verbose_name=_('страна'))
    citizenship = models.ForeignKey('dictionary.Citizenship', on_delete=models.RESTRICT, verbose_name=_('гражданство'))
    competence = models.ManyToManyField('dictionary.Competence', verbose_name=_('компетенции'))

    class Meta:
        ordering = ['id']
        verbose_name = _('анкета')
        verbose_name_plural = _('анкеты')


class CvContact(DatesModelBase):
    cv = models.ForeignKey('cv.CV', on_delete=models.CASCADE, related_name='contacts', verbose_name=_('анкета'))
    contact_type = models.ForeignKey(
        'dictionary.ContactType', on_delete=models.RESTRICT, related_name='cv_list',
        verbose_name=_('тип контактной информации')
    )
    value = models.CharField(max_length=1000)
    is_primary = models.BooleanField(default=False)

    class Meta:
        ordering = ['id']
        verbose_name = _('контактные данные')
        verbose_name_plural = _('контактные данные')


class CvPosition(DatesModelBase):
    cv = models.ForeignKey('cv.CV', on_delete=models.CASCADE, related_name='positions', verbose_name=_('анкета'))
    position = models.ForeignKey(
        'dictionary.Position', on_delete=models.RESTRICT, related_name='cv_positions',
        verbose_name=_('должность')
    )
    competencies = models.ManyToManyField('dictionary.Competence', verbose_name=_('компетенции'))

    class Meta:
        ordering = ['id']
        verbose_name = _('должность / роль')
        verbose_name_plural = _('должности / роли')


class CvPositionFile(DatesModelBase):
    cv_position = models.ForeignKey(
        'cv.CvPosition', on_delete=models.CASCADE, related_name='files', verbose_name=_('роль'))
    file = models.FileField(verbose_name=_('файл'))

    class Meta:
        ordering = ['id']
        verbose_name = _('файл роли')
        verbose_name_plural = _('файлы роли')


class CvProject(DatesModelBase):
    cv = models.ForeignKey('cv.CV', on_delete=models.CASCADE, related_name='projects', verbose_name=_('анкета'))
    date_from = models.DateField(null=True, blank=True, verbose_name=_('период с'))
    date_to = models.DateField(null=True, blank=True, verbose_name=_('период по'))
    project = models.ForeignKey(
        'main.Project', on_delete=models.RESTRICT, related_name='cv_list',
        verbose_name=_('проект')
    )
    position = models.ForeignKey(
        'dictionary.Position', on_delete=models.RESTRICT, related_name='cv_projects',
        verbose_name=_('должность / роль')
    )
    competencies = models.ManyToManyField('dictionary.Competence', verbose_name=_('компетенции'))
    description = models.TextField(null=True, blank=True, verbose_name=_('описание'))

    class Meta:
        ordering = ['-date_from']
        verbose_name = _('проект')
        verbose_name_plural = _('проекты')


class CvEducation(DatesModelBase):
    cv = models.ForeignKey('cv.CV', on_delete=models.CASCADE, related_name='education', verbose_name=_('анкета'))
    date_from = models.DateField(null=True, blank=True, verbose_name=_('период с'))
    date_to = models.DateField(null=True, blank=True, verbose_name=_('период по'))
    education_place = models.ForeignKey(
        'dictionary.EducationPlace', on_delete=models.RESTRICT, related_name='cv_education',
        verbose_name=_('место обучения')
    )
    education_speciality = models.ForeignKey(
        'dictionary.EducationSpecialty', on_delete=models.RESTRICT, related_name='cv_education',
        null=True, blank=True,
        verbose_name=_('специальность')
    )
    education_graduate = models.ForeignKey(
        'dictionary.EducationGraduate', on_delete=models.RESTRICT, related_name='cv_education',
        null=True, blank=True,
        verbose_name=_('степень')
    )
    competencies = models.ManyToManyField('dictionary.Competence', verbose_name=_('компетенции'))
    description = models.TextField(null=True, blank=True, verbose_name=_('описание'))

    class Meta:
        ordering = ['-date_from']
        verbose_name = _('образование')
        verbose_name_plural = _('образование')


class CvCertificate(DatesModelBase):
    cv = models.ForeignKey('cv.CV', on_delete=models.CASCADE, related_name='certificates', verbose_name=_('анкета'))
    date = models.DateField(null=True, blank=True, verbose_name=_('выдан'))
    education_speciality = models.ForeignKey(
        'dictionary.EducationSpecialty', on_delete=models.RESTRICT, related_name='cv_certificate',
        null=True, blank=True,
        verbose_name=_('специальность')
    )
    education_graduate = models.ForeignKey(
        'dictionary.EducationGraduate', on_delete=models.RESTRICT, related_name='cv_certificate',
        null=True, blank=True,
        verbose_name=_('степень')
    )
    competencies = models.ManyToManyField('dictionary.Competence', verbose_name=_('компетенции'))
    description = models.TextField(null=True, blank=True, verbose_name=_('описание'))

    class Meta:
        ordering = ['-date']
        verbose_name = _('сертификат')
        verbose_name_plural = _('сертификаты')


class CvFile(DatesModelBase):
    cv = models.ForeignKey('cv.CV', on_delete=models.CASCADE, related_name='files', verbose_name=_('анкета'))
    name = models.CharField(max_length=500, null=True, blank=True, verbose_name=_('название'))
    file = models.FileField(verbose_name=_('файл'))

    class Meta:
        ordering = ['name']
        verbose_name = _('файл')
        verbose_name_plural = _('файлы')
