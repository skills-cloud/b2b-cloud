from main import models as main_models
from api.fields import PrimaryKeyRelatedIdField
from api.serializers import ModelSerializer


class OrganizationSerializer(ModelSerializer):
    class Meta:
        model = main_models.Organization
        exclude = ['created_at', 'updated_at']


class OrganizationProjectSerializer(ModelSerializer):
    organization_id = PrimaryKeyRelatedIdField(
        queryset=main_models.Organization.objects
    )
    organization = OrganizationSerializer()

    class Meta:
        model = main_models.OrganizationProject
        exclude = ['created_at', 'updated_at']
