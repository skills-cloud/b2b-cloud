#!/bin/sh

set -e

./docker/entry-point/${DJANGO_ENV:-prod}/$1.sh