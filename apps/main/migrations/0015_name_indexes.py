# Generated by Django 3.2.5 on 2021-12-31 00:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0014_round4'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='name',
            field=models.CharField(db_index=True, max_length=500, verbose_name='название'),
        ),
    ]
