import sys
from pathlib import Path
from os import environ
from split_settings.tools import include, optional

sys.path.append('apps')

DEBUG = False
DJANGO_SILK_ENABLED = False

environ.setdefault('DJANGO_ENV', 'dev')
DJANGO_ENV = environ['DJANGO_ENV']

environ.setdefault('DJANGO_TEST', '')
DJANGO_TEST = environ['DJANGO_TEST']

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = 'django-insecure-2mw(kwl1g&-t28nvir)jby8mk%%64ad$@v4_mnkgz&m=$-92kn'

_base_settings = (
    f'envs/{DJANGO_ENV}.py',
    'bits/db.py',
    'bits/acc.py',
    'bits/locale.py',
    'bits/static.py',
    'bits/redis.py',
    'bits/cache.py',
    'bits/celery.py',
    'bits/email.py',
    'bits/api.py',
    'bits/log.py',
    'bits/test_users.py',
    optional('settings_local.py'),
    'bits/_last.py',
)

include(*_base_settings)

GRAPH_MODELS = {
    'all_applications': True,
    'group_models': True,
}
