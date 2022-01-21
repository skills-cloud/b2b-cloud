import random

import datetime

import hashlib

from typing import List, Dict

import reversion
from django.db import models
from django.contrib.auth.models import AbstractUser, Group as GroupBase
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _

from project.contrib.db.upload_to import upload_to
from project.msg import get_email_message_by_template


class Role(models.TextChoices):
    # EMPLOYEE = 'employee', _('Специалист')
    ADMIN = 'admin', _('Администратор')
    PFM = 'pfm', _('Руководитель портфеля проектов')
    PM = 'pm', _('Руководитель проекта')
    RM = 'rm', _('Ресурсный менеджер')


class UserQuerySet(models.QuerySet):
    def filter_by_user(self, user: 'User'):
        return self


class UserManager(models.Manager.from_queryset(UserQuerySet), BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)

    @classmethod
    def get_queryset_prefetch_related_roles(cls) -> List[str]:
        return [
            'organizations_contractors_roles',
            'organizations_contractors_roles__organization_contractor',
        ]


class Gender(models.TextChoices):
    MALE = 'M', _('Мужской')
    FEMALE = 'F', _('Женский')
    OTHER = '-', _('Другой')


@reversion.register()
class User(AbstractUser):
    backend = 'django.contrib.auth.backends.ModelBackend'

    UPLOAD_TO = 'user'
    username = None

    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(null=True, blank=True, max_length=150, verbose_name=_('имя'))
    middle_name = models.CharField(null=True, blank=True, max_length=150, verbose_name=_('отчество'))
    last_name = models.CharField(null=True, blank=True, max_length=150, verbose_name=_('фамилия'))

    photo = models.ImageField(null=True, blank=True, upload_to=upload_to)

    gender = models.CharField(max_length=1, null=True, blank=True, choices=Gender.choices, verbose_name=_('пол'))
    birth_date = models.DateField(null=True, blank=True, verbose_name=_('дата рождения'))
    phone = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('телефон'))

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f'{self.first_name} {self.last_name} < {self.email} >'

    @property
    def roles(self) -> List[Role]:
        return [role.role for role in self.system_roles.all()]

    def generate_password(self) -> str:
        password = hashlib.md5(str(datetime.datetime.now()).encode()).hexdigest()[:random.randint(8, 12)]
        self.set_password(password)
        self.save()
        return password

    def generate_password_and_send_invite(self):
        password = self.generate_password()
        msg = get_email_message_by_template('registration_invite', user=self, password=password)
        msg.to = [self.email]
        msg.send()


class UserSystemRole(models.Model):
    user = models.ForeignKey('acc.User', related_name='system_roles', on_delete=models.CASCADE)
    role = models.CharField(max_length=50, choices=Role.choices)

    class Meta:
        unique_together = [
            ['user', 'role']
        ]
        verbose_name = _('системная роль')
        verbose_name_plural = _('системные роли')


class Group(GroupBase):
    class Meta:
        proxy = True
