from project.settings import BASE_DIR

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# CORS_ORIGIN_ALLOW_ALL = True
# CORS_ALLOW_CREDENTIALS = True

PROJECT_APPS = [
    'api',
    'acc',
    'dictionary',
    'main',
    'cv',
]

ADVANCED_APPS = [
    'project.contrib.management',
    'project.contrib.admin_tools',
    'project.contrib.db',
]

INSTALLED_APPS = (
        [
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            'django.contrib.humanize',
            'django_select2',
            'django_extensions',
            'django_json_widget',
            'django_filters',
            'django_pickling',
            'admin_auto_filters',
            'rest_framework',
            'drf_yasg',
            'cacheops',
            'sorl.thumbnail',
            'rangefilter',
            # 'corsheaders',
            'mptt',
            'adminsortable2',
            'reversion',
            'nested_admin',
            'guardian',
        ]
        + ADVANCED_APPS
        + PROJECT_APPS
)

MIDDLEWARE = [
    # 'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'reversion.middleware.RevisionMiddleware',
    'project.contrib.middleware.TimezoneMiddleware',
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
        ],
        'OPTIONS': {
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'

FIXTURE_DIRS = [
    BASE_DIR / 'fixtures'
]

if DEBUG:
    MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')
    INSTALLED_APPS.append('debug_toolbar')
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda _request: True
    }

if DJANGO_SILK_ENABLED:
    MIDDLEWARE.append('silk.middleware.SilkyMiddleware')
    INSTALLED_APPS.append('silk')

SILENCED_SYSTEM_CHECKS = [
    'debug_toolbar.W006',
]
