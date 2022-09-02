from collections import namedtuple

__all__ = ['EMAIL_TEMPLATE']

EmailTemplate = namedtuple('EmailTemplate', ['subject', 'body_text', 'body_html'])

hello = '<p>Greetings{% if user.get_email_title %}, {{ user.get_email_title }}{% endif %}!</p>'

EMAIL_TEMPLATE = {
    'test': EmailTemplate(
        'TEST TEST TEST',
        'TEST TEST TEST\nTEST TEST TEST',
        '<h1>TEST TEST TEST</h1><h2>TEST TEST TEST</h2><h3>TEST TEST TEST</h3>',
    ),
    'password_reset': EmailTemplate(
        'Password recovery {{ domain }}',
        '',
        'To continue password recovery <a href="{{ confirm_url }}">use this link</a>',
    ),
    'registration_invite': EmailTemplate(
        'Welcome {{ domain }}!',
        '',
        '''
<h3>Your credentials</h3>
<p>
Link to enter your personal account <b>{{ base_url }}</b><br>
E-mail / login: <b>{{ user.email }}</b><br>
Password: <b>{{ password }}</b>
</p>
        ''',
    ),
}
