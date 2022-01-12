from main import models as main_models
from main.models._signals_receivers._base import SignalsReceiver


class OrganizationContractorSignalsReceiver(SignalsReceiver):
    instance: main_models.OrganizationContractor


class OrganizationCustomerSignalsReceiver(SignalsReceiver):
    instance: main_models.OrganizationCustomer
