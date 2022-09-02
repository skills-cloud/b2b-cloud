# Generated by Django 3.2.5 on 2021-12-30 19:38

import django.contrib.postgres.indexes
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('cv', '0009_round3_3'),
    ]

    operations = [
        migrations.AddField(
            model_name='cv',
            name='attributes',
            field=models.JSONField(default=dict,
                                   help_text='если вы не до конца понимаете назначение этого поля, '
                                             'вам лучше избежать редактирования',
                                   verbose_name='доп. атрибуты'),
        ),

        migrations.AddIndex(
            model_name='cv',
            index=django.contrib.postgres.indexes.GinIndex(fields=['attributes'], name='cv_cv_attribu_f794b4_gin'),
        ),
    ]
