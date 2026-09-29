"""Ports for button-related Frontend components.

Tracks GOV.UK Frontend Nunjucks macros / ``template.njk`` for fixture HTML parity.
"""

from __future__ import annotations

from .attributes import Attributes, attribute_if, classes_if, flag_if
from .nunjucks import (
    def_truthy,
    indent,
    is_undefined,
    out,
    str_value,
    trim,
    truthy,
)
from .params import Params, Safe, new_params

# The leading newline is part of the upstream macro's output.
START_ICON = (
    "\n"
    '  <svg class="govuk-button__start-icon" xmlns="http://www.w3.org/2000/svg" '
    'width="17.5" height="19" viewBox="0 0 33 40" aria-hidden="true" focusable="false">\n'
    '    <path fill="currentColor" d="M0 0h13l20 20-20 20H0l20-20z"/>\n'
    "  </svg>"
)

# Trailing newline matches the captured `{% set %}` block upstream.
EXIT_THIS_PAGE_DEFAULT_HTML = (
    '  <span class="govuk-visually-hidden">Emergency</span> Exit this page\n'
)


def render_button(p: Params) -> str:
    from .nunjucks import escape

    class_names = "govuk-button"
    classes = p.get("classes")
    if truthy(classes):
        class_names += " " + str_value(classes)
    start_button = truthy(p.get("isStartButton"))
    if start_button:
        class_names += " govuk-button--start"

    common_attributes = (
        ' class="'
        + escape(class_names)
        + '" data-module="govuk-button"'
        + Attributes(p.get("attributes"))
        + attribute_if("id", p.get("id"))
    )

    html = p.get("html")
    text = out(p.get("text"))
    if truthy(html) and start_button:
        text = "<span>" + trim(str_value(html)) + "</span>"
    elif truthy(html):
        text = trim(str_value(html))

    parts: list[str] = []
    if truthy(p.get("href")):
        parts.append(
            '<a href="'
            + out(p.get("href"))
            + '" role="button" draggable="false"'
            + common_attributes
            + ">\n  "
            + indent(text, 2, False)
        )
    else:
        parts.append(
            '<button type="'
            + out(def_truthy(p.get("type"), "submit"))
            + '"'
            + attribute_if("value", p.get("value"))
            + attribute_if("name", p.get("name"))
            + flag_if(' disabled aria-disabled="true"', p.get("disabled"))
        )
        prevent_double_click = p.get("preventDoubleClick")
        if not is_undefined(prevent_double_click):
            parts.append(' data-prevent-double-click="' + out(prevent_double_click) + '"')
        parts.append(common_attributes + ">\n  " + indent(text, 2, False))

    if start_button:
        parts.append(START_ICON)
    if truthy(p.get("href")):
        parts.append("\n</a>")
    else:
        parts.append("\n</button>")
    return "".join(parts)


def render_exit_this_page(p: Params) -> str:
    html = p.get("html")
    if not truthy(html) and not truthy(p.get("text")):
        html = Safe(EXIT_THIS_PAGE_DEFAULT_HTML)

    button = render_button(
        new_params(
            "html",
            html,
            "text",
            p.get("text"),
            "classes",
            "govuk-button--warning govuk-exit-this-page__button govuk-js-exit-this-page-button",
            "href",
            def_truthy(p.get("redirectUrl"), "https://www.bbc.co.uk/weather"),
            "attributes",
            new_params("rel", "nofollow noreferrer"),
        )
    )

    return (
        "<div"
        + attribute_if("id", p.get("id"))
        + ' class="govuk-exit-this-page'
        + classes_if(p.get("classes"))
        + '" data-module="govuk-exit-this-page"'
        + Attributes(p.get("attributes"))
        + attribute_if("data-i18n.activated", p.get("activatedText"))
        + attribute_if("data-i18n.timed-out", p.get("timedOutText"))
        + attribute_if("data-i18n.press-two-more-times", p.get("pressTwoMoreTimesText"))
        + attribute_if("data-i18n.press-one-more-time", p.get("pressOneMoreTimeText"))
        + ">\n  "
        + indent(trim(button), 2, False)
        + "\n</div>"
    )
