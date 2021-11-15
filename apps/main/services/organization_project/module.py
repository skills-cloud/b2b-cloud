import datetime
import math
from collections import OrderedDict
from dataclasses import dataclass
from typing import Dict, Optional

from dictionary.models import Position
from main import models as main_models


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


@dataclass
class ModuleLaborEstimateService:
    instance: main_models.Module

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
        result.positions_estimates = self._sort_positions_estimates({
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
        result.positions_estimates = self._sort_positions_estimates(requested, 'workers_count')
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
        result.positions_estimates = self._sort_positions_estimates(diff)
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
        result.positions_estimates = self._sort_positions_estimates(diff, 'workers_count')
        return result

    def _get_empty_labor_estimate(self) -> LaborEstimate:
        return LaborEstimate(
            date_from=self.instance.start_date,
            date_to=self.instance.deadline_date,
            work_days_count=self.instance.work_days_count,
            work_day_hours_count=self.instance.work_days_hours_count,
            positions_estimates={},
        )

    @classmethod
    def _sort_positions_estimates(
            cls,
            estimates: Dict[int, PositionLaborEstimate],
            key_field='hours_count'
    ) -> OrderedDict[int, PositionLaborEstimate]:
        return OrderedDict([
            (k, v)
            for k, v in sorted(estimates.items(), key=lambda x: getattr(x[1], key_field), reverse=True)
        ])
