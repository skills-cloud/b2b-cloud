from django.db.models import signals

from main import models as main_models
from main.services import request_requirement

__all__ = ['setup']


class RequestRequirementReceiver:
    def post_save(self, sender, instance: main_models.RequestRequirement, **kwargs) -> None:
        request_requirement.request_requirement_time_slots_setup(instance)


class RequestRequirementCvReceiver:
    def post_save(self, sender, instance: main_models.RequestRequirementCv, **kwargs) -> None:
        request_requirement.request_requirement_cv_time_slots_setup(instance)


RECEIVER_INSTANCE = set()


def setup():
    for model, receiver_class in [
        [main_models.RequestRequirement, RequestRequirementReceiver],
        [main_models.RequestRequirementCv, RequestRequirementCvReceiver],
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
