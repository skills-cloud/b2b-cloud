from pathlib import Path

from django.core.management.base import BaseCommand

from cv.services.fw_cv import import_fw_cv_file_txt


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('filepath', nargs='*')

    def handle(self, *args, **options):
        for filepath in options['filepath']:
            print(import_fw_cv_file_txt(Path(filepath)))
            print('*' * 80)
