import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('dictionary', '0002_round1_imports'),
        ('main', '0009_round3_5'),
    ]

    operations = [
        migrations.AddField(
            model_name='requestrequirementcv',
            name='rating',
            field=models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1),
                                                                         django.core.validators.MaxValueValidator(5)],
                                      verbose_name='rating'),
        ),

        migrations.RemoveField(
            model_name='requestrequirementcv',
            name='organization_project_card_items',
        ),
        migrations.AddField(
            model_name='requestrequirementcv',
            name='attributes',
            field=models.JSONField(default=dict,
                                   help_text='avoid editing, '
                                             'if you do not know the purpose of this field',
                                   verbose_name='additional attributes'),
        ),
        migrations.AlterField(
            model_name='organizationprojectcarditem',
            name='positions',
            field=models.ManyToManyField(blank=True, related_name='_main_organizationprojectcarditem_positions_+',
                                         to='dictionary.Position', verbose_name='positions'),
        ),
        migrations.AlterField(
            model_name='organizationprojectcarditemtemplate',
            name='positions',
            field=models.ManyToManyField(blank=True,
                                         related_name='_main_organizationprojectcarditemtemplate_positions_+',
                                         to='dictionary.Position', verbose_name='positions'),
        ),
    ]
