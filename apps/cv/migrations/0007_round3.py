from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0008_round3_4'),
        ('cv', '0006_cveducation_diploma_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='cvtimeslot',
            name='request_requirement_link',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                    related_name='time_slots', to='main.requestrequirementcv',
                                    verbose_name='linked to a request'),
        ),
        migrations.RunSQL('TRUNCATE cv_cvtimeslot CASCADE')
    ]
