from prowler_manager.settings.base import *  # noqa: F403

# CSRF and session cookies should be secure in production
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

# Only JSON in production
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = ["rest_framework.renderers.JSONRenderer"]  # noqa: F405
REST_FRAMEWORK["DEFAULT_PARSER_CLASSES"] = ["rest_framework.parsers.JSONParser"]  # noqa: F405
