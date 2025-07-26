#!/bin/sh

set -ex

if [ $1 = "test" ]; then
    ruff check
    ty check
    ENVIRONMENT=test exec pytest -v --no-migrations --cov

elif [ $1 = "worker" ]; then
    exec python manage.py procrastinate worker --concurrency $WORKER_CONCURRENCY

elif [ $1 = "debug" ]; then
    exec python -m debugpy --listen 0.0.0.0:$DEBUG_PORT manage.py runserver 0.0.0.0:$API_PORT  --noreload

elif [ $ENVIRONMENT = "local" ]; then
    exec python  manage.py runserver 0.0.0.0:$API_PORT

else
    python manage.py collectstatic --noinput
    exec gunicorn --bind 0.0.0.0:$API_PORT prowler_manager.wsgi:application

fi
