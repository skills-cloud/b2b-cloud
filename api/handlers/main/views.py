from main import models as main_models
from api.handlers.main import serializers as main_serializers
from api.handlers.dictionary.views import DictionaryBaseViewSet


class OrganizationViewSet(DictionaryBaseViewSet):
    queryset = main_models.Organization.objects
    serializer_class = main_serializers.OrganizationSerializer
