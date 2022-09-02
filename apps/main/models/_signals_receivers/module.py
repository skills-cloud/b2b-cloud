from main import models as main_models
from main.services import get_work_days_count
from main.models._signals_receivers._base import SignalsReceiver


class ModuleSignalsReceiver(SignalsReceiver):
    instance: main_models.Module

    def pre_save(self, **kwargs):
        super().pre_save(**kwargs)
        if (
                not self.instance.work_days_count
                and self.instance.start_date
                and self.instance.deadline_date
        ):
            self.instance.work_days_count = get_work_days_count(
                self.instance.start_date,
                self.instance.deadline_date,
            )


class FunPointTypeSignalsReceiver(SignalsReceiver):
    instance: main_models.FunPointType


class FunPointTypeDifficultyLevelSignalsReceiver(SignalsReceiver):
    instance: main_models.FunPointTypeDifficultyLevel
