"""Django settings for the GOV.UK Frontend Python example."""

from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-example-only-change-me-for-any-real-deployment",
)

DEBUG = os.environ.get("DEBUG", "true").lower() in {"1", "true", "yes"}

# Demos (component catalogue) are on in DEBUG, or when DEMOS_ENABLED=true (Render).
_demos_env = os.environ.get("DEMOS_ENABLED")
DEMOS_ENABLED = (
    DEBUG
    if _demos_env is None
    else _demos_env.lower() in {"1", "true", "yes"}  # pragma: no cover
)

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("ALLOWED_HOSTS", "*").split(",")
    if host.strip()
]

INSTALLED_APPS = [
    # No contenttypes / auth — sessions live in LocMemCache; no ORM models required.
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "govuk_components",
    "service",
    "previews",
]

MIDDLEWARE = [
    "config.middleware.CompressionMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "config.middleware.BaselineHeadersMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "govuk_components" / "templates",
            BASE_DIR / "service" / "templates",
            BASE_DIR / "previews" / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "config.context_processors.service_chrome",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# No database — in-memory sessions only (Render free tier friendly).
DATABASES: dict[str, dict[str, str]] = {}

# Pinned GOV.UK Frontend release (must match package.json / fixtures).
GOVUK_FRONTEND_VERSION = "6.5.1"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "govuk-example",
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
SESSION_COOKIE_NAME = "rod_session"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_AGE = 4 * 60 * 60

LANGUAGE_CODE = "en-gb"
TIME_ZONE = "Europe/London"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Compiled Sass + GOV.UK Frontend assets (fonts, images, JS).
GOVUK_FRONTEND_ROOT = BASE_DIR / "node_modules" / "govuk-frontend"
GOVUK_COMPONENTS_DIR = GOVUK_FRONTEND_ROOT / "dist" / "govuk" / "components"
DIST_DIR = BASE_DIR / "dist"
BASELINE_POLICY_PATH = BASE_DIR / "baseline" / "policy.json"

SERVICE_NAME = "Apply for a fishing rod licence"
SERVICE_NAME_CY = "Gwneud cais am drwydded bysgota"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# CSRF: Django default; forms include {% csrf_token %}.
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
