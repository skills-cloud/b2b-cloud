# Generated by Django 3.2.12 on 2022-02-02 11:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0006_round5_dict_org'),
        ('cv', '0018_alter_cv_attributes'),
        ('main', '0025_round5_dict_org'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requestrequirement',
            name='position',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='requests_requirements', to='dictionary.position', verbose_name='должность'),
        ),
        migrations.AlterField(
            model_name='timesheetrow',
            name='cv',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='time_sheet_rows', to='cv.cv', verbose_name='анкета исполнителя'),
        ),
    ]