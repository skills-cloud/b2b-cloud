from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('cv', '0007_round3'),
    ]

    operations = [
        migrations.AddField(
            model_name='cvtimeslot',
            name='kind',
            field=models.CharField(choices=[('manual', 'Manual'), ('request_requirement', 'Request Requirement')],
                                   default='manual', max_length=50, verbose_name='тип слота'),
        ),
        migrations.AddField(
            model_name='cvtimeslot',
            name='is_free',
            field=models.BooleanField(default=False, verbose_name='свободен?'),
        ),
    ]
