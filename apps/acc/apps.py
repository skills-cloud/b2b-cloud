from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AccConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'acc'
    verbose_name = _('Пользователи и роли')

    def ready(self):
        from acc._signals_receivers import setup as signals_receivers_setup
        signals_receivers_setup()
