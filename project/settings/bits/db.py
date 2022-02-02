import datetime
import dj_database_url
from pathlib import Path

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

DATABASE_ENGINE_POSTGRESQL = 'django.db.backends.postgresql'

DATABASES = {
    'default': dj_database_url.config(
        default='postgres://postgres:not1pass@pg/cloud'
    ),
}


def GET_DB_DUMP_FILENAME_DEFAULT() -> Path:
    from project.settings import MEDIA_ROOT, DJANGO_ENV
    return Path(MEDIA_ROOT) / 'DB_DUMP' / f'b2b-{DJANGO_ENV}-{datetime.datetime.now().strftime("%Y%m%d%H%M")}.sql'
