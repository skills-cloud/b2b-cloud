from django.core.management.base import BaseCommand

from acc.models import User
from project.msg import get_email_message_by_template


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('email', nargs='+')

    def handle(self, *args, **options):
        for email in options['email']:
            user = User.objects.filter(email=email).first()
            msg = get_email_message_by_template('test', user=user)
            msg.to = [email]
            msg.send()
