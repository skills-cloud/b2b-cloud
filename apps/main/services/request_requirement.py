from django.db import transaction

from main.models import RequestRequirementCv, RequestRequirement
from cv.services.cv_time_slot import CvTimeSlotService

__all__ = [
    'request_requirement_time_slots_setup',
    'request_requirement_cv_time_slots_setup',
]


@transaction.atomic
def request_requirement_time_slots_setup(instance: RequestRequirement):
    for cv_link in instance.cv_links.all():
        request_requirement_cv_time_slots_setup(cv_link)


@transaction.atomic
def request_requirement_cv_time_slots_setup(instance: RequestRequirementCv):
    CvTimeSlotService(instance.cv).setup()
