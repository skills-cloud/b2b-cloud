from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ('cv', '0006_cveducation_diploma_number'),
        ('main', '0007_round3_2_timesheet'),
    ]

    operations = [
        migrations.DeleteModel(
            name='TimeSheetRow',
        ),
        migrations.CreateModel(
            name='TimeSheetRow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='created')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('date_from',
                 models.DateField(db_index=True, default=django.utils.timezone.now, verbose_name='date from')),
                ('date_to', models.DateField(blank=True, null=True, verbose_name='date to')),
                ('task_name', models.CharField(max_length=1000, verbose_name='task name')),
                ('task_description', models.TextField(blank=True, null=True, verbose_name='task description')),
                ('work_time', models.FloatField(verbose_name='time spent')),
                ('cv', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='time_sheet_rows',
                                         to='cv.cv', verbose_name='CV')),
                ('request',
                 models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='time_sheet_rows',
                                   to='main.request', verbose_name='request')),
            ],
            options={
                'verbose_name': 'timesheet row',
                'verbose_name_plural': 'timesheet rows',
                'ordering': ['-date_from'],
                'index_together': {('request', 'date_from'), ('request', 'task_name')},
            },
        ),
        migrations.RemoveField(
            model_name='requestrequirement',
            name='cv_list',
        ),
        migrations.CreateModel(
            name='RequestRequirementCv',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='created')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('status',
                 models.CharField(choices=[('candidate', 'Candidate'), ('canceled', 'Canceled'), ('worker', 'Worker')],
                                  default='candidate', max_length=50, verbose_name='status')),
                ('cv', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                         related_name='requests_requirements_links', to='cv.cv',
                                         verbose_name='CV')),
                ('request_requirement',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cv_links',
                                   to='main.requestrequirement', verbose_name='request requirement')),
            ],
            options={
                'verbose_name': 'request requirement resume',
                'verbose_name_plural': 'request requirement resumes',
                'ordering': ['-id'],
                'unique_together': {('request_requirement', 'cv')},
            },
        ),

        migrations.AddField(
            model_name='requestrequirementcv',
            name='date_from',
            field=models.DateField(blank=True, null=True, verbose_name='project participation from'),
        ),
        migrations.AddField(
            model_name='requestrequirementcv',
            name='date_to',
            field=models.DateField(blank=True, null=True, verbose_name='project participation to'),
        ),
        migrations.AddField(
            model_name='requestrequirementcv',
            name='organization_project_card_items',
            field=models.ManyToManyField(blank=True, to='main.OrganizationProjectCardItem',
                                         verbose_name='organization project card'),
        ),
    ]
