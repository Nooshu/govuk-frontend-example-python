"""Reusable Django app: GOV.UK Frontend component renderers and template tags."""

from __future__ import annotations

from django.apps import AppConfig


class GovukComponentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "govuk_components"
    label = "govuk_components"
    verbose_name = "GOV.UK components"
