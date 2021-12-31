from pathlib import Path

from django.core.management.base import BaseCommand

from cv.services.fw_cv_json import ImportFwCvJson


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('filepath', nargs='*')
        parser.add_argument('--no-skills', dest='without_skills', action='store_true')
        parser.add_argument('--skip-exists', dest='skip_exists', action='store_true')

    def handle(self, *args, **options):
        for filepath in options['filepath']:
            ImportFwCvJson(
                Path(filepath),
                without_skills=options['without_skills'],
                skip_exists=options['skip_exists'],
            ).do_import()
