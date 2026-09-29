"""Ports for text components (inset-text, warning-text, tag, …).

Tracks GOV.UK Frontend Nunjucks macros / ``template.njk`` for fixture HTML parity.
"""

from __future__ import annotations

from .attributes import (
    Attributes,
    attribute_if,
    classes_if,
    content,
    content_indent,
    flag_if,
)
from .components_button import render_button
from .nunjucks import (
    concat_if,
    contains,
    def_,
    def_truthy,
    escape,
    get,
    heading,
    indent,
    items,
    out,
    str_value,
    trim,
    truthy,
)
from .params import Params, new_params


def render_back_link(p: Params) -> str:
    text = out(def_truthy(p.get("text"), "Back"))
    html = p.get("html")
    if truthy(html):
        text = str_value(html)
    return (
        '<a href="'
        + out(def_truthy(p.get("href"), "#"))
        + '" class="govuk-back-link'
        + classes_if(p.get("classes"))
        + '"'
        + Attributes(p.get("attributes"))
        + ">"
        + text
        + "</a>"
    )


def render_skip_link(p: Params) -> str:
    return (
        '<a href="'
        + out(def_truthy(p.get("href"), "#content"))
        + '" class="govuk-skip-link'
        + classes_if(p.get("classes"))
        + '"'
        + Attributes(p.get("attributes"))
        + ' data-module="govuk-skip-link">'
        + content(p, "html", "text")
        + "</a>"
    )


def render_hint(p: Params) -> str:
    return (
        "<div"
        + attribute_if("id", p.get("id"))
        + ' class="govuk-hint'
        + classes_if(p.get("classes"))
        + '"'
        + Attributes(p.get("attributes"))
        + ">\n  "
        + content_indent(p, "html", "text", 2)
        + "\n</div>"
    )


def render_inset_text(p: Params) -> str:
    return (
        "<div"
        + attribute_if("id", p.get("id"))
        + ' class="govuk-inset-text'
        + classes_if(p.get("classes"))
        + '"'
        + Attributes(p.get("attributes"))
        + ">\n  "
        + content_indent(p, "html", "text", 2)
        + "\n</div>"
    )


def render_tag(p: Params | None) -> str:
    if p is None:
        p = Params()  # pragma: no cover
    return (
        '<strong class="govuk-tag'
        + classes_if(p.get("classes"))
        + '"'
        + Attributes(p.get("attributes"))
        + ">\n  "
        + content_indent(p, "html", "text", 2)
        + "\n</strong>"
    )


def render_warning_text(p: Params) -> str:
    return (
        '<div class="govuk-warning-text'
        + classes_if(p.get("classes"))
        + '"'
        + Attributes(p.get("attributes"))
        + ">\n"
        + '  <span class="govuk-warning-text__icon" aria-hidden="true">!</span>\n'
        + '  <strong class="govuk-warning-text__text">\n'
        + '    <span class="govuk-visually-hidden">'
        + out(def_truthy(p.get("iconFallbackText"), "Warning"))
        + "</span>\n"
        + "    "
        + content(p, "html", "text")
        + "\n"
        + "  </strong>\n</div>"
    )


def render_error_message(p: Params) -> str:
    visually_hidden = def_(p.get("visuallyHiddenText"), "Error")
    message = content_indent(p, "html", "text", 2)

    parts: list[str] = []
    parts.append(
        "<p"
        + attribute_if("id", p.get("id"))
        + ' class="govuk-error-message'
        + classes_if(p.get("classes"))
        + '"'
        + Attributes(p.get("attributes"))
        + ">\n"
    )
    if truthy(visually_hidden):
        parts.append(
            '  <span class="govuk-visually-hidden">'
            + out(visually_hidden)
            + ":</span> "
            + message
            + "\n"
        )
    else:
        parts.append("  " + message + "\n")
    parts.append("</p>")
    return "".join(parts)


def render_details(p: Params) -> str:
    return (
        "<details"
        + attribute_if("id", p.get("id"))
        + ' class="govuk-details'
        + classes_if(p.get("classes"))
        + '"'
        + Attributes(p.get("attributes"))
        + flag_if(" open", p.get("open"))
        + ">\n"
        + '  <summary class="govuk-details__summary">\n'
        + '    <span class="govuk-details__summary-text">\n'
        + "      "
        + content_indent(p, "summaryHtml", "summaryText", 6)
        + "\n"
        + "    </span>\n  </summary>\n"
        + '  <div class="govuk-details__text">\n'
        + "    "
        + content(p, "html", "text")
        + "\n"
        + "  </div>\n</details>"
    )


def render_label(p: Params) -> str:
    if not truthy(p.get("html")) and not truthy(p.get("text")):
        return ""
    label = (
        '<label class="govuk-label'
        + classes_if(p.get("classes"))
        + '"'
        + Attributes(p.get("attributes"))
        + attribute_if("for", p.get("for"))
        + ">\n  "
        + content_indent(p, "html", "text", 2)
        + "\n</label>\n"
    )

    if truthy(p.get("isPageHeading")):
        return (
            '<h1 class="govuk-label-wrapper">\n  '
            + indent(trim(label), 2, False)
            + "\n</h1>\n"
        )
    return trim(label) + "\n"


