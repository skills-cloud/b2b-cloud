import sys
import os
import environ

import dj_database_url

from pathlib import Path

from django.utils.translation import ugettext_lazy as _

from multiprocessing import cpu_count

env = environ.Env()
env.read_env('envs/.env')


BASE_URL = os.environ.get("BASE_URL")

ALLOWED_HOSTS = [
    "*",
    "127.0.0.1", "dev.b2bcloud.com",
    "89.108.124.151", "back.b2bcloud.com",
    "deven.b2bcloud.com"
]
INTERNAL_IPS = ["89.108.124.151"]
os.environ.setdefault("DJANGO_ENV", "dev")
DJANGO_ENV = os.environ.get("DJANGO_ENV")

sys.path.append("apps")

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = os.environ.get("DEBUG")

SECRET_KEY = "django-insecure-2mw(kwl1g&-t28nvir)jby8mk%%64ad$@v4_mnkgz&m=$-92kn"


USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# CORS_ORIGIN_ALLOW_ALL = True
# CORS_ALLOW_CREDENTIALS = True

PROJECT_APPS = [
    "api",
    "acc",
    "dictionary",
    "main",
    "cv",
]

ADVANCED_APPS = [
    "project.contrib.management",
    "project.contrib.admin_tools",
    "project.contrib.db",
]

INSTALLED_APPS = (
    [
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        "django.contrib.humanize",
        "django_select2",
        "django_extensions",
        "django_json_widget",
        "django_filters",
        "django_pickling",
        "admin_auto_filters",
        "rest_framework",
        "drf_yasg",
        "cacheops",
        "sorl.thumbnail",
        "rangefilter",
        # 'corsheaders',
        "mptt",
        "adminsortable2",
        "reversion",
        "nested_admin"
    ]
    + ADVANCED_APPS
    + PROJECT_APPS
)

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "reversion.middleware.RevisionMiddleware",
    "project.contrib.middleware.timezone.TimezoneMiddleware",
]

ROOT_URLCONF = "project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR / "templates")
        ],
        "OPTIONS": {
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "project.wsgi.application"

FIXTURE_DIRS = [BASE_DIR / "fixtures"]


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

DATABASE_ENGINE_POSTGRESQL = "django.db.backends.postgresql"

DATABASES = {
    "default": dj_database_url.config(
        default="postgres://postgres:not1pass@pg/cloud"
    )
}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTH_USER_MODEL = "acc.User"

LANGUAGE_CODE = "en"

TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = (
    ("en", _("English")),
    ("ru", _("Russian")),
)

LOCALE_PATHS = (os.path.join(BASE_DIR, "locale"),)

if DEBUG:
    MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")
    INSTALLED_APPS.append("debug_toolbar")
    DEBUG_TOOLBAR_CONFIG = {"SHOW_TOOLBAR_CALLBACK": lambda _request: True}

WWW_FILES_BASE_FOLDER = Path("/www")

FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o777
FILE_UPLOAD_PERMISSIONS = 0o777

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]


# STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
# STATIC_ROOT = WWW_FILES_BASE_FOLDER / "assets"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

STATIC_URL = "/api/assets/"


MEDIA_URL = "/storage/"
MEDIA_ROOT = WWW_FILES_BASE_FOLDER / "storage"

FILE_UPLOAD_HANDLERS = [
    "django.core.files.uploadhandler.TemporaryFileUploadHandler",
]

SESSION_COOKIE_NAME = "_id_"
CSRF_COOKIE_NAME = "_sec_"

LOGIN_URL = "/api/login/"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ("api.authentication.SessionAuthentication",),
    # "DEFAULT_PERMISSION_CLASSES": ("api.permissions.IsAuthenticated",),
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    "DEFAULT_PAGINATION_CLASS": "api.pagination.DefaultPagination",
    "DEFAULT_RENDERER_CLASSES": ("drf_ujson.renderers.UJSONRenderer",),
    "DEFAULT_PARSER_CLASSES": ("drf_ujson.parsers.UJSONParser",),
    "EXCEPTION_HANDLER": "api.exceptions.custom_exception_handler",
}

SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": [],
    "USE_SESSION_AUTH": True,
    "REFETCH_SCHEMA_WITH_AUTH": True,
}


REDIS_HOST = os.environ.get("REDIS_HOST") or "redis"
REDIS_PORT = os.environ.get("REDIS_PORT") or 6379
REDIS_CONNECT_RETRY = True

REDIS_ENABLED = True

REDIS_DB_SESSION = 1
REDIS_DB_CACHE_DEFAULT = 2
REDIS_DB_CACHE_SELECT2 = 3
REDIS_DB_CACHE_CACHEOPS = 4
REDIS_DB_CELERY = 5

SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = False
SESSION_COOKIE_AGE = 3600 * 24 * 30
SESSION_COOKIE_ANONYMOUS_AGE = 3600 * 24 * 3

SESSION_ENGINE = "redis_sessions.session"
SESSION_REDIS = {
    "host": REDIS_HOST,
    "port": REDIS_PORT,
    "db": REDIS_DB_SESSION,
    "retry_on_timeout": True,
    "socket_timeout": 2,
}


CACHES = {
    cache_name: {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/{cache_db}",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "DB": cache_db,
        },
    }
    for cache_name, cache_db in [
        ["default", REDIS_DB_CACHE_DEFAULT],
        ["select2", REDIS_DB_CACHE_SELECT2],
    ]
}

SELECT2_CACHE_BACKEND = "select2"

CACHEOPS_REDIS = {
    "host": REDIS_HOST,
    "port": REDIS_PORT,
    "db": REDIS_DB_CACHE_CACHEOPS,
}
CACHEOPS_DEFAULTS = {"timeout": 60**2 * 24 * 365}
CACHEOPS = {
    "auth.*": {"ops": "all"},
    "acc.*": {"ops": "all"},
    "cv.*": {"ops": "all"},
    "dictionary.*": {"ops": "all"},
    "main.*": {"ops": "all"},
    "sorl.thumbnail.*": {"ops": "all"},
}


CELERY_WORKER_CONCURRENCY = cpu_count()

EMAIL_HOST = os.getenv("EMAIL_HOST", "192.168.0.1")
EMAIL_PORT = os.getenv("EMAIL_PORT", 25)
EMAIL_USER = os.getenv("EMAIL_USER", "info@b2bcloud.com")
EMAIL_USE_TLS = False
DEFAULT_FROM_EMAIL = EMAIL_USER
CELERY_EMAIL_CHUNK_SIZE = 1
CELERY_EMAIL_TASK_CONFIG = {
    "name": "djcelery_email_send",
    "rate_limit": "500/m",
    "ignore_result": True,
}
CELERY_EMAIL_MESSAGE_EXTRA_ATTRIBUTES = []

STATS_STEP_DELAY = 10  # sec
CELERY_ENABLED = True

CELERY = {
    "broker_url": "redis://%s:%s/%s" % (REDIS_HOST, REDIS_PORT, REDIS_DB_CELERY),
    "enable_utc": True,
    "timezone": TIME_ZONE,
    "accept_content": ["json", "pickle"],
    "task_serializer": "pickle",
    "result_serializer": "pickle",
    "worker_disable_rate_limits": True,
    "worker_pool_restarts": True,
    "worker_concurrency": CELERY_WORKER_CONCURRENCY,
    "task_ignore_result": True,
    "result_expires": 60 * 60 * 4,
}


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {},
    "formatters": {
        "colored": {
            "()": "project.contrib.logging.formaters.ColoredExtraFormatter",
            "format": "%(log_color)s[%(levelname)s] %(asctime)s :: %(message)s",
            "log_colors": {
                "DEBUG": "bold_black",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        }
    },
    "handlers": {
        "console_colored": {
            "class": "colorlog.StreamHandler",
            "formatter": "colored",
        },
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console_colored"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
