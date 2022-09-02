from main import models as main_models
from main.models._signals_receivers._base import SignalsReceiver


class OrganizationProjectSignalsReceiver(SignalsReceiver):
    instance: main_models.OrganizationProject


class OrganizationProjectUserRoleSignalsReceiver(SignalsReceiver):
    instance: main_models.OrganizationProjectUserRole
