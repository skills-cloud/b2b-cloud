from pathlib import Path

from typing import Optional
from django.core.management import call_command
from django.conf import settings

from project.celery import app


@app.task()
def db_dump(filename: Optional[str] = None):
    if not filename:
        filename = str(settings.GET_DB_DUMP_FILENAME_DEFAULT())
    filepath = Path(filename)
    if not filepath.exists():
        filepath.parent.mkdir(parents=True, exist_ok=True)
    call_command('db_dump', file_name=filename)
