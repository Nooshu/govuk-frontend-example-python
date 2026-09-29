"""Django app config for component demos."""

from __future__ import annotations

from django.apps import AppConfig


class PreviewsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "previews"
    label = "previews"
    verbose_name = "GOV.UK component previews"
