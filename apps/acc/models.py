from typing import List

from django.db import models
from django.contrib.auth.models import AbstractUser, Group as GroupBase
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _

from project.contrib.db.upload_to import upload_to


class Role(models.TextChoices):
    EMPLOYEE = 'employee', _('Специалист')
    ADMIN = 'admin', _('Администратор')
    PFM = 'pfm', _('Руководитель портфеля проектов')
    PM = 'pm', _('Руководитель проекта ')
    RM = 'rm', _('Ресурсный менеджер')


class CustomUserManager(BaseUserManager):
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


class User(AbstractUser):
    backend = 'django.contrib.auth.backends.ModelBackend'

    UPLOAD_TO = 'user'
    username = None
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=150)
    last_name = models.CharField(_('last name'), max_length=150)

    photo = models.ImageField(null=True, blank=True, upload_to=upload_to)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return f'{self.first_name} {self.last_name} < {self.email} >'

    @property
    def roles(self) -> List[Role]:
        return [role.role for role in self.system_roles.all()]


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
