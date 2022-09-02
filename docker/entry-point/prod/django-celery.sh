#!/bin/sh

set -e

celery --app=project worker --concurrency=${CELERY_WORKERS:-4} --loglevel=info
