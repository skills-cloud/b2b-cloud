import logging

from django.core.management.base import BaseCommand
from django.db import transaction

from cv.models import CV

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    @transaction.atomic
    def handle(self, *args, **options):
        qs = CV.objects.filter(attributes__has_key='fw_json')
        qs_count = len(qs)
        for i, cv in enumerate(qs):
            cv.last_name = None
            cv.first_name = 'Тестовый'
            cv.middle_name = 'Пользователь %s' % cv.id
            cv.save()
            logger.info(f'{i+1}/{qs_count}\t{cv.id_verbose}')