def render_panel(p: Params) -> str:
    classes = p.get("classes")
    interruption = truthy(classes) and contains("govuk-panel--interruption", classes)
    level = heading(p.get("headingLevel"), "1")

    parts: list[str] = []
    parts.append('<div class="govuk-panel')
    if not interruption:
        parts.append(" govuk-panel--confirmation")
    parts.append(classes_if(classes) + '"' + Attributes(p.get("attributes")) + ">\n")
    parts.append(
        "  <h"
        + level
        + ' class="govuk-panel__title">'
        + "\n    "
        + content(p, "titleHtml", "titleText")
        + "\n  </h"
        + level
        + ">\n"
    )

    if truthy(p.get("html")) or truthy(p.get("text")):
        parts.append(
            '  <div class="govuk-panel__body">\n    '
            + content_indent(p, "html", "text", 4)
            + "\n  </div>\n"
        )

    actions = p.get("actions")
    if interruption and truthy(actions):
        parts.append(
            '  <div class="govuk-panel__actions'
            + classes_if(get(actions, "classes"))
            + '"'
            + Attributes(get(actions, "attributes"))
            + ">"
        )
        entries = items(get(actions, "items"))
        if len(entries) > 0:
            parts.append('<div class="govuk-button-group">\n')
            for action in entries:
                parts.append(
                    "      " + indent(trim(_panel_action(action)), 6, False) + "\n"
                )
            parts.append("    </div>")
        parts.append("</div>\n")

    parts.append("</div>")
    return "".join(parts)


def _panel_action(action: object) -> str:
    href = get(action, "href")
    if not truthy(href) or str_value(get(action, "type")) == "button":
        return render_button(
            new_params(
                "text",
                get(action, "text"),
                "type",
                def_truthy(get(action, "type"), "button"),
                "classes",
                "govuk-button--inverse" + concat_if(" ", get(action, "classes")),
                "href",
                href,
                "attributes",
                get(action, "attributes"),
            )
        )
    return (
        '<a class="govuk-link govuk-link--inverse'
        + classes_if(get(action, "classes"))
        + '" href="'
        + out(href)
        + '"'
        + Attributes(get(action, "attributes"))
        + ">"
        + out(get(action, "text"))
        + "</a>"
    )


def render_phase_banner(p: Params) -> str:
    tag = p.get("tag")
    tag_html = render_tag(
        new_params(
            "text",
            get(tag, "text"),
            "html",
            get(tag, "html"),
            "classes",
            "govuk-phase-banner__content__tag" + concat_if(" ", get(tag, "classes")),
        )
    )
    return (
        '<div class="govuk-phase-banner govuk-width-container'
        + classes_if(p.get("classes"))
        + '"'
        + Attributes(p.get("attributes"))
        + ">\n"
        + '  <p class="govuk-phase-banner__content">\n'
        + "    "
        + indent(trim(tag_html), 4, False)
        + "\n"
        + '    <span class="govuk-phase-banner__text">\n'
        + "      "
        + content_indent(p, "html", "text", 6)
        + "\n"
        + "    </span>\n  </p>\n</div>"
    )


def render_feedback(p: Params) -> str:
    level = heading(p.get("headingLevel"), "2")

    parts: list[str] = []
    parts.append(
        '<div class="govuk-feedback govuk-width-container'
        + classes_if(p.get("classes"))
        + '"'
        + Attributes(p.get("attributes"))
        + ">\n"
    )
    parts.append('  <div class="govuk-grid-row">\n')
    parts.append('    <div class="govuk-grid-column-two-thirds">\n')
    parts.append(
        "      <h"
        + level
        + ' class="govuk-feedback__title">'
        + "\n        "
        + content(p, "titleHtml", "titleText")
        + "\n      </h"
        + level
        + ">\n"
    )

    html, text = p.get("html"), p.get("text")
    if truthy(html) or truthy(text):  # pragma: no branch
        parts.append('        <div class="govuk-feedback__body">\n')
        if truthy(html):
            parts.append(
                "            " + indent(trim(str_value(html)), 4, False) + "\n"
            )
        elif truthy(text):  # pragma: no branch
            parts.append('            <p class="govuk-body">\n')
            parts.append(
                "              "
                + escape(indent(trim(str_value(text)), 6, False))
                + "\n"
            )
            parts.append("            </p>\n")
        parts.append("        </div>\n")

    parts.append("    </div>\n  </div>\n</div>")
    return "".join(parts)


def render_fieldset(p: Params) -> str:
    parts: list[str] = []
    parts.append(
        '<fieldset class="govuk-fieldset'
        + classes_if(p.get("classes"))
        + '"'
        + attribute_if("role", p.get("role"))
        + attribute_if("aria-describedby", p.get("describedBy"))
        + Attributes(p.get("attributes"))
        + ">\n"
    )

    legend = p.get("legend")
    if truthy(get(legend, "html")) or truthy(get(legend, "text")):  # pragma: no branch
        parts.append(
            '  <legend class="govuk-fieldset__legend'
            + classes_if(get(legend, "classes"))
            + '">\n'
        )
        if truthy(get(legend, "isPageHeading")):
            parts.append('    <h1 class="govuk-fieldset__heading">\n')
            parts.append(
                "      " + content_indent(legend, "html", "text", 6) + "\n"
            )
            parts.append("    </h1>\n")
        else:
            parts.append(
                "    " + content_indent(legend, "html", "text", 4) + "\n"
            )
        parts.append("  </legend>\n")

    html = p.get("html")
    if truthy(html):
        parts.append("  " + str_value(html) + "\n")

    parts.append("</fieldset>")
    return "".join(parts)
