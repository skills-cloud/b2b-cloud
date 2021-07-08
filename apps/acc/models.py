import os
import hashlib
import datetime
import random
from typing import Optional

from django.db import models
from django.contrib.auth.models import AbstractUser, Group as GroupBase
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


def upload_to(instance, filename):
    filename = filename.lower()
    hd = hashlib.sha256((str(datetime.datetime.now()) + str(random.random())).encode()).hexdigest()
    return os.path.join(instance.UPLOAD_TO, hd[:2], hd[2:4], '%s%s' % (hd, os.path.splitext(filename)[1]))


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


class Group(GroupBase):
    class Meta:
        proxy = True
