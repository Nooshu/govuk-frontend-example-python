"""Template context for shared service chrome."""

from __future__ import annotations

from typing import Any

from django.conf import settings
from django.http import HttpRequest
from service.assets import load_page_assets

from config.baseline import js_enabled_snippet


def service_chrome(request: HttpRequest) -> dict[str, Any]:
    assets = load_page_assets()
    return {
        "service_name": settings.SERVICE_NAME,
        "service_name_cy": settings.SERVICE_NAME_CY,
        "demos_enabled": settings.DEMOS_ENABLED,
        "js_enabled_snippet": js_enabled_snippet(),
        "stylesheet_href": assets.stylesheet_href,
        "app_module_href": assets.app_module_href,
        "frontend_version": settings.GOVUK_FRONTEND_VERSION,
    }
