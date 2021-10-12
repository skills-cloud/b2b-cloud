import logging
from dataclasses import dataclass
from django.db import transaction

from main.models import RequestRequirementCvStatus

from cv.models import CV, CvTimeSlot

__all__ = [
    'CvTimeSlotService',
]

logger = logging.getLogger(__name__)


@dataclass
class CvTimeSlotService:
    cv: CV

    @transaction.atomic
    def setup_requests_slots(self):
        logger.debug('CvTimeSlotService.setup', extra={'cv': self.cv})
        self._clean_requests_slots()
        self._setup_requests_slots()

    def _clean_requests_slots(self):
        self.cv.time_slots.filter(request_requirement_link__isnull=False).delete()

    def _setup_requests_slots(self):
        for_create = []
        for request_requirement_link in (
                self.cv.requests_requirements_links
                        .filter(status=RequestRequirementCvStatus.WORKER)
                        .prefetch_related('request_requirement')
        ):
            date_from = None
            date_to = None
            if (
                    request_requirement_link.date_from
                    or request_requirement_link.date_to
            ):
                date_from = request_requirement_link.date_from
                date_to = request_requirement_link.date_to
            elif (
                    request_requirement_link.request_requirement.date_from
                    or request_requirement_link.request_requirement.date_to
            ):
                date_from = request_requirement_link.request_requirement.date_from
                date_to = request_requirement_link.request_requirement.date_to
            if date_from and date_to:
                for_create.append(
                    CvTimeSlot(
                        cv=self.cv,
                        request_requirement_link=request_requirement_link,
                        type_of_employment=request_requirement_link.request_requirement.type_of_employment,
                        date_from=date_from,
                        date_to=date_to,
                        is_free=False,
                    )
                )
        if for_create:
            CvTimeSlot.objects.bulk_create(for_create)
