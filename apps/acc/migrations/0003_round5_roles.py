# Generated by Django 3.2.11 on 2022-01-13 11:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('acc', '0002_round5'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usersystemrole',
            name='role',
            field=models.CharField(choices=[('admin', 'Администратор'), ('pfm', 'Руководитель портфеля проектов'), ('pm', 'Руководитель проекта'), ('rm', 'Ресурсный менеджер')], max_length=50),
        ),
    ]
