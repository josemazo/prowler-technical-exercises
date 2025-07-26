from prowler_manager.settings.base import *  # noqa: F403

# Use SQLite in-memory database for tests
DATABASES["default"] = {  # noqa: F405
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": ":memory:",
}

# Only JSON in test
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = ["rest_framework.renderers.JSONRenderer"]  # noqa: F405
REST_FRAMEWORK["DEFAULT_PARSER_CLASSES"] = ["rest_framework.parsers.JSONParser"]  # noqa: F405

# Skip scan sleep and all checks success
CHECK_SLEEP_TIME = 0
CHECK_EXCEPTION_RATE = 0
CHECK_SUCCESS_RATE = 1
