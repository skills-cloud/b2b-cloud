# Generated by Django 3.2.5 on 2021-07-08 15:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('main', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dictionary', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CV',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='создано')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='обновлено')),
                ('first_name', models.CharField(blank=True, max_length=500, null=True, verbose_name='имя')),
                ('last_name', models.CharField(blank=True, max_length=500, null=True, verbose_name='фамилия')),
                ('middle_name', models.CharField(blank=True, max_length=500, null=True, verbose_name='отчество')),
                ('gender', models.CharField(blank=True, choices=[('М', 'Мужской'), ('F', 'Женский')], max_length=1, null=True, verbose_name='пол')),
                ('birth_date', models.DateField(blank=True, null=True, verbose_name='дата рождения')),
                ('citizenship', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='dictionary.citizenship', verbose_name='гражданство')),
                ('competence', models.ManyToManyField(to='dictionary.Competence', verbose_name='компетенции')),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='dictionary.country', verbose_name='страна')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cv_list', to=settings.AUTH_USER_MODEL, verbose_name='пользователь')),
            ],
            options={
                'verbose_name': 'анкета',
                'verbose_name_plural': 'анкеты',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='CvPosition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='создано')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='обновлено')),
                ('competencies', models.ManyToManyField(to='dictionary.Competence', verbose_name='компетенции')),
                ('cv', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='positions', to='cv.cv', verbose_name='анкета')),
                ('position', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='cv_positions', to='dictionary.position', verbose_name='должность')),
            ],
            options={
                'verbose_name': 'должность / роль',
                'verbose_name_plural': 'должности / роли',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='CvProject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='создано')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='обновлено')),
                ('date_from', models.DateField(blank=True, null=True, verbose_name='период с')),
                ('date_to', models.DateField(blank=True, null=True, verbose_name='период по')),
                ('description', models.TextField(blank=True, null=True, verbose_name='описание')),
                ('competencies', models.ManyToManyField(to='dictionary.Competence', verbose_name='компетенции')),
                ('cv', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='projects', to='cv.cv', verbose_name='анкета')),
                ('position', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='cv_projects', to='dictionary.position', verbose_name='должность / роль')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='cv_list', to='main.project', verbose_name='проект')),
            ],
            options={
                'verbose_name': 'проект',
                'verbose_name_plural': 'проекты',
                'ordering': ['-date_from'],
            },
        ),
        migrations.CreateModel(
            name='CvPositionFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='создано')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='обновлено')),
                ('file', models.FileField(upload_to='', verbose_name='файл')),
                ('cv_position', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='cv.cvposition', verbose_name='роль')),
            ],
            options={
                'verbose_name': 'файл роли',
                'verbose_name_plural': 'файлы роли',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='CvFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='создано')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='обновлено')),
                ('name', models.CharField(blank=True, max_length=500, null=True, verbose_name='название')),
                ('file', models.FileField(upload_to='', verbose_name='файл')),
                ('cv', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='cv.cv', verbose_name='анкета')),
            ],
            options={
                'verbose_name': 'файл',
                'verbose_name_plural': 'файлы',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='CvEducation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='создано')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='обновлено')),
                ('date_from', models.DateField(blank=True, null=True, verbose_name='период с')),
                ('date_to', models.DateField(blank=True, null=True, verbose_name='период по')),
                ('description', models.TextField(blank=True, null=True, verbose_name='описание')),
                ('competencies', models.ManyToManyField(to='dictionary.Competence', verbose_name='компетенции')),
                ('cv', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='education', to='cv.cv', verbose_name='анкета')),
                ('education_graduate', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='cv_education', to='dictionary.educationgraduate', verbose_name='степень')),
                ('education_place', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='cv_education', to='dictionary.educationplace', verbose_name='место обучения')),
                ('education_speciality', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='cv_education', to='dictionary.educationspecialty', verbose_name='специальность')),
            ],
            options={
                'verbose_name': 'образование',
                'verbose_name_plural': 'образование',
                'ordering': ['-date_from'],
            },
        ),
        migrations.CreateModel(
            name='CvContact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='создано')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='обновлено')),
                ('value', models.CharField(max_length=1000)),
                ('is_primary', models.BooleanField(default=False)),
                ('contact_type', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='cv_list', to='dictionary.contacttype', verbose_name='тип контактной информации')),
                ('cv', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contacts', to='cv.cv', verbose_name='анкета')),
            ],
            options={
                'verbose_name': 'контактные данные',
                'verbose_name_plural': 'контактные данные',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='CvCertificate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='создано')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='обновлено')),
                ('date', models.DateField(blank=True, null=True, verbose_name='выдан')),
                ('description', models.TextField(blank=True, null=True, verbose_name='описание')),
                ('competencies', models.ManyToManyField(to='dictionary.Competence', verbose_name='компетенции')),
                ('cv', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='certificates', to='cv.cv', verbose_name='анкета')),
                ('education_graduate', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='cv_certificate', to='dictionary.educationgraduate', verbose_name='степень')),
                ('education_speciality', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='cv_certificate', to='dictionary.educationspecialty', verbose_name='специальность')),
            ],
            options={
                'verbose_name': 'сертификат',
                'verbose_name_plural': 'сертификаты',
                'ordering': ['-date'],
            },
        ),
    ]
