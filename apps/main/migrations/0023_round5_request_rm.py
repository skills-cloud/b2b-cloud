# Generated by Django 3.2.11 on 2022-01-19 18:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0022_round5_project_pm_pfm'),
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='manager_rm',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='requests_as_rm', to=settings.AUTH_USER_MODEL, verbose_name='RM'),
        ),
    ]
