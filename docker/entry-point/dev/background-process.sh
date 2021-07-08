#!/bin/sh
watchmedo auto-restart --directory=/app --recursive --pattern='*.py' --debug-force-polling -- ./manage.py background_process