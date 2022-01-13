# Generated by Django 3.2.11 on 2022-01-13 11:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0003_name_indexes'),
        ('cv', '0011_round5'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cvpositioncompetence',
            name='competence',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dictionary.competence', verbose_name='компетенция'),
        ),
    ]