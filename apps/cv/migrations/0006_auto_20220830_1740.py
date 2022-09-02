# Generated by Django 3.2.5 on 2022-08-30 14:40

import cv.models_upload_to
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0003_auto_20220830_1740'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0004_round2_2'),
        ('cv', '0005_round2_2_2'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cv',
            options={'ordering': ['-id'], 'verbose_name': 'анкета', 'verbose_name_plural': 'анкеты'},
        ),
        migrations.AlterModelOptions(
            name='cvcareer',
            options={'ordering': ['-date_from', '-id'], 'verbose_name': 'карьера', 'verbose_name_plural': 'карьера'},
        ),
        migrations.AlterModelOptions(
            name='cvcareerfile',
            options={'ordering': ['-id'], 'verbose_name': 'файл карьеры', 'verbose_name_plural': 'файлы карьеры'},
        ),
        migrations.AlterModelOptions(
            name='cvcertificate',
            options={'ordering': ['-date', '-id'], 'verbose_name': 'сертификат', 'verbose_name_plural': 'сертификаты'},
        ),
        migrations.AlterModelOptions(
            name='cvcontact',
            options={'ordering': ['is_primary', '-id'], 'verbose_name': 'контактные данные', 'verbose_name_plural': 'контактные данные'},
        ),
        migrations.AlterModelOptions(
            name='cveducation',
            options={'ordering': ['-date_from', '-id'], 'verbose_name': 'образование', 'verbose_name_plural': 'образование'},
        ),
        migrations.AlterModelOptions(
            name='cvfile',
            options={'ordering': ['-id'], 'verbose_name': 'файл анкеты', 'verbose_name_plural': 'файлы анкеты'},
        ),
        migrations.AlterModelOptions(
            name='cvposition',
            options={'ordering': ['-id'], 'verbose_name': 'должность / роль', 'verbose_name_plural': 'должности / роли'},
        ),
        migrations.AlterModelOptions(
            name='cvpositioncompetence',
            options={'ordering': ['-year_started', 'id'], 'verbose_name': 'компетенция роли', 'verbose_name_plural': 'компетенции роли'},
        ),
        migrations.AlterModelOptions(
            name='cvpositionfile',
            options={'ordering': ['-id'], 'verbose_name': 'файл роли', 'verbose_name_plural': 'файлы роли'},
        ),
        migrations.AlterModelOptions(
            name='cvproject',
            options={'ordering': ['-date_from', '-id'], 'verbose_name': 'проект', 'verbose_name_plural': 'проекты'},
        ),
        migrations.AlterModelOptions(
            name='cvtimeslot',
            options={'ordering': ['-date_from', '-id'], 'verbose_name': 'таймслот', 'verbose_name_plural': 'таймслоты'},
        ),
        migrations.AlterField(
            model_name='cv',
            name='about',
            field=models.TextField(blank=True, null=True, verbose_name='доп. информация'),
        ),
        migrations.AlterField(
            model_name='cv',
            name='birth_date',
            field=models.DateField(blank=True, null=True, verbose_name='дата рождения'),
        ),
        migrations.AlterField(
            model_name='cv',
            name='citizenship',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='dictionary.citizenship', verbose_name='гражданство'),
        ),
        migrations.AlterField(
            model_name='cv',
            name='city',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='dictionary.city', verbose_name='город'),
        ),
        migrations.AlterField(
            model_name='cv',
            name='country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='dictionary.country', verbose_name='страна'),
        ),
        migrations.AlterField(
            model_name='cv',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='создано'),
        ),
        migrations.AlterField(
            model_name='cv',
            name='days_to_contact',
            field=models.CharField(blank=True, choices=[('all', 'Все дни'), ('workdays', 'Будние дни'), ('weekends', 'Выходные дни')], max_length=50, null=True, verbose_name='дни для связи'),
        ),
        migrations.AlterField(
            model_name='cv',
            name='first_name',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='имя'),
        ),
        migrations.AlterField(
            model_name='cv',
            name='gender',
            field=models.CharField(blank=True, choices=[('M', 'Мужской'), ('F', 'Женский')], max_length=1, null=True, verbose_name='пол'),
        ),
        migrations.AlterField(
            model_name='cv',
            name='is_resource_owner',
            field=models.BooleanField(default=False, verbose_name='владелец ресурса'),
        ),
        migrations.AlterField(
            model_name='cv',
            name='is_verified',
            field=models.BooleanField(default=False, verbose_name='подтверждено'),
        ),
        migrations.AlterField(
            model_name='cv',
            name='last_name',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='фамилия'),
        ),
        migrations.AlterField(
            model_name='cv',
            name='linked',
            field=models.ManyToManyField(blank=True, related_name='_cv_cv_linked_+', to='cv.CV', verbose_name='связанные анкеты'),
        ),
        migrations.AlterField(
            model_name='cv',
            name='middle_name',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='отчество'),
        ),
        migrations.AlterField(
            model_name='cv',
            name='physical_limitations',
            field=models.ManyToManyField(blank=True, to='dictionary.PhysicalLimitation', verbose_name='физические особенности'),
        ),
        migrations.AlterField(
            model_name='cv',
            name='price',
            field=models.FloatField(blank=True, null=True, verbose_name='ставка'),
        ),
        migrations.AlterField(
            model_name='cv',
            name='time_to_contact_from',
            field=models.TimeField(blank=True, null=True, verbose_name='время для связи / с'),
        ),
        migrations.AlterField(
            model_name='cv',
            name='time_to_contact_to',
            field=models.TimeField(blank=True, null=True, verbose_name='время для связи / по'),
        ),
        migrations.AlterField(
            model_name='cv',
            name='types_of_employment',
            field=models.ManyToManyField(blank=True, to='dictionary.TypeOfEmployment', verbose_name='тип занятости'),
        ),
        migrations.AlterField(
            model_name='cv',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='обновлено'),
        ),
        migrations.AlterField(
            model_name='cv',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cv_list', to=settings.AUTH_USER_MODEL, verbose_name='пользователь'),
        ),
        migrations.AlterField(
            model_name='cvcareer',
            name='competencies',
            field=models.ManyToManyField(blank=True, to='dictionary.Competence', verbose_name='компетенции'),
        ),
        migrations.AlterField(
            model_name='cvcareer',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='создано'),
        ),
        migrations.AlterField(
            model_name='cvcareer',
            name='cv',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='career', to='cv.cv', verbose_name='анкета'),
        ),
        migrations.AlterField(
            model_name='cvcareer',
            name='date_from',
            field=models.DateField(blank=True, null=True, verbose_name='период с'),
        ),
        migrations.AlterField(
            model_name='cvcareer',
            name='date_to',
            field=models.DateField(blank=True, null=True, verbose_name='период по'),
        ),
        migrations.AlterField(
            model_name='cvcareer',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='описание'),
        ),
        migrations.AlterField(
            model_name='cvcareer',
            name='is_verified',
            field=models.BooleanField(default=False, verbose_name='подтверждено'),
        ),
        migrations.AlterField(
            model_name='cvcareer',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='main.organization', verbose_name='заказчик'),
        ),
        migrations.AlterField(
            model_name='cvcareer',
            name='position',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='dictionary.position', verbose_name='должность / роль'),
        ),
        migrations.AlterField(
            model_name='cvcareer',
            name='projects',
            field=models.ManyToManyField(blank=True, to='main.OrganizationProject', verbose_name='проекты'),
        ),
        migrations.AlterField(
            model_name='cvcareer',
            name='title',
            field=models.CharField(blank=True, max_length=2000, null=True, verbose_name='произвольное название'),
        ),
        migrations.AlterField(
            model_name='cvcareer',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='обновлено'),
        ),
        migrations.AlterField(
            model_name='cvcareerfile',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='создано'),
        ),
        migrations.AlterField(
            model_name='cvcareerfile',
            name='cv_career',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='cv.cvcareer', verbose_name='карьера'),
        ),
        migrations.AlterField(
            model_name='cvcareerfile',
            name='file',
            field=models.FileField(upload_to=cv.models_upload_to.cv_career_file_upload_to, verbose_name='файл'),
        ),
        migrations.AlterField(
            model_name='cvcareerfile',
            name='file_name',
            field=models.CharField(blank=True, max_length=1000, null=True, verbose_name='название файла'),
        ),
        migrations.AlterField(
            model_name='cvcareerfile',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='обновлено'),
        ),
        migrations.AlterField(
            model_name='cvcertificate',
            name='competencies',
            field=models.ManyToManyField(blank=True, to='dictionary.Competence', verbose_name='компетенции'),
        ),
        migrations.AlterField(
            model_name='cvcertificate',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='создано'),
        ),
        migrations.AlterField(
            model_name='cvcertificate',
            name='cv',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='certificates', to='cv.cv', verbose_name='анкета'),
        ),
        migrations.AlterField(
            model_name='cvcertificate',
            name='date',
            field=models.DateField(blank=True, null=True, verbose_name='выдан'),
        ),
        migrations.AlterField(
            model_name='cvcertificate',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='описание'),
        ),
        migrations.AlterField(
            model_name='cvcertificate',
            name='education_graduate',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='dictionary.educationgraduate', verbose_name='степень'),
        ),
        migrations.AlterField(
            model_name='cvcertificate',
            name='education_place',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='dictionary.educationplace', verbose_name='место обучения'),
        ),
        migrations.AlterField(
            model_name='cvcertificate',
            name='education_speciality',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='dictionary.educationspecialty', verbose_name='специальность'),
        ),
        migrations.AlterField(
            model_name='cvcertificate',
            name='is_verified',
            field=models.BooleanField(default=False, verbose_name='подтверждено'),
        ),
        migrations.AlterField(
            model_name='cvcertificate',
            name='name',
            field=models.CharField(blank=True, max_length=1000, null=True, verbose_name='наименование'),
        ),
        migrations.AlterField(
            model_name='cvcertificate',
            name='number',
            field=models.CharField(blank=True, max_length=1000, null=True, verbose_name='номер'),
        ),
        migrations.AlterField(
            model_name='cvcertificate',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='обновлено'),
        ),
        migrations.AlterField(
            model_name='cvcontact',
            name='comment',
            field=models.TextField(blank=True, max_length=1000, null=True, verbose_name='комментарий'),
        ),
        migrations.AlterField(
            model_name='cvcontact',
            name='contact_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='dictionary.contacttype', verbose_name='тип'),
        ),
        migrations.AlterField(
            model_name='cvcontact',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='создано'),
        ),
        migrations.AlterField(
            model_name='cvcontact',
            name='cv',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contacts', to='cv.cv', verbose_name='анкета'),
        ),
        migrations.AlterField(
            model_name='cvcontact',
            name='is_primary',
            field=models.BooleanField(default=False, verbose_name='основной'),
        ),
        migrations.AlterField(
            model_name='cvcontact',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='обновлено'),
        ),
        migrations.AlterField(
            model_name='cvcontact',
            name='value',
            field=models.CharField(max_length=1000, verbose_name='значение'),
        ),
        migrations.AlterField(
            model_name='cveducation',
            name='competencies',
            field=models.ManyToManyField(blank=True, to='dictionary.Competence', verbose_name='компетенции'),
        ),
        migrations.AlterField(
            model_name='cveducation',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='создано'),
        ),
        migrations.AlterField(
            model_name='cveducation',
            name='cv',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='education', to='cv.cv', verbose_name='анкета'),
        ),
        migrations.AlterField(
            model_name='cveducation',
            name='date_from',
            field=models.DateField(blank=True, null=True, verbose_name='период с'),
        ),
        migrations.AlterField(
            model_name='cveducation',
            name='date_to',
            field=models.DateField(blank=True, null=True, verbose_name='период по'),
        ),
        migrations.AlterField(
            model_name='cveducation',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='описание'),
        ),
        migrations.AlterField(
            model_name='cveducation',
            name='education_graduate',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='dictionary.educationgraduate', verbose_name='степень'),
        ),
        migrations.AlterField(
            model_name='cveducation',
            name='education_place',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='dictionary.educationplace', verbose_name='место обучения'),
        ),
        migrations.AlterField(
            model_name='cveducation',
            name='education_speciality',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='dictionary.educationspecialty', verbose_name='специальность'),
        ),
        migrations.AlterField(
            model_name='cveducation',
            name='is_verified',
            field=models.BooleanField(default=False, verbose_name='подтверждено'),
        ),
        migrations.AlterField(
            model_name='cveducation',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='обновлено'),
        ),
        migrations.AlterField(
            model_name='cvfile',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='создано'),
        ),
        migrations.AlterField(
            model_name='cvfile',
            name='cv',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='cv.cv', verbose_name='анкета'),
        ),
        migrations.AlterField(
            model_name='cvfile',
            name='file',
            field=models.FileField(upload_to=cv.models_upload_to.cv_file_file_upload_to, verbose_name='файл'),
        ),
        migrations.AlterField(
            model_name='cvfile',
            name='file_name',
            field=models.CharField(blank=True, max_length=1000, null=True, verbose_name='название файла'),
        ),
        migrations.AlterField(
            model_name='cvfile',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='обновлено'),
        ),
        migrations.AlterField(
            model_name='cvposition',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='создано'),
        ),
        migrations.AlterField(
            model_name='cvposition',
            name='cv',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='positions', to='cv.cv', verbose_name='анкета'),
        ),
        migrations.AlterField(
            model_name='cvposition',
            name='position',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='dictionary.position', verbose_name='должность'),
        ),
        migrations.AlterField(
            model_name='cvposition',
            name='title',
            field=models.CharField(blank=True, max_length=2000, null=True, verbose_name='произвольное название'),
        ),
        migrations.AlterField(
            model_name='cvposition',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='обновлено'),
        ),
        migrations.AlterField(
            model_name='cvposition',
            name='year_started',
            field=models.IntegerField(blank=True, null=True, verbose_name='год начала практики'),
        ),
        migrations.AlterField(
            model_name='cvpositioncompetence',
            name='competence',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='dictionary.competence', verbose_name='компетенция'),
        ),
        migrations.AlterField(
            model_name='cvpositioncompetence',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='создано'),
        ),
        migrations.AlterField(
            model_name='cvpositioncompetence',
            name='cv_position',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='competencies', to='cv.cvposition', verbose_name='должность / роль'),
        ),
        migrations.AlterField(
            model_name='cvpositioncompetence',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='обновлено'),
        ),
        migrations.AlterField(
            model_name='cvpositioncompetence',
            name='year_started',
            field=models.IntegerField(blank=True, null=True, verbose_name='год начала практики'),
        ),
        migrations.AlterField(
            model_name='cvpositionfile',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='создано'),
        ),
        migrations.AlterField(
            model_name='cvpositionfile',
            name='cv_position',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='cv.cvposition', verbose_name='роль'),
        ),
        migrations.AlterField(
            model_name='cvpositionfile',
            name='file',
            field=models.FileField(upload_to=cv.models_upload_to.cv_position_file_upload_to, verbose_name='файл'),
        ),
        migrations.AlterField(
            model_name='cvpositionfile',
            name='file_name',
            field=models.CharField(blank=True, max_length=1000, null=True, verbose_name='название файла'),
        ),
        migrations.AlterField(
            model_name='cvpositionfile',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='обновлено'),
        ),
        migrations.AlterField(
            model_name='cvproject',
            name='competencies',
            field=models.ManyToManyField(blank=True, to='dictionary.Competence', verbose_name='компетенции'),
        ),
        migrations.AlterField(
            model_name='cvproject',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='создано'),
        ),
        migrations.AlterField(
            model_name='cvproject',
            name='cv',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='projects', to='cv.cv', verbose_name='анкета'),
        ),
        migrations.AlterField(
            model_name='cvproject',
            name='date_from',
            field=models.DateField(blank=True, null=True, verbose_name='период с'),
        ),
        migrations.AlterField(
            model_name='cvproject',
            name='date_to',
            field=models.DateField(blank=True, null=True, verbose_name='период по'),
        ),
        migrations.AlterField(
            model_name='cvproject',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='описание'),
        ),
        migrations.AlterField(
            model_name='cvproject',
            name='industry_sector',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='dictionary.industrysector', verbose_name='отрасль'),
        ),
        migrations.AlterField(
            model_name='cvproject',
            name='is_verified',
            field=models.BooleanField(default=False, verbose_name='подтверждено'),
        ),
        migrations.AlterField(
            model_name='cvproject',
            name='name',
            field=models.CharField(max_length=1000, verbose_name='название'),
        ),
        migrations.AlterField(
            model_name='cvproject',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='main.organization', verbose_name='заказчик'),
        ),
        migrations.AlterField(
            model_name='cvproject',
            name='position',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='dictionary.position', verbose_name='должность / роль'),
        ),
        migrations.AlterField(
            model_name='cvproject',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='обновлено'),
        ),
        migrations.AlterField(
            model_name='cvtimeslot',
            name='city',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='dictionary.city', verbose_name='город'),
        ),
        migrations.AlterField(
            model_name='cvtimeslot',
            name='country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='dictionary.country', verbose_name='страна'),
        ),
        migrations.AlterField(
            model_name='cvtimeslot',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='создано'),
        ),
        migrations.AlterField(
            model_name='cvtimeslot',
            name='cv',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='time_slots', to='cv.cv', verbose_name='анкета'),
        ),
        migrations.AlterField(
            model_name='cvtimeslot',
            name='date_from',
            field=models.DateField(blank=True, null=True, verbose_name='период с'),
        ),
        migrations.AlterField(
            model_name='cvtimeslot',
            name='date_to',
            field=models.DateField(blank=True, null=True, verbose_name='период по'),
        ),
        migrations.AlterField(
            model_name='cvtimeslot',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='описание'),
        ),
        migrations.AlterField(
            model_name='cvtimeslot',
            name='is_work_permit_required',
            field=models.BooleanField(default=False, verbose_name='требуется разрешение на работу'),
        ),
        migrations.AlterField(
            model_name='cvtimeslot',
            name='price',
            field=models.FloatField(blank=True, null=True, verbose_name='ставка'),
        ),
        migrations.AlterField(
            model_name='cvtimeslot',
            name='type_of_employment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='dictionary.typeofemployment', verbose_name='тип занятости'),
        ),
        migrations.AlterField(
            model_name='cvtimeslot',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='обновлено'),
        ),
    ]