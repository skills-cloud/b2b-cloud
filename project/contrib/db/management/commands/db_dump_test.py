from django.core.management.base import BaseCommand

from project.contrib.db.tasks import db_dump


class Command(BaseCommand):
    def handle(self, *args, **options):
        db_dump()
