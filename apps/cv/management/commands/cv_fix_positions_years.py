import datetime

from django.core.management.base import BaseCommand

from cv import models as cv_models


class Command(BaseCommand):
    def handle(self, *args, **options):
        for cv_pos in cv_models.CvPosition.objects.filter(year_started__lte=0):
            cv_pos.year_started = datetime.datetime.now().year - cv_pos.year_started
            cv_pos.save()
