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
                'verbose_name': 'contractor organization',
                'verbose_name_plural': 'contractor organizations',
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
                'verbose_name': 'customer organization',
                'verbose_name_plural': 'customer organizations',
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
            field=models.BooleanField(default=False, verbose_name='contractor?'),
        ),
        migrations.AlterField(
            model_name='funpointtype',
            name='organization',
            field=models.ForeignKey(blank=True, help_text='general type if this field is left empty', null=True,
                                    on_delete=django.db.models.deletion.CASCADE, related_name='fun_points_types',
                                    to='main.organizationcustomer', verbose_name='customer'),
        ),
        migrations.AlterField(
            model_name='organizationproject',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='projects',
                                    to='main.organizationcustomer', verbose_name='customer'),
        ),
        migrations.AddField(
            model_name='organization',
            name='contractor',
            field=models.ForeignKey(blank=True, help_text='value applies only to customer organizations', null=True,
                                    on_delete=django.db.models.deletion.SET_NULL, to='main.organizationcontractor',
                                    verbose_name='contractor for this customer'),
        ),
        migrations.AlterField(
            model_name='organization',
            name='is_contractor',
            field=models.BooleanField(default=False, verbose_name='is a contractor?'),
        ),
        migrations.AlterField(
            model_name='organization',
            name='is_customer',
            field=models.BooleanField(default=False, verbose_name='is a customer?'),
        ),
        migrations.CreateModel(
            name='OrganizationContractorUserRole',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('employee', 'Employee'), ('admin', 'Administrator'),
                                                   ('pfm', 'Project portfolio manager'),
                                                   ('pm', 'Project manager '), ('rm', 'Resource manager')],
                                          max_length=50)),
                ('organization_contractor',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='users_roles',
                                   to='main.organizationcontractor', verbose_name='contractor organization')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                           related_name='organizations_contractors_roles',
                                           to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'user role',
                'verbose_name_plural': 'user roles',
                'unique_together': {('organization_contractor', 'user', 'role')},
            },
        ),
        migrations.CreateModel(
            name='OrganizationProjectUserRole',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('employee', 'Employee'), ('admin', 'Administrator'),
                                                   ('pfm', 'Project portfolio manager'),
                                                   ('pm', 'Project manager '), ('rm', 'Resource manager')],
                                          max_length=50)),
                ('organization_project',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='users_roles',
                                   to='main.organizationproject', verbose_name='project')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                           related_name='organizations_projects_roles', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'user role',
                'verbose_name_plural': 'user roles',
                'unique_together': {('organization_project', 'user', 'role')},
            },
        ),
        migrations.AlterField(
            model_name='organizationcontractoruserrole',
            name='role',
            field=models.CharField(choices=[('employee', 'Employee'), ('admin', 'Administrator'),
                                            ('pfm', 'Project portfolio manager'), ('pm', 'Project manager '),
                                            ('rm', 'Resource manager')], max_length=50, verbose_name='role'),
        ),
        migrations.AlterField(
            model_name='organizationcontractoruserrole',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    related_name='organizations_contractors_roles', to=settings.AUTH_USER_MODEL,
                                    verbose_name='user'),
        ),
        migrations.AlterField(
            model_name='organizationprojectuserrole',
            name='role',
            field=models.CharField(choices=[('employee', 'Employee'), ('admin', 'Administrator'),
                                            ('pfm', 'Project portfolio manager'), ('pm', 'Project manager '),
                                            ('rm', 'Resource manager')], max_length=50, verbose_name='role'),
        ),
        migrations.AlterField(
            model_name='organizationprojectuserrole',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    related_name='organizations_projects_roles', to=settings.AUTH_USER_MODEL,
                                    verbose_name='user'),
        ),
        migrations.RemoveField(
            model_name='organizationproject',
            name='recruiters',
        ),
        migrations.RemoveField(
            model_name='organizationproject',
            name='resource_managers',
        ),
        migrations.AlterField(
            model_name='organizationcontractoruserrole',
            name='role',
            field=models.CharField(choices=[('employee', 'Employee'), ('admin', 'Administrator'),
                                            ('pfm', 'Project portfolio manager'), ('pm', 'Project manager'),
                                            ('rm', 'Resource manager')], max_length=50, verbose_name='role'),
        ),
        migrations.AlterField(
            model_name='organizationprojectuserrole',
            name='role',
            field=models.CharField(choices=[('employee', 'Employee'), ('admin', 'Administrator'),
                                            ('pfm', 'Project portfolio manager'), ('pm', 'Project manager'),
                                            ('rm', 'Resource manager')], max_length=50, verbose_name='role'),
        ),

        migrations.RenameField(
            model_name='organizationproject',
            old_name='organization',
            new_name='organization_customer',
        ),
        migrations.RenameField(
            model_name='funpointtype',
            old_name='organization',
            new_name='organization_customer',
        ),
        migrations.AlterUniqueTogether(
            name='funpointtype',
            unique_together={('organization_customer', 'name')},
        ),
    ]
