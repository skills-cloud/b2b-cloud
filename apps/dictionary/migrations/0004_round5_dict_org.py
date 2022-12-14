# Generated by Django 3.2.11 on 2022-01-19 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0003_name_indexes'),
    ]

    operations = [
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='создано')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='обновлено')),
                ('name', models.CharField(db_index=True, max_length=500, verbose_name='название')),
                ('is_verified', models.BooleanField(default=False, verbose_name='подтверждено')),
                ('description', models.TextField(blank=True, null=True, verbose_name='описание')),
                ('sorting', models.IntegerField(default=0, verbose_name='сортировка')),
                ('old_id', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'компания',
                'verbose_name_plural': 'компании',
                'ordering': ['sorting', 'name'],
            },
        ),
    ]
