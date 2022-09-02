import logging

from typing import List

from django.apps import AppConfig
from django.conf import settings
from django.contrib.auth import get_user_model

from acc.apps import AccConfig

logger = logging.getLogger(__name__)

User = get_user_model()


def test_users_signal_receiver(sender: AppConfig, **kwargs) -> None:
    if (
            not getattr(settings, 'TEST_USERS_CREATE', False)
            or not getattr(settings, 'TEST_USERS', None)
            or not isinstance(sender, AccConfig)
    ):
        return
    test_users_create()


def test_users_create() -> List[User]:
    users = []
    for row in settings.TEST_USERS:
        users.append(test_user_get_or_create(**row))
    return users


def test_user_get_or_create(**kwargs) -> User:
    created = False
    user = User.objects.filter(email=kwargs['email']).first()
    if not user:
        created = True
        user = User(**kwargs)
    user.set_password(kwargs['password'])
    user.save()
    logger.info(f'<< {user} >> {"created" if created else "already exists"}')
    return user
