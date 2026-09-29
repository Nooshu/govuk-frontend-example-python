"""Django template tags for GOV.UK Frontend components."""

from __future__ import annotations

from typing import Any

from django import template
from django.utils.safestring import mark_safe

from govuk_components.rendering import MustRender
from govuk_components.rendering.params import Params, params_from_mapping

register = template.Library()


@register.simple_tag
def govuk(component: str, options: dict[str, Any] | Params | None = None) -> str:
    """Render a GOV.UK Frontend component by kebab-case name.

    Usage::

        {% load govuk %}
        {% govuk "button" button_opts %}
    """
    params = (
        options
        if isinstance(options, Params)
        else params_from_mapping(options or {})
    )
    return mark_safe(MustRender(component, params))  # noqa: S308 — trusted renderer output


@register.simple_tag
def govuk_html(html: str) -> str:
    """Mark trusted component HTML safe for insertion into the page shell."""
    return mark_safe(html)  # noqa: S308
