# Generated by Django 3.2.11 on 2022-01-19 18:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cv', '0015_round5_dict_org'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cv',
            name='is_resource_owner',
        ),
        migrations.AddField(
            model_name='cv',
            name='manager_rm',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='cv_list_as_rm', to=settings.AUTH_USER_MODEL, verbose_name='РМ'),
        ),
    ]
