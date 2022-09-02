from collections import namedtuple

__all__ = ['EMAIL_TEMPLATE']

EmailTemplate = namedtuple('EmailTemplate', ['subject', 'body_text', 'body_html'])

hello = '<p>Здравствуйте{% if user.get_email_title %}, {{ user.get_email_title }}{% endif %}!</p>'

EMAIL_TEMPLATE = {
    'test': EmailTemplate(
        'TEST TEST TEST',
        'TEST TEST TEST\nTEST TEST TEST',
        '<h1>TEST TEST TEST</h1><h2>TEST TEST TEST</h2><h3>TEST TEST TEST</h3>',
    ),
    'password_reset': EmailTemplate(
        'Восстановление пароля на сайте {{ domain }}',
        '',
        'Для продолжения процедуры восстановления пароля <a href="{{ confirm_url }}">пройдите этой по ссылке</a>',
    ),
    'registration_invite': EmailTemplate(
        'Добро пожаловать в систему {{ domain }}!',
        '',
        '''
<h3>Ваши учетные данные</h3>
<p>
Ссылка для входа в личный кабинет <b>{{ base_url }}</b><br>
E-mail / логин: <b>{{ user.email }}</b><br>
Пароль: <b>{{ password }}</b>
</p>
        ''',
    ),
}
