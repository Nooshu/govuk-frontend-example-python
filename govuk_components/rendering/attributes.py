"""Attribute and i18n helpers matching Nunjucks macros.

Tracks GOV.UK Frontend Nunjucks macros / ``template.njk`` for fixture HTML parity.
"""

from __future__ import annotations

from typing import Any

from .nunjucks import escape, get, indent, is_undefined, out, str_value, trim, truthy
from .params import Params, Safe


def Attributes(value: Any) -> str:
    """Render the ``attributes`` option like Frontend's private ``govukAttributes`` macro."""
    if isinstance(value, Safe):
        return str.__str__(value)
    if isinstance(value, str):
        return value
    if isinstance(value, Params):
        parts: list[str] = []
        for name in value:
            parts.append(attribute(name, value.get(name)))
        return "".join(parts)
    return ""


def attribute(name: str, item: Any) -> str:
    """Render a single entry of the ``attributes`` option."""
    value: Any = item
    optional = False
    if isinstance(item, Params):
        value = item.get("value")
        flag = item.get("optional")
        optional = isinstance(flag, bool) and flag

    empty = value is None or is_undefined(value)
    escaped = ""
    if not empty:
        escaped = (
            str.__str__(value) if isinstance(value, Safe) else escape(str_value(value))
        )

    if optional:
        is_bool = isinstance(value, bool)
        if is_bool and value:
            return " " + escape(name)
        if empty or (is_bool and not value):
            return ""
    return " " + escape(name) + '="' + escaped + '"'


def i18n_attributes(key: str, message: Any, messages: Any) -> str:
    """Render translated text into ``data-i18n.*`` attributes."""
    if truthy(messages):
        if not isinstance(messages, Params):
            return ""  # pragma: no cover
        parts: list[str] = []
        for rule in messages:
            parts.append(
                " data-i18n."
                + key
                + "."
                + rule
                + '="'
                + escape(str_value(messages.get(rule)))
                + '"'
            )
        return "".join(parts)
    if truthy(message):
        return " data-i18n." + key + '="' + escape(str_value(message)) + '"'
    return ""


def attribute_if(name: str, value: Any) -> str:
    """Render `` name="value"`` when the option is truthy."""
    if not truthy(value):
        return ""
    return " " + name + '="' + out(value) + '"'


def classes_if(value: Any) -> str:
    """Render `` some-class`` when the option is truthy."""
    if not truthy(value):
        return ""
    return " " + out(value)


def flag_if(suffix: str, value: Any) -> str:
    """Render a literal suffix when the option is truthy."""
    if not truthy(value):
        return ""
    return suffix


def content(params: Any, html_key: str, text_key: str) -> str:
    """Render ``x.html | safe if x.html else x.text``."""
    html = get(params, html_key)
    if truthy(html):
        return str_value(html)
    return out(get(params, text_key))


def content_indent(params: Any, html_key: str, text_key: str, width: int) -> str:
    """Render ``x.html | safe | trim | indent(width) if x.html else x.text``."""
    html = get(params, html_key)
    if truthy(html):
        return indent(trim(str_value(html)), width, False)
    return out(get(params, text_key))
