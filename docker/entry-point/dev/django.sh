#!/bin/sh

set -e

./manage.py cache_invalidate_all
./manage.py migrate --fake-initial --noinput
./manage.py runserver 0:8000
#watchmedo auto-restart --directory=/app --recursive --pattern='*.py' --debug-force-polling -- uwsgi --harakiri=60 --master --lazy-apps -p ${UWSGI_WORKERS:-4} --max-requests 100000 --disable-logging --http 0.0.0.0:8000 -w project.wsgi
