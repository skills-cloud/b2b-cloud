from django.conf import settings
from django.db import migrations, models
from django.db import migrations, models
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dictionary', '0002_round1_imports'),
        ('main', '0005_round2_3'),
    ]

    operations = [
        migrations.AddField(
            model_name='organizationproject',
            name='date_from',
            field=models.DateField(blank=True, null=True, verbose_name='date from'),
        ),
        migrations.AddField(
            model_name='organizationproject',
            name='date_to',
            field=models.DateField(blank=True, null=True, verbose_name='date to'),
        ),
        migrations.AddField(
            model_name='organizationproject',
            name='industry_sector',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT,
                                    related_name='organizations_projects', to='dictionary.industrysector',
                                    verbose_name='industry'),
        ),
        migrations.AddField(
            model_name='organizationproject',
            name='manager',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT,
                                    related_name='organizations_projects_as_manager', to=settings.AUTH_USER_MODEL,
                                    verbose_name='project manager'),
        ),
        migrations.AddField(
            model_name='organizationproject',
            name='recruiters',
            field=models.ManyToManyField(related_name='organizations_projects_as_recruiter',
                                         to=settings.AUTH_USER_MODEL, verbose_name='recruiters'),
        ),
        migrations.AddField(
            model_name='organizationproject',
            name='resource_managers',
            field=models.ManyToManyField(related_name='organizations_projects_as_resource_manager',
                                         to=settings.AUTH_USER_MODEL, verbose_name='resource managers'),
        ),
        migrations.AddField(
            model_name='request',
            name='manager',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT,
                                    related_name='requests_as_manager', to=settings.AUTH_USER_MODEL,
                                    verbose_name='project manager'),
        ),
        migrations.AddField(
            model_name='request',
            name='organization_project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT,
                                    related_name='requests', to='main.organizationproject',
                                    verbose_name='customer request'),
        ),
        migrations.AlterField(
            model_name='request',
            name='project',
            field=models.ForeignKey(blank=True,
                                    help_text='Not used at this moment.<br>Link to '
                                              'customer project',
                                    null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='requests',
                                    to='main.project', verbose_name='inner project'),
        ),

        migrations.RemoveField(
            model_name='request',
            name='customer',
        ),
        migrations.AlterField(
            model_name='request',
            name='organization_project',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.RESTRICT, related_name='requests',
                                    to='main.organizationproject', verbose_name='customer project'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='organizationproject',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='projects',
                                    to='main.organization', verbose_name='organization'),
        ),
        migrations.CreateModel(
            name='OrganizationProjectCardItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='created')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('name', models.CharField(max_length=500, verbose_name='name')),
                ('description', models.TextField(blank=True, null=True, verbose_name='description')),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('mptt_level', models.PositiveIntegerField(editable=False)),
                ('organization_project',
                 models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                   related_name='cards_items', to='main.organizationproject',
                                   verbose_name='organization project')),
                ('parent',
                 mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                            related_name='children', to='main.organizationprojectcarditem',
                                            verbose_name='parent')),
            ],
            options={
                'verbose_name': 'organization project card',
                'verbose_name_plural': 'organization project cards'
            },
        ),
        migrations.AlterField(
            model_name='organizationprojectcarditem',
            name='organization_project',
            field=models.ForeignKey(blank=True, help_text='set only for the root card', null=True,
                                    on_delete=django.db.models.deletion.CASCADE, related_name='cards_items',
                                    to='main.organizationproject', verbose_name='organization project'),
        ),
        migrations.AlterField(
            model_name='organizationprojectcarditem',
            name='parent',
            field=mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                             related_name='children', to='main.organizationprojectcarditem',
                                             verbose_name='parent card'),
        ),
    ]
