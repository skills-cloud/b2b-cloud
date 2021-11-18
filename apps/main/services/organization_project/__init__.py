from dataclasses import dataclass
from typing import Optional

from main import models as main_models
from main.services.organization_project.module import ModuleLaborEstimateService, LaborEstimate, PositionLaborEstimate


@dataclass
class ProjectLaborEstimateService:
    instance: main_models.OrganizationProject

    def get_expected_labor_estimate(self) -> Optional[LaborEstimate]:
        ...

    def get_saved_labor_estimate(self) -> Optional[LaborEstimate]:
        project_estimate = None
        for module in self.instance.modules.all():
            module_service = ModuleLaborEstimateService(module)
            module_estimate = module_service.get_saved_labor_estimate()
            if not project_estimate:
                project_estimate = module_estimate
            else:
                project_estimate += module_estimate
        return project_estimate

    def get_requested_labor_estimate(self) -> Optional[LaborEstimate]:
        ...

    def get_expected_minus_saved_labor_estimate(self) -> Optional[LaborEstimate]:
        ...

    def get_saved_minus_requested_labor_estimate(self) -> Optional[LaborEstimate]:
        ...
