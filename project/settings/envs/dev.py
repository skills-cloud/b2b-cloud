from project.settings import BASE_DIR

DEBUG = True

CACHEOPS_ENABLED = False

BASE_URL = 'http://local.tet-a-tet:10001'

ALLOWED_HOSTS = ['*']
INTERNAL_IPS = ['*']

CELERY_WORKER_CONCURRENCY = 2

EMAIL_FILE_PATH = BASE_DIR.parent / '.emails'
EMAIL_BACKEND_DEBUG = 'django.core.mail.backends.filebased.EmailBackend'

STATS_STEP_DELAY = 2


MEETING_BOOKING_TIMINGS_CHECK_DISABLED = True
MEETING_SLOT_TIMINGS_CHECK_DISABLED = True
