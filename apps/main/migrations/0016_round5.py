# Generated by Django 3.2.10 on 2022-01-04 01:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0015_name_indexes'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrganizationContractor',
            fields=[
            ],
            options={
                'verbose_name': 'организация исполнитель',
                'verbose_name_plural': 'организации исполнители',
                'ordering': ['name'],
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('main.organization',),
        ),
        migrations.CreateModel(
            name='OrganizationCustomer',
            fields=[
            ],
            options={
                'verbose_name': 'организация заказчик',
                'verbose_name_plural': 'организации заказчики',
                'ordering': ['name'],
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('main.organization',),
        ),
        migrations.AddField(
            model_name='organization',
            name='is_contractor',
            field=models.BooleanField(default=False, verbose_name='исполнитель?'),
        ),
        migrations.AlterField(
            model_name='funpointtype',
            name='organization',
            field=models.ForeignKey(blank=True, help_text='глобальный тип, если оставить это поле пустым', null=True,
                                    on_delete=django.db.models.deletion.CASCADE, related_name='fun_points_types',
                                    to='main.organizationcustomer', verbose_name='заказчик'),
        ),
        migrations.AlterField(
            model_name='organizationproject',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='projects',
                                    to='main.organizationcustomer', verbose_name='заказчик'),
        ),
        migrations.AddField(
            model_name='organization',
            name='contractor',
            field=models.ForeignKey(blank=True, help_text='имеет значение только для организаций заказчиков', null=True,
                                    on_delete=django.db.models.deletion.SET_NULL, to='main.organizationcontractor',
                                    verbose_name='исполнитель для этого заказчика'),
        ),
        migrations.AlterField(
            model_name='organization',
            name='is_contractor',
            field=models.BooleanField(default=False, verbose_name='это исполнитель?'),
        ),
        migrations.AlterField(
            model_name='organization',
            name='is_customer',
            field=models.BooleanField(default=False, verbose_name='это заказчик?'),
        ),
    ]