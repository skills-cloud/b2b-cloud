from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0007_round3_3'),
    ]

    operations = [
        migrations.AddField(
            model_name='requestrequirement',
            name='date_from',
            field=models.DateField(blank=True, null=True, verbose_name='date from'),
        ),
        migrations.AddField(
            model_name='requestrequirement',
            name='date_to',
            field=models.DateField(blank=True, null=True, verbose_name='date to'),
        ),
        migrations.AlterField(
            model_name='timesheetrow',
            name='request',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='time_sheet_rows',
                                    to='main.request', verbose_name='request'),
        ),
        migrations.AlterField(
            model_name='requestrequirementcv',
            name='status',
            field=models.CharField(
                choices=[('pre-candidate', 'Pre Candidate'), ('candidate', 'Candidate'), ('canceled', 'Canceled'),
                         ('worker', 'Worker')], default='candidate', max_length=50, verbose_name='status'),
        ),
    ]
