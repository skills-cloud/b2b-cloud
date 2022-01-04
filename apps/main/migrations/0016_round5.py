from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
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
        migrations.CreateModel(
            name='OrganizationContractorUserRole',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('employee', 'Специалист'), ('admin', 'Администратор'),
                                                   ('pfm', 'Руководитель портфеля проектов'),
                                                   ('pm', 'Руководитель проекта '), ('rm', 'Ресурсный менеджер')],
                                          max_length=50)),
                ('organization_contractor',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='users_roles',
                                   to='main.organizationcontractor', verbose_name='организация исполнитель')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                           related_name='organizations_contractors_roles',
                                           to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'роль пользователя',
                'verbose_name_plural': 'роли пользователей',
                'unique_together': {('organization_contractor', 'user', 'role')},
            },
        ),
        migrations.CreateModel(
            name='OrganizationProjectUserRole',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('employee', 'Специалист'), ('admin', 'Администратор'),
                                                   ('pfm', 'Руководитель портфеля проектов'),
                                                   ('pm', 'Руководитель проекта '), ('rm', 'Ресурсный менеджер')],
                                          max_length=50)),
                ('organization_project',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='users_roles',
                                   to='main.organizationproject', verbose_name='проект')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                           related_name='organizations_projects_roles', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'роль пользователя',
                'verbose_name_plural': 'роли пользователей',
                'unique_together': {('organization_project', 'user', 'role')},
            },
        ),
        migrations.AlterField(
            model_name='organizationcontractoruserrole',
            name='role',
            field=models.CharField(choices=[('employee', 'Специалист'), ('admin', 'Администратор'),
                                            ('pfm', 'Руководитель портфеля проектов'), ('pm', 'Руководитель проекта '),
                                            ('rm', 'Ресурсный менеджер')], max_length=50, verbose_name='роль'),
        ),
        migrations.AlterField(
            model_name='organizationcontractoruserrole',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    related_name='organizations_contractors_roles', to=settings.AUTH_USER_MODEL,
                                    verbose_name='пользователь'),
        ),
        migrations.AlterField(
            model_name='organizationprojectuserrole',
            name='role',
            field=models.CharField(choices=[('employee', 'Специалист'), ('admin', 'Администратор'),
                                            ('pfm', 'Руководитель портфеля проектов'), ('pm', 'Руководитель проекта '),
                                            ('rm', 'Ресурсный менеджер')], max_length=50, verbose_name='роль'),
        ),
        migrations.AlterField(
            model_name='organizationprojectuserrole',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    related_name='organizations_projects_roles', to=settings.AUTH_USER_MODEL,
                                    verbose_name='пользователь'),
        ),
        migrations.RemoveField(
            model_name='organizationproject',
            name='recruiters',
        ),
        migrations.RemoveField(
            model_name='organizationproject',
            name='resource_managers',
        ),
    ]
