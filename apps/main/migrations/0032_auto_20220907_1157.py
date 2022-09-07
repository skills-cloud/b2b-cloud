# Generated by Django 3.2.5 on 2022-09-07 08:57

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0010_auto_20220906_1337'),
        ('main', '0031_auto_20220907_1053'),
    ]

    operations = [
        migrations.AlterField(
            model_name='partner',
            name='category',
            field=models.ManyToManyField(related_name='categories', to='dictionary.Category', verbose_name='category'),
        ),
        migrations.AlterField(
            model_name='partner',
            name='services_type',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(choices=[('OUTSOURCE', 'Outsource'), ('OUTSTAFF', 'Outstaff'), ('BOTH', 'Both')], max_length=255, verbose_name='services_type'), size=None),
        ),
    ]