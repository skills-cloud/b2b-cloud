# Generated by Django 3.2.10 on 2022-01-04 02:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('acc', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserSystemRole',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('employee', 'Специалист'), ('admin', 'Администратор'),
                                                   ('pfm', 'Руководитель портфеля проектов'),
                                                   ('pm', 'Руководитель проекта '), ('rm', 'Ресурсный менеджер')],
                                          max_length=50)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='system_roles',
                                           to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'системная роль',
                'verbose_name_plural': 'системные роли',
                'unique_together': {('user', 'role')},
            },
        ),

        migrations.AlterField(
            model_name='usersystemrole',
            name='role',
            field=models.CharField(choices=[('employee', 'Специалист'), ('admin', 'Администратор'),
                                            ('pfm', 'Руководитель портфеля проектов'), ('pm', 'Руководитель проекта'),
                                            ('rm', 'Ресурсный менеджер')], max_length=50),
        ),
    ]
