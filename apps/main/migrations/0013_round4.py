# Generated by Django 3.2.5 on 2021-11-13 12:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_round4'),
    ]

    operations = [
        migrations.AddField(
            model_name='module',
            name='work_days_count',
            field=models.IntegerField(blank=True, help_text='если пусто, заполнится автоматически из расчета пятидневной рабочей недели<br>ПН-ПТ deadline_date-start_date', null=True, verbose_name='кол-во рабочих дней'),
        ),
        migrations.AddField(
            model_name='module',
            name='work_days_hours_count',
            field=models.IntegerField(default=8, verbose_name='кол-во рабочих часов в рабочем дне'),
        ),
        migrations.AlterField(
            model_name='request',
            name='module',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requests', to='main.module', verbose_name='модуль'),
        ),
    ]