from django.db.models.signals import post_migrate

from acc.test_users import test_users_signal_receiver


def setup():
    post_migrate.connect(test_users_signal_receiver, weak=False)
