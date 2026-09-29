"""Django app config for the example licence journey."""

from __future__ import annotations

from django.apps import AppConfig


class ServiceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "service"
    label = "service"
    verbose_name = "Rod fishing licence service"
