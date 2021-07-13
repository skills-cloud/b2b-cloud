from main import models as main_models
from api.serializers import ModelSerializer


class OrganizationSerializer(ModelSerializer):
    class Meta:
        model = main_models.Organization
        exclude = ['created_at', 'updated_at']
