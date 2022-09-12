from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import ArrayField
from mptt.models import MPTTModel, TreeForeignKey

from project.contrib.db.models import DatesModelBase


class DictionaryModelBase(DatesModelBase):
    name = models.CharField(max_length=500, db_index=True, verbose_name=_('title'))
    is_verified = models.BooleanField(default=False, verbose_name=_('verified'))
    description = models.TextField(null=True, blank=True, verbose_name=_('description'))
    sorting = models.IntegerField(default=0, verbose_name=_('sorting'))
    attributes = models.JSONField(
        default=dict, verbose_name=_('additional attributes'), editable=False,
        help_text=_(' if you don\'t really understand purpose of this field you should avoid editing')
    )

    class Meta(DatesModelBase.Meta):
        abstract = True

    def __str__(self):
        return self.name


class TypeOfEmployment(DictionaryModelBase):
    class Meta(DatesModelBase.Meta):
        ordering = ['sorting', 'name']
        verbose_name = _('employment type')
        verbose_name_plural = _('employment types')


class Country(DictionaryModelBase):
    class Meta(DatesModelBase.Meta):
        ordering = ['sorting', 'name']
        verbose_name = _('country')
        verbose_name_plural = _('countries')


class City(DictionaryModelBase):
    country = models.ForeignKey(
        'dictionary.Country', on_delete=models.CASCADE, related_name='cities', verbose_name=_('country')
    )

    class Meta:
        ordering = ['sorting', 'name']
        verbose_name = _('city')
        verbose_name_plural = _('cities')

    def __str__(self):
        return f'{self.name} < {self.country} >'


class Citizenship(DictionaryModelBase):
    class Meta:
        ordering = ['sorting', 'name']
        verbose_name = _('citizenship')
        verbose_name_plural = _('citizenships')


class ContactType(DictionaryModelBase):
    class Meta:
        ordering = ['sorting', 'name']
        verbose_name = _('contact info type')
        verbose_name_plural = _('contact info types')


class EducationPlace(DictionaryModelBase):
    class Meta:
        ordering = ['sorting', 'name']
        verbose_name = _('education place')
        verbose_name_plural = _('education places')


class EducationSpecialty(DictionaryModelBase):
    class Meta:
        ordering = ['sorting', 'name']
        verbose_name = _('specialty')
        verbose_name_plural = _('specialties')


class EducationGraduate(DictionaryModelBase):
    class Meta:
        ordering = ['sorting', 'name']
        verbose_name = _('science degree')
        verbose_name_plural = _('science degree')


class Position(DictionaryModelBase):
    class Meta:
        ordering = ['sorting', 'name']
        verbose_name = _('position')
        verbose_name_plural = _('positions')


class PhysicalLimitation(DictionaryModelBase):
    class Meta:
        ordering = ['sorting', 'name']
        verbose_name = _('disability')
        verbose_name_plural = _('disabilities')


class Competence(MPTTModel, DictionaryModelBase):
    sorting = None
    parent = TreeForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='children',
        verbose_name=_('parent')
    )
    aliases = ArrayField(models.CharField(max_length=500), null=True, blank=True)

    class Meta:
        verbose_name = _('competence')
        verbose_name_plural = _('competences')

    class MPTTMeta:
        level_attr = 'mptt_level'
        order_insertion_by = ['name']

    class ManagerFlat(models.Manager):
        pass

    objects_flat = ManagerFlat()


class IndustrySector(DictionaryModelBase):
    class Meta:
        ordering = ['sorting', 'name']
        verbose_name = _('sector')
        verbose_name_plural = _('sectors')


class Organization(DictionaryModelBase):
    class Meta:
        ordering = ['sorting', 'name']
        verbose_name = _('company')
        verbose_name_plural = _('companies')


class Category(DictionaryModelBase):
    class Meta:
        ordering = ['sorting', 'name']
        verbose_name = _('category')
        verbose_name_plural = _('categories')


class Certificate(DictionaryModelBase):
    class Meta:
        ordering = ['sorting', 'name']
        verbose_name = _('certificate')
        verbose_name_plural = _('certificate')


class CurrencyReference(DictionaryModelBase):
    currency_name = models.CharField(
        max_length=40, verbose_name=_('Currency name')
    )
    digital_code = models.CharField(
        max_length=5, verbose_name=_('Digital code')
    )
    designation = models.CharField(
        max_length=5, verbose_name=_('Designation')
    )
    currency_link = models.CharField(
        max_length=255, verbose_name=_('Currency link')
    )

    class Meta:
        ordering = ['sorting', 'name']
        verbose_name = _('Currency reference')
        verbose_name_plural = _('Currency references')

    def __str__(self):
        return f'{self.currency_name} {self.designation}'
