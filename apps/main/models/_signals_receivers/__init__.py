from typing import Type
from django.db.models import signals, Model

from project.contrib.disable_for_loaddata import disable_for_loaddata
from main.models._signals_receivers._base import SignalsReceiver
from main.services.organization_project import request_requirement
from main import models as main_models
from main.models._signals_receivers.module import ModuleSignalsReceiver

__all__ = ['setup']


class Receiver:
    receiver_class: Type[SignalsReceiver]

    @disable_for_loaddata
    def pre_save(self, sender, instance: Model, **kwargs) -> None:
        self._get_service(instance).pre_save(sender=sender, **kwargs)

    @disable_for_loaddata
    def post_save(self, sender, instance: Model, **kwargs) -> None:
        self._get_service(instance).post_save(sender=sender, **kwargs)

    @disable_for_loaddata
    def pre_delete(self, sender, instance: Model, **kwargs) -> None:
        self._get_service(instance).pre_delete(sender=sender, **kwargs)

    @disable_for_loaddata
    def post_delete(self, sender, instance: Model, **kwargs) -> None:
        self._get_service(instance).post_delete(sender=sender, **kwargs)

    def _get_service(self, instance: Model) -> SignalsReceiver:
        return self.receiver_class(instance)


class RequestRequirementReceiver:
    def post_save(self, sender, instance: main_models.RequestRequirement, **kwargs) -> None:
        request_requirement.request_requirement_time_slots_setup(instance)


class RequestRequirementCvReceiver:
    def post_save(self, sender, instance: main_models.RequestRequirementCv, **kwargs) -> None:
        request_requirement.request_requirement_cv_time_slots_setup(instance)


class ModuleReceiver(Receiver):
    receiver_class = ModuleSignalsReceiver


RECEIVER_INSTANCE = set()


def setup():
    for model, receiver_class in [
        [main_models.RequestRequirement, RequestRequirementReceiver],
        [main_models.RequestRequirementCv, RequestRequirementCvReceiver],
        [main_models.Module, ModuleReceiver],
    ]:
        receiver = receiver_class()
        RECEIVER_INSTANCE.add(receiver)
        for singal, reciever_func_name in [
            [signals.pre_save, 'pre_save'],
            [signals.post_save, 'post_save'],
            [signals.pre_delete, 'pre_delete'],
            [signals.post_delete, 'post_delete'],
        ]:
            if hasattr(receiver, reciever_func_name):
                singal.connect(getattr(receiver, reciever_func_name), sender=model)
