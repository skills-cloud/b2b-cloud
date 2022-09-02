from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'
    verbose_name = _('Организации, модули и запросы')

    def ready(self):
        from main.models._signals_receivers import setup as signals_receivers_setup
        signals_receivers_setup()
