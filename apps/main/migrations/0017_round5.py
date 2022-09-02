from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0016_round5'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organizationproject',
            name='organization_customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='projects',
                                    to='main.organizationcustomer', verbose_name='заказчик'),
        ),
    ]
