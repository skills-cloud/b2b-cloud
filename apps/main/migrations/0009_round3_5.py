from django.db import migrations, models
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):
    dependencies = [
        ('dictionary', '0002_round1_imports'),
        ('main', '0008_round3_4'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='organizationprojectcarditem',
            options={'verbose_name': 'organization project card',
                     'verbose_name_plural': 'organization project cards'},
        ),
        migrations.CreateModel(
            name='OrganizationProjectCardItemTemplate',
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
                ('parent',
                 mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                            related_name='children', to='main.organizationprojectcarditemtemplate',
                                            verbose_name='parent card')),
            ],
            options={
                'verbose_name': 'organization project card template',
                'verbose_name_plural': 'organization project card templates',
            },
        ),
        migrations.AddField(
            model_name='organizationprojectcarditem',
            name='positions',
            field=models.ManyToManyField(related_name='_main_organizationprojectcarditem_positions_+',
                                         to='dictionary.Position', verbose_name='positions'),
        ),
        migrations.AddField(
            model_name='organizationprojectcarditemtemplate',
            name='positions',
            field=models.ManyToManyField(related_name='_main_organizationprojectcarditemtemplate_positions_+',
                                         to='dictionary.Position', verbose_name='positions'),
        ),
    ]
