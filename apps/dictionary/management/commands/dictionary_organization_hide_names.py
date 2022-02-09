import logging

from django.core.management.base import BaseCommand
from django.db import transaction

from dictionary.models import Organization

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    @transaction.atomic
    def handle(self, *args, **options):
        qs = Organization.objects.all()
        qs_count = len(qs)
        for i, o in enumerate(qs):
            o.attributes = {'real_name': o.name}
            o.name = f'Организация {o.id}'
            o.save()
            logger.info(f'{i + 1}/{qs_count}\t{o.id}')
