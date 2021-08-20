import re
from typing import List, Union
from dataclasses import dataclass

import datetime
from openpyxl import load_workbook
from django.core.management.base import BaseCommand
from django.db import transaction

from dictionary import models as dictionary_models


@dataclass
class Row:
    role_name: str
    competence_name: str
    sub_competence_name: Union[str, bool]
    sub_competence_versions: List

    def __post_init__(self):
        self.competence_name = self._prepare_value(self.competence_name)
        if self.sub_competence_name:
            self.sub_competence_name = self._prepare_value(self.sub_competence_name)
        for i, v in enumerate(self.sub_competence_versions):
            if isinstance(v, datetime.date):
                self.sub_competence_versions[i] = f'{v.day}.{v.month}'
            else:
                self.sub_competence_versions[i] = self._prepare_value(str(self.sub_competence_versions[i]))

    @classmethod
    def _prepare_value(cls, value):
        ret = re.sub(r'\s+', ' ', value, re.MULTILINE).strip()
        for replace in [
            ['Знание инстурментов тестирования', 'Знание инструментов тестирования'],
            ['Знание систем графического дизайна', 'Знание систем для графического дизайна'],
            ['Знание языков программирования', 'Языки программирования'],
            ['Знание модулей', 'Знание модулей SAP'],
        ]:
            ret = ret.replace(*replace)
        return ret


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('filepath')

    @transaction.atomic
    def handle(self, *args, **options):
        wb = load_workbook(options['filepath'])
        for sheet in wb:
            role_name = None
            competence_name = None
            for row_i, row in enumerate(sheet):
                if not row_i:
                    continue
                row = [cell.value for cell in row]
                if row[0]:
                    role_name = row[0]
                if row[1]:
                    competence_name = row[1]
                sub_competence_name = row[2]
                sub_competence_versions = [v for v in row[3:] if v]
                self.make_one(
                    Row(
                        role_name=role_name,
                        competence_name=competence_name,
                        sub_competence_name=sub_competence_name,
                        sub_competence_versions=sub_competence_versions,
                    )
                )

    @classmethod
    def make_one(cls, row: Row) -> None:
        print(
            row.role_name,
            row.competence_name,
            row.sub_competence_name,
            row.sub_competence_versions,
            sep='\t|\t',
        )
        position, is_position_created = dictionary_models.Position.objects.get_or_create(name=row.role_name)
        if not position.is_verified:
            position.is_verified = True
            position.save()
        competence, is_competence_created = dictionary_models.Competence.objects.get_or_create(
            name=row.competence_name,
        )
        if not competence.is_verified:
            competence.is_verified = True
            competence.save()
        if not row.sub_competence_name:
            return
        sub_competence, is_sub_competence_created = dictionary_models.Competence.objects.get_or_create(
            parent=competence,
            name=row.sub_competence_name,
        )
        if not sub_competence.is_verified:
            sub_competence.is_verified = True
            sub_competence.save()
        for v_name in row.sub_competence_versions:
            v, is_v_created = dictionary_models.Competence.objects.get_or_create(
                parent=sub_competence,
                name=v_name,
                is_verified=True,
            )
            if not v.is_verified:
                v.is_verified = True
                v.save()
