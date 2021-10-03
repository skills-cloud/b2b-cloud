from typing import List

import reversion
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from project.contrib.db.models import DatesModelBase
from acc.models import User

__all__ = [
    'TimeSheetRow',
]


@reversion.register()
class TimeSheetRow(DatesModelBase):
    request_requirement = models.ForeignKey(
        'main.RequestRequirement', on_delete=models.RESTRICT, related_name='time_sheet_rows',
        verbose_name=_('требование проектного запроса')
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
            return self

    class Manager(models.Manager.from_queryset(QuerySet)):
        @classmethod
        def get_queryset_prefetch_related(cls) -> List:
            return ['request_requirement', 'cv']

    class Meta:
        ordering = ['-date_from']
        index_together = [
            ['request_requirement', 'date_from'],
            ['request_requirement', 'task_name'],
        ]
        verbose_name = _('строка таймшита')
        verbose_name_plural = _('строки таймшитов')

    objects = Manager()

    def __str__(self):
        return f'< {self.task_name} / {self.request_requirement} >'

    def clean(self):
        if not self.request_requirement.cv_list.filter(id=self.cv_id).exists():
            raise ValidationError({
                'cv': _('Анкета не связана с требованием проектного запроса')
            })
