# Generated by Django 3.2.5 on 2022-09-08 10:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0035_auto_20220908_1348'),
    ]

    operations = [
        migrations.AlterField(
            model_name='partner',
            name='services_type',
            field=models.CharField(choices=[('OUTSOURCE', 'Outsource'), ('OUTSTAFF', 'Outstaff'), ('BOTH', 'Both')], default='OUTSTAFF', max_length=15, verbose_name='services_type'),
        ),
    ]