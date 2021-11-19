import logging
from django.db.models import Model

logger = logging.getLogger(__name__)


class SignalsReceiver:
    instance: Model

    def __init__(self, instance: Model):
        self.instance = instance

    def pre_save(self, **kwargs) -> None:
        self._log_signal('pre_save', **kwargs)

    def post_save(self, **kwargs) -> None:
        self._log_signal('post_save', **kwargs)

    def pre_delete(self, **kwargs) -> None:
        self._log_signal('pre_delete', **kwargs)

    def post_delete(self, **kwargs) -> None:
        self._log_signal('post_delete', **kwargs)

    def _log_signal(self, name: str, **kwargs):
        logger.info(f'{self.__class__.__name__}.{name}', extra={
            'instance_id': self.instance.id,
            'diff': self.instance.diff,
        })
