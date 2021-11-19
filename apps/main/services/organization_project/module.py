import datetime
import itertools
import json
import math
import pprint
from collections import OrderedDict
from dataclasses import dataclass
from typing import Dict, Optional

from django.db import transaction

from dictionary.models import Position
from main import models as main_models


def _prepare_positions_estimates(
        estimates: Dict[int, 'PositionLaborEstimate'],
        key_field: str = 'hours_count',
        is_skip_zero: bool = False,
) -> OrderedDict[int, 'PositionLaborEstimate']:
    return OrderedDict([
        (k, v)
        for k, v in sorted(estimates.items(), key=lambda x: getattr(x[1], key_field), reverse=True)
        if not is_skip_zero or getattr(v, key_field) != 0
    ])


@dataclass
class PositionLaborEstimate:
    position: Position
    hours_count: Optional[int]
    workers_count: int


@dataclass
class LaborEstimate:
    date_from: Optional[datetime.date]
    date_to: Optional[datetime.date]
    work_days_count: Optional[int]
    work_day_hours_count: int
    positions_estimates: Dict[int, PositionLaborEstimate]
    """{ position_id: PositionLaborEstimate }"""

    def __add__(self, other: 'LaborEstimate'):
        positions_estimates = {}
        for est in itertools.chain(self.positions_estimates.values(), other.positions_estimates.values()):
            pid = est.position.id
            if pid not in positions_estimates:
                positions_estimates[pid] = est
            else:
                if not positions_estimates[pid].workers_count:
                    positions_estimates[pid].workers_count = est.workers_count
                else:
                    positions_estimates[pid].workers_count += est.workers_count
                if not positions_estimates[pid].hours_count:
                    positions_estimates[pid].hours_count = est.hours_count
                else:
                    positions_estimates[pid].hours_count += est.hours_count
        date_from = self.date_from or other.date_from
        if self.date_from and other.date_from:
            date_from = min(self.date_from, other.date_from)
        date_to = self.date_from or other.date_from
        if self.date_to and other.date_to:
            date_to = max(self.date_to, other.date_to)
        return LaborEstimate(
            date_from=date_from,
            date_to=date_to,
            work_days_count=(self.work_days_count or 0) + (other.work_days_count or 0),
            work_day_hours_count=(self.work_day_hours_count or 0) + (other.work_day_hours_count or 0),
            positions_estimates=_prepare_positions_estimates(positions_estimates),
        )


