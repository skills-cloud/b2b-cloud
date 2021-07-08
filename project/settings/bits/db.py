import dj_database_url

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

DATABASE_ENGINE_POSTGRESQL = 'django.db.backends.postgresql'

DATABASES = {
    'default': dj_database_url.config(
        default='postgres://postgres:not1pass@pg/cloud'
    ),
}