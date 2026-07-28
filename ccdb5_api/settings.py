import os
import tempfile

import django
from django.utils.crypto import get_random_string

from complaint_search.defaults import EXPORT_TEMP_MAX_AGE_SECONDS


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", get_random_string(50))

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = (
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "complaint_search",
    "flags",
)

MIDDLEWARE = (
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.security.SecurityMiddleware",
)

if django.VERSION < (2, 0):  # pragma: no cover
    MIDDLEWARE += (
        "django.contrib.auth.middleware.SessionAuthenticationMiddleware",
    )

ROOT_URLCONF = "ccdb5_api.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "ccdb5_api.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = "/static/"

# Export temp file cleanup. Override via environment when needed.
# EXPORT_TEMP_MAX_AGE_SECONDS should exceed worst-case export build time plus
# download time for the largest expected export.
EXPORT_TEMP_BASE_DIR = os.environ.get(
    "EXPORT_TEMP_BASE_DIR", tempfile.gettempdir()
)
EXPORT_TEMP_MAX_AGE_SECONDS = int(
    os.environ.get(
        "EXPORT_TEMP_MAX_AGE_SECONDS", EXPORT_TEMP_MAX_AGE_SECONDS
    )
)
