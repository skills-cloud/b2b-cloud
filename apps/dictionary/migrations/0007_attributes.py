from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0006_round5_dict_org'),
    ]

    operations = [
        migrations.AddField(
            model_name='citizenship',
            name='attributes',
            field=models.JSONField(default=dict, editable=False, help_text='если вы не до конца понимаете назначение этого поля, вам лучше избежать редактирования', verbose_name='доп. атрибуты'),
        ),
        migrations.AddField(
            model_name='city',
            name='attributes',
            field=models.JSONField(default=dict, editable=False, help_text='если вы не до конца понимаете назначение этого поля, вам лучше избежать редактирования', verbose_name='доп. атрибуты'),
        ),
        migrations.AddField(
            model_name='competence',
            name='attributes',
            field=models.JSONField(default=dict, editable=False, help_text='если вы не до конца понимаете назначение этого поля, вам лучше избежать редактирования', verbose_name='доп. атрибуты'),
        ),
        migrations.AddField(
            model_name='contacttype',
            name='attributes',
            field=models.JSONField(default=dict, editable=False, help_text='если вы не до конца понимаете назначение этого поля, вам лучше избежать редактирования', verbose_name='доп. атрибуты'),
        ),
        migrations.AddField(
            model_name='country',
            name='attributes',
            field=models.JSONField(default=dict, editable=False, help_text='если вы не до конца понимаете назначение этого поля, вам лучше избежать редактирования', verbose_name='доп. атрибуты'),
        ),
        migrations.AddField(
            model_name='educationgraduate',
            name='attributes',
            field=models.JSONField(default=dict, editable=False, help_text='если вы не до конца понимаете назначение этого поля, вам лучше избежать редактирования', verbose_name='доп. атрибуты'),
        ),
        migrations.AddField(
            model_name='educationplace',
            name='attributes',
            field=models.JSONField(default=dict, editable=False, help_text='если вы не до конца понимаете назначение этого поля, вам лучше избежать редактирования', verbose_name='доп. атрибуты'),
        ),
        migrations.AddField(
            model_name='educationspecialty',
            name='attributes',
            field=models.JSONField(default=dict, editable=False, help_text='если вы не до конца понимаете назначение этого поля, вам лучше избежать редактирования', verbose_name='доп. атрибуты'),
        ),
        migrations.AddField(
            model_name='industrysector',
            name='attributes',
            field=models.JSONField(default=dict, editable=False, help_text='если вы не до конца понимаете назначение этого поля, вам лучше избежать редактирования', verbose_name='доп. атрибуты'),
        ),
        migrations.AddField(
            model_name='organization',
            name='attributes',
            field=models.JSONField(default=dict, editable=False, help_text='если вы не до конца понимаете назначение этого поля, вам лучше избежать редактирования', verbose_name='доп. атрибуты'),
        ),
        migrations.AddField(
            model_name='physicallimitation',
            name='attributes',
            field=models.JSONField(default=dict, editable=False, help_text='если вы не до конца понимаете назначение этого поля, вам лучше избежать редактирования', verbose_name='доп. атрибуты'),
        ),
        migrations.AddField(
            model_name='position',
            name='attributes',
            field=models.JSONField(default=dict, editable=False, help_text='если вы не до конца понимаете назначение этого поля, вам лучше избежать редактирования', verbose_name='доп. атрибуты'),
        ),
        migrations.AddField(
            model_name='typeofemployment',
            name='attributes',
            field=models.JSONField(default=dict, editable=False, help_text='если вы не до конца понимаете назначение этого поля, вам лучше избежать редактирования', verbose_name='доп. атрибуты'),
        ),
    ]
