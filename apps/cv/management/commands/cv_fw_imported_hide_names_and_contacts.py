import datetime

import logging

from django.core.management.base import BaseCommand
from django.db import transaction

from project.contrib.datetime import random_date
from cv.models import CV

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    @transaction.atomic
    def handle(self, *args, **options):
        bd_from = datetime.datetime(1970, 1, 1)
        bd_to = datetime.datetime(2000, 12, 31)
        qs = CV.objects.filter(attributes__has_key='fw_json')
        qs_count = len(qs)
        for i, cv in enumerate(qs):
            cv.last_name = None
            cv.first_name = 'Тестовый'
            cv.middle_name = 'Пользователь %s' % cv.id
            cv.birth_date = random_date(bd_from, bd_to).date()
            cv.save()
            cv.contacts.all().delete()
            logger.info(f'{i+1}/{qs_count}\t{cv.id_verbose}\t{cv.birth_date}')

