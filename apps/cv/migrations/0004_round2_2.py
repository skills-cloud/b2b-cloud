# Generated by Django 3.2.5 on 2021-09-02 11:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0002_round1_imports'),
        ('cv', '0003_round2'),
    ]

    operations = [
        migrations.AddField(
            model_name='cv',
            name='linked',
            field=models.ManyToManyField(blank=True, related_name='_cv_cv_linked_+', to='cv.CV', verbose_name='связанные анкеты'),
        ),
        migrations.AddField(
            model_name='cv',
            name='price',
            field=models.FloatField(blank=True, null=True, verbose_name='ставка'),
        ),
        migrations.AddField(
            model_name='cv',
            name='types_of_employment',
            field=models.ManyToManyField(blank=True, to='dictionary.TypeOfEmployment', verbose_name='тип занятости'),
        ),
    ]
