from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('cv', '0008_round3_2'),
    ]

    operations = [
        migrations.CreateModel(
            name='CvInfo',
            fields=[
                ('cv', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True,
                                            related_name='info', serialize=False, to='cv.cv')),
                ('rating', models.IntegerField(null=True)),
            ],
            options={
                'db_table': 'v_cv_info',
                'managed': False,
            },
        ),
    ]
