#!/bin/bash
# Entrypoint script for Django container: runs migrations and starts server
set -e

python manage.py migrate --noinput
python manage.py collectstatic --noinput || true
exec "$@"
