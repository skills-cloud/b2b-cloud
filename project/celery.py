import os
import celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')


class Celery(celery.Celery):
    def on_configure(self):
        pass


app = Celery('app', config_source=settings.CELERY)
app.autodiscover_tasks()
