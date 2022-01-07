import os

TEST_USERS_CREATE = os.environ.get('TEST_USERS_CREATE') or False

password = 'Not11B2B;Pass'

TEST_USERS = [
    {
        'email': 'admin@b2b-cloud.club',
        'password': password,
        'first_name': 'Superuser',
        'last_name': 'Superuser',
        'is_staff': True,
        'is_superuser': True,
    },
    {
        'email': 'user@b2b-cloud.club',
        'password': password,
        'first_name': 'User',
        'last_name': 'User',
    },
]
