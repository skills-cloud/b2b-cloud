# Generated by Django 3.2.5 on 2022-09-08 10:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cv', '0020_languagelevel'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='languagelevel',
            options={'verbose_name': 'Language level', 'verbose_name_plural': 'Language levels'},
        ),
    ]