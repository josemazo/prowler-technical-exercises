"""
ASGI config for prowler_manager project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

environment = os.environ.get("ENVIRONMENT", "local")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"prowler_manager.settings.{environment}")

application = get_asgi_application()
