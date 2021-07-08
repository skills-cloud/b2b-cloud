import datetime
import logging
from django.core.management.base import BaseCommand

from main.models import MeetingHost

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        message = f'message %s'
        extra = {
            'datetime': datetime.datetime.now(),
            'django_obj': MeetingHost.objects.first()
        }
        for what in ['debug', 'info', 'warning', 'error', 'critical']:
            getattr(logger, what)(message % what, extra=extra)
