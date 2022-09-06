# Generated by Django 3.2.5 on 2022-09-06 10:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('currency', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='currencyreference',
            options={'verbose_name': 'Currency reference', 'verbose_name_plural': 'Currency references'},
        ),
        migrations.AlterField(
            model_name='currencyreference',
            name='currency_name',
            field=models.CharField(max_length=40, verbose_name='Currency name'),
        ),
        migrations.AlterField(
            model_name='currencyreference',
            name='designation',
            field=models.CharField(max_length=5, verbose_name='Designation'),
        ),
        migrations.AlterField(
            model_name='currencyreference',
            name='digital_code',
            field=models.CharField(max_length=5, verbose_name='Digital code'),
        ),
    ]
