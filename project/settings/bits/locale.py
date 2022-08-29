import os

from django.utils.translation import ugettext_lazy as _

from project.settings import BASE_DIR


LANGUAGE_CODE = 'en'

TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = (
    ('en', _('English')),
    ('ru', _('Russian')),
)

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)
