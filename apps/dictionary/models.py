from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import ArrayField
from mptt.models import MPTTModel, TreeForeignKey

from project.contrib.db.models import DatesModelBase


class DictionaryModelBase(DatesModelBase):
    name = models.CharField(max_length=500, db_index=True, verbose_name=_('название'))
    is_verified = models.BooleanField(default=False, verbose_name=_('подтверждено'))
    description = models.TextField(null=True, blank=True, verbose_name=_('описание'))
    sorting = models.IntegerField(default=0, verbose_name=_('сортировка'))

    class Meta(DatesModelBase.Meta):
        abstract = True

    def __str__(self):
        return self.name


class TypeOfEmployment(DictionaryModelBase):
    class Meta(DatesModelBase.Meta):
        ordering = ['sorting', 'name']
        verbose_name = _('тип занятости')
        verbose_name_plural = _('типы занятости')


class Country(DictionaryModelBase):
    class Meta(DatesModelBase.Meta):
        ordering = ['sorting', 'name']
        verbose_name = _('страна')
        verbose_name_plural = _('страны')


class City(DictionaryModelBase):
    country = models.ForeignKey(
        'dictionary.Country', on_delete=models.CASCADE, related_name='cities', verbose_name=_('страна')
    )

    class Meta:
        ordering = ['sorting', 'name']
        verbose_name = _('город')
        verbose_name_plural = _('города')

    def __str__(self):
        return f'{self.name} < {self.country} >'


class Citizenship(DictionaryModelBase):
    class Meta:
        ordering = ['sorting', 'name']
        verbose_name = _('гражданство')
        verbose_name_plural = _('гражданства')


class ContactType(DictionaryModelBase):
    class Meta:
        ordering = ['sorting', 'name']
        verbose_name = _('тип контактной информации')
        verbose_name_plural = _('типы контактной информации')


class EducationPlace(DictionaryModelBase):
    class Meta:
        ordering = ['sorting', 'name']
        verbose_name = _('место учебы')
        verbose_name_plural = _('места учебы')


class EducationSpecialty(DictionaryModelBase):
    class Meta:
        ordering = ['sorting', 'name']
        verbose_name = _('специальность')
        verbose_name_plural = _('специальности')


class EducationGraduate(DictionaryModelBase):
    class Meta:
        ordering = ['sorting', 'name']
        verbose_name = _('ученая степень')
        verbose_name_plural = _('ученые степени')


class Position(DictionaryModelBase):
    class Meta:
        ordering = ['sorting', 'name']
        verbose_name = _('должность')
        verbose_name_plural = _('должности')


class PhysicalLimitation(DictionaryModelBase):
    class Meta:
        ordering = ['sorting', 'name']
        verbose_name = _('физическая особенность')
        verbose_name_plural = _('физические особенности')


class Competence(MPTTModel, DictionaryModelBase):
    sorting = None
    parent = TreeForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='children',
        verbose_name=_('родитель')
    )
    aliases = ArrayField(models.CharField(max_length=500), null=True, blank=True)

    class Meta:
        verbose_name = _('компетенция')
        verbose_name_plural = _('компетенции')

    class MPTTMeta:
        level_attr = 'mptt_level'
        order_insertion_by = ['name']

    class ManagerFlat(models.Manager):
        pass

    objects_flat = ManagerFlat()


class IndustrySector(DictionaryModelBase):
    class Meta:
        ordering = ['sorting', 'name']
        verbose_name = _('отрасль')
        verbose_name_plural = _('отрасли')
