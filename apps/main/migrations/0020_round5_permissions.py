from django.db import migrations, models
import django.db.models.deletion


def f(apps, schema_editor):
    OrganizationProject = apps.get_model("main", "OrganizationProject")
    OrganizationContractor = apps.get_model("main", "OrganizationContractor")
    customer = OrganizationContractor.objects.filter(id=42977).first() or OrganizationContractor.objects.first()
    OrganizationProject.objects.update(organization_contractor=customer)


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0019_round5_permissions'),
    ]

    operations = [
        migrations.RunPython(f)
    ]
