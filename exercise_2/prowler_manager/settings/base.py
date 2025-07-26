import os

from pathlib import Path

# Base settings
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # Build paths inside the project like this: BASE_DIR/'subdir'
SECRET_KEY = os.environ.get("SECRET_KEY", "secret_key")
DEBUG = False
ALLOWED_HOSTS = ["127.0.0.1", "0.0.0.0", "localhost"]

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "procrastinate.contrib.django",
    "rest_framework",
    "api.apps.APIConfig",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "prowler_manager.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
WSGI_APPLICATION = "prowler_manager.wsgi.application"

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "prowler_manager"),
        "USER": os.environ.get("POSTGRES_USER", "prowler"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
        "HOST": os.environ.get("POSTGRES_HOST", "postgres"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = False  # We are in an API
USE_TZ = False  # I'm a declared enemy of using time zones in the backend

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "console": {
            "format": "{levelname:8} {asctime} {name:30} {message}",
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "console",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        # Django framework loggers
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        # Application loggers
        "prowler_manager": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "api": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
        # Third-party libraries
        "rest_framework": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "procrastinate": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# REST Framework settings
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 10,
    "EXCEPTION_HANDLER": "api.utils.custom_exception_handler",
}

# API settings
CHECK_SLEEP_TIME = float(os.environ.get("CHECK_SLEEP_TIME", "3.0"))
CHECK_EXCEPTION_RATE = float(os.environ.get("CHECK_EXCEPTION_RATE", "0.05"))  # If check raise an exception, scan fails
CHECK_SUCCESS_RATE = float(os.environ.get("CHECK_SUCCESS_RATE", "0.8"))
