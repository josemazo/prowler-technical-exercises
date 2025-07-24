#!/bin/sh

set -ex

if [ "$1" = "test" ]; then
    ruff check
    ty check
    ENVIRONMENT=test exec pytest

elif [ "$1" = "debug" ]; then
    ENVIRONMENT=local exec debugpy --wait-for-client --listen 0.0.0.0:$DEBUG_PORT -m python manage.py runserver --noreload 0.0.0.0:$API_PORT

elif [ $ENVIRONMENT = "local" ]; then
    exec python manage.py runserver 0.0.0.0:$API_PORT

else
    exec uvicorn --host 0.0.0.0 --port $API_PORT prowler_manager.asgi:application

fi
