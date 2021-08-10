import os
from multiprocessing import cpu_count

DEBUG = False

BASE_URL = 'https://test.dev.b2bcloud.com/'

ALLOWED_HOSTS = ['*']
INTERNAL_IPS = ['*']

CELERY_WORKER_CONCURRENCY = cpu_count()

EMAIL_HOST = os.getenv('EMAIL_HOST', '192.168.0.1')
EMAIL_PORT = os.getenv('EMAIL_PORT', 25)
EMAIL_USER = os.getenv('EMAIL_USER', 'info@b2bcloud.com')
EMAIL_USE_TLS = False
DEFAULT_FROM_EMAIL = EMAIL_USER
CELERY_EMAIL_CHUNK_SIZE = 1
CELERY_EMAIL_TASK_CONFIG = {
    'name': 'djcelery_email_send',
    'rate_limit': '500/m',
    'ignore_result': True,
}
CELERY_EMAIL_MESSAGE_EXTRA_ATTRIBUTES = []

STATS_STEP_DELAY = 10  # sec
