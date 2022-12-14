from typing import Optional, Callable

from django.db import models
from django.forms.models import model_to_dict
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _


class DatesModelBase(models.Model):
    class Meta:
        abstract = True

    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name=_('создано'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('обновлено'))


class ModelDiffMixin:
    __initial__ = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__initial__ = self._dict

    @property
    def diff(self):
        d1 = self.__initial__
        d2 = self._dict
        diffs = [(k, (v, d2[k])) for k, v in d1.items() if v != d2[k]]
        return dict(diffs)

    @property
    def has_changed(self):
        return bool(self.diff)

    @property
    def changed_fields(self):
        return self.diff.keys()

    def get_field_diff(self, field_name):
        return self.diff.get(field_name, None)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.__initial__ = self._dict

    @property
    def _dict(self):
        return model_to_dict(self, fields=[field.name for field in self._meta.fields])


class ModelPermissionsMixin:
    permission_save: Optional[Callable] = None
    permission_delete: Optional[Callable] = None

    def clean(self):
        if self.permission_save and not self.permission_save():
            raise PermissionDenied(_('У вас нет прав'))
        return super().clean()

    def delete(self, **kwargs):
        if self.permission_delete and not self.permission_delete():
            raise PermissionDenied(_('У вас нет прав'))
        return super().delete(**kwargs)
