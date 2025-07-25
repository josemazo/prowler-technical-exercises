"""
WSGI config for prowler_manager project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

environment = os.environ.get("ENVIRONMENT", "local")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"prowler_manager.settings.{environment}")

application = get_wsgi_application()
