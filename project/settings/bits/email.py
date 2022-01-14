import os
from . import *

# EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'

EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.yandex.ru')
EMAIL_PORT = os.getenv('EMAIL_PORT', 587)
EMAIL_HOST_USER = os.getenv('EMAIL_USER', 'noreply@digitalcore.ru')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_PASSWORD', '123456')
EMAIL_USE_TLS = True

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

EMAIL_CONTEXT = {
    'protocol': 'https',
    'domain': 'b2bcloud.com',
    'base_url': BASE_URL,
    'info_email': f'info@b2bcloud.com',
}
