import datetime

from django.core.management.base import BaseCommand

from cv import models as cv_models
from project.contrib.db import get_sql_from_queryset


class Command(BaseCommand):
    def handle(self, *args, **options):
        qs = cv_models.CvPosition.objects.filter(year_started__gt=datetime.datetime.now().year)
        for cv_pos in qs:
            cv_pos.year_started = datetime.datetime.now().year + (datetime.datetime.now().year - cv_pos.year_started)
            cv_pos.save()
