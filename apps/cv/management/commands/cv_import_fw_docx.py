from pathlib import Path

from django.core.management.base import BaseCommand

from cv.services.fw_cv import import_fw_cv_file_docx


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('filepath')

    def handle(self, *args, **options):
        import_fw_cv_file_docx(Path(options['filepath']))