@dataclass
class ModuleLaborEstimateService:
    instance: main_models.Module

    @transaction.atomic
    def set_expected_labor_estimate_as_saved(self) -> bool:
        if not self.get_expected_minus_saved_labor_estimate().positions_estimates:
            return False
        self.instance.positions_labor_estimates.all().delete()
        for_create = []
        for est in self.get_expected_labor_estimate().positions_estimates.values():
            for_create.append(main_models.ModulePositionLaborEstimate(
                module=self.instance,
                position=est.position,
                count=est.workers_count,
                hours=est.hours_count,
            ))
        main_models.ModulePositionLaborEstimate.objects.bulk_create(for_create)
        return True

    @transaction.atomic
    def create_request_for_saved_labor_estimate(self) -> Optional[main_models.Request]:
        estimates_diff = [
            estimate
            for estimate in self.get_saved_minus_requested_labor_estimate().positions_estimates.values()
            if estimate.workers_count > 0
        ]
        if not estimates_diff:
            return
        request = main_models.Request(
            module=self.instance
        )
        request.save()
        for position_estimate in estimates_diff:
            requirement = main_models.RequestRequirement(
                request=request,
                position=position_estimate.position,
                count=position_estimate.workers_count,
            )
            requirement.save()
        return request

    def get_expected_labor_estimate(self) -> LaborEstimate:
        estimates = {}
        positions = {}
        for fun_point in self.instance.fun_points.all():
            for position_labor_estimate in fun_point.fun_point_type.positions_labor_estimates.all():
                position_id = position_labor_estimate.position_id
                if position_id not in estimates:
                    estimates[position_id] = 0
                estimates[position_id] += position_labor_estimate.hours * fun_point.difficulty_factor
                if position_id not in positions:
                    positions[position_id] = position_labor_estimate.position
        work_days = self.instance.work_days_count
        work_day_hours = self.instance.work_days_hours_count
        result_estimates = []
        for position_id, estimate_hours_count in sorted(estimates.items(), key=lambda x: x[1], reverse=True):
            estimate_days_count = math.ceil(estimate_hours_count / work_day_hours)
            estimate_workers_count = 1
            if work_days:
                estimate_workers_count = math.ceil(estimate_days_count / work_days)
            result_estimates.append(PositionLaborEstimate(
                position=positions[position_id],
                hours_count=estimate_hours_count,
                workers_count=estimate_workers_count,
            ))
        result = self._get_empty_labor_estimate()
        result.positions_estimates = OrderedDict((row.position.id, row) for row in result_estimates)
        return result

    def get_saved_labor_estimate(self) -> LaborEstimate:
        result = self._get_empty_labor_estimate()
        result.positions_estimates = _prepare_positions_estimates({
            row.position_id: PositionLaborEstimate(
                position=row.position,
                hours_count=row.hours,
                workers_count=row.count,
            )
            for row in self.instance.positions_labor_estimates.all()
        })
        return result

    def get_requested_labor_estimate(self) -> LaborEstimate:
        requested = {}
        for request in self.instance.requests.all():
            for requirement in request.requirements.all():
                if requirement.position_id not in requested:
                    requested[requirement.position_id] = PositionLaborEstimate(
                        position=requirement.position,
                        hours_count=None,
                        workers_count=0,
                    )
                requested[requirement.position_id].workers_count += requirement.count
        result = self._get_empty_labor_estimate()
        result.positions_estimates = _prepare_positions_estimates(requested, 'workers_count')
        return result

    def get_expected_minus_saved_labor_estimate(self) -> LaborEstimate:
        expected = self.get_expected_labor_estimate().positions_estimates
        saved = self.get_saved_labor_estimate().positions_estimates
        diff = {}
        for position_id in set(expected.keys()) | set(saved.keys()):
            pos_expected = expected.get(position_id)
            pos_saved = saved.get(position_id)
            diff[position_id] = PositionLaborEstimate(
                position=getattr(pos_expected, 'position', None) or getattr(pos_saved, 'position', None),
                hours_count=getattr(pos_expected, 'hours_count', 0) - getattr(pos_saved, 'hours_count', 0),
                workers_count=getattr(pos_expected, 'workers_count', 0) - getattr(pos_saved, 'workers_count', 0),
            )
        result = self._get_empty_labor_estimate()
        result.positions_estimates = _prepare_positions_estimates(diff, is_skip_zero=True)
        return result

    def get_saved_minus_requested_labor_estimate(self) -> LaborEstimate:
        saved = self.get_saved_labor_estimate().positions_estimates
        requested = self.get_requested_labor_estimate().positions_estimates
        diff = {}
        for position_id in set(saved.keys()) | set(requested.keys()):
            pos_saved = saved.get(position_id)
            pos_requested = requested.get(position_id)
            diff[position_id] = PositionLaborEstimate(
                position=getattr(pos_saved, 'position', None) or getattr(pos_requested, 'position', None),
                hours_count=None,
                workers_count=getattr(pos_saved, 'workers_count', 0) - getattr(pos_requested, 'workers_count', 0),
            )
        result = self._get_empty_labor_estimate()
        result.positions_estimates = _prepare_positions_estimates(diff, 'workers_count', is_skip_zero=True)
        return result

    def _get_empty_labor_estimate(self) -> LaborEstimate:
        return LaborEstimate(
            date_from=self.instance.start_date,
            date_to=self.instance.deadline_date,
            work_days_count=self.instance.work_days_count,
            work_day_hours_count=self.instance.work_days_hours_count,
            positions_estimates={},
        )
