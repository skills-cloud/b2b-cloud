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
            field=models.DateField(blank=True, null=True, verbose_name='дата с'),
        ),
        migrations.AddField(
            model_name='organizationproject',
            name='date_to',
            field=models.DateField(blank=True, null=True, verbose_name='дата по'),
        ),
        migrations.AddField(
            model_name='organizationproject',
            name='industry_sector',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT,
                                    related_name='organizations_projects', to='dictionary.industrysector',
                                    verbose_name='отрасль'),
        ),
        migrations.AddField(
            model_name='organizationproject',
            name='manager',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT,
                                    related_name='organizations_projects_as_manager', to=settings.AUTH_USER_MODEL,
                                    verbose_name='руководитель проекта'),
        ),
        migrations.AddField(
            model_name='organizationproject',
            name='recruiters',
            field=models.ManyToManyField(related_name='organizations_projects_as_recruiter',
                                         to=settings.AUTH_USER_MODEL, verbose_name='рекрутеры'),
        ),
        migrations.AddField(
            model_name='organizationproject',
            name='resource_managers',
            field=models.ManyToManyField(related_name='organizations_projects_as_resource_manager',
                                         to=settings.AUTH_USER_MODEL, verbose_name='ресурсные менеджеры'),
        ),
        migrations.AddField(
            model_name='request',
            name='manager',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT,
                                    related_name='requests_as_manager', to=settings.AUTH_USER_MODEL,
                                    verbose_name='руководитель проекта'),
        ),
        migrations.AddField(
            model_name='request',
            name='organization_project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT,
                                    related_name='requests', to='main.organizationproject',
                                    verbose_name='проект заказчика'),
        ),
        migrations.AlterField(
            model_name='request',
            name='project',
            field=models.ForeignKey(blank=True,
                                    help_text='На текущий момент не используется.<br>Надо задавать связку с '
                                              'проектом заказчика',
                                    null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='requests',
                                    to='main.project', verbose_name='внутренний проект'),
        ),

        migrations.RemoveField(
            model_name='request',
            name='customer',
        ),
        migrations.AlterField(
            model_name='request',
            name='organization_project',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.RESTRICT, related_name='requests',
                                    to='main.organizationproject', verbose_name='проект заказчика'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='organizationproject',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='projects',
                                    to='main.organization', verbose_name='организация'),
        ),
        migrations.CreateModel(
            name='OrganizationProjectCardItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='создано')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='обновлено')),
                ('name', models.CharField(max_length=500, verbose_name='название')),
                ('description', models.TextField(blank=True, null=True, verbose_name='описание')),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('mptt_level', models.PositiveIntegerField(editable=False)),
                ('organization_project',
                 models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                   related_name='cards_items', to='main.organizationproject',
                                   verbose_name='проект организации')),
                ('parent',
                 mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                            related_name='children', to='main.organizationprojectcarditem',
                                            verbose_name='родитель')),
            ],
            options={
                'verbose_name': 'карточка проект организации',
                'verbose_name_plural': 'карточки проектов организаций'
            },
        ),
        migrations.AlterField(
            model_name='organizationprojectcarditem',
            name='organization_project',
            field=models.ForeignKey(blank=True, help_text='необходимо задавать только для корневой карточки', null=True,
                                    on_delete=django.db.models.deletion.CASCADE, related_name='cards_items',
                                    to='main.organizationproject', verbose_name='проект организации'),
        ),
        migrations.AlterField(
            model_name='organizationprojectcarditem',
            name='parent',
            field=mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                             related_name='children', to='main.organizationprojectcarditem',
                                             verbose_name='родительская карточка'),
        ),
    ]
