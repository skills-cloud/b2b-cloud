#!/bin/sh

set -e

./manage.py cache_invalidate_all
./manage.py migrate --fake-initial --noinput || exit 1

uwsgi --harakiri=60 --master --lazy-apps -p ${UWSGI_WORKERS:-8} --max-requests 100000 --disable-logging --http 0.0.0.0:8000 -w project.wsgi
