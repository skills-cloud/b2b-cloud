# Generated by Django 3.2.11 on 2022-01-19 17:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0024_round5_fk_2_user_set_null'),
    ]

    operations = [
        migrations.RunSQL('''
DELETE FROM main_organization WHERE NOT is_customer AND NOT is_contractor 
        ''')
    ]
