"""Ports for list-like components (table, task-list, summary-list, …).

Tracks GOV.UK Frontend Nunjucks macros / ``template.njk`` for fixture HTML parity.
"""

from __future__ import annotations

from typing import Any

from .attributes import (
    Attributes,
    attribute_if,
    classes_if,
    content,
    content_indent,
    flag_if,
    i18n_attributes,
)
from .components_text import render_tag
from .nunjucks import (
    def_,
    def_truthy,
    escape,
    get,
    heading,
    indent,
    is_undefined,
    items,
    length,
    out,
    str_value,
    trim,
    truthy,
)
from .params import Params, Undefined


def render_accordion(p: Params) -> str:
    parts: list[str] = []
    parts.append(
        '<div class="govuk-accordion'
        + classes_if(p.get("classes"))
        + '" data-module="govuk-accordion" id="'
        + out(p.get("id"))
        + '"'
        + i18n_attributes("hide-all-sections", p.get("hideAllSectionsText"), Undefined)
        + i18n_attributes("hide-section", p.get("hideSectionText"), Undefined)
        + i18n_attributes(
            "hide-section-aria-label", p.get("hideSectionAriaLabelText"), Undefined
        )
        + i18n_attributes("show-all-sections", p.get("showAllSectionsText"), Undefined)
        + i18n_attributes("show-section", p.get("showSectionText"), Undefined)
        + i18n_attributes(
            "show-section-aria-label", p.get("showSectionAriaLabelText"), Undefined
        )
    )
    remember = p.get("rememberExpanded")
    if not is_undefined(remember):
        parts.append(' data-remember-expanded="' + escape(str_value(remember)) + '"')
    parts.append(Attributes(p.get("attributes")) + ">\n")

    for index, item in enumerate(items(p.get("items"))):
        if not truthy(item):
            continue
        parts.append(_accordion_item(p, item, index + 1))

    parts.append("</div>")
    return "".join(parts)


def _accordion_item(p: Params, item: Any, index: int) -> str:
    level = heading(p.get("headingLevel"), "2")
    id_ = out(p.get("id"))
    position = str(index)
    item_heading = get(item, "heading")
    summary = get(item, "summary")
    item_content = get(item, "content")

    parts: list[str] = []
    parts.append(
        '  <div class="govuk-accordion__section'
        + flag_if(" govuk-accordion__section--expanded", get(item, "expanded"))
        + '">\n'
    )
    parts.append('    <div class="govuk-accordion__section-header">\n')
    parts.append(
        "      <h" + level + ' class="govuk-accordion__section-heading">\n'
    )
    parts.append(
        '        <span class="govuk-accordion__section-button" id="'
        + id_
        + "-heading-"
        + position
        + '">\n'
    )
    parts.append(
        "          " + content_indent(item_heading, "html", "text", 8) + "\n"
    )
    parts.append("        </span>\n      </h" + level + ">\n")
    if truthy(get(summary, "html")) or truthy(get(summary, "text")):
        parts.append(
            '      <div class="govuk-accordion__section-summary govuk-body" id="'
            + id_
            + "-summary-"
            + position
            + '">\n'
        )
        parts.append(
            "        " + content_indent(summary, "html", "text", 8) + "\n"
        )
        parts.append("      </div>\n")
    parts.append("    </div>\n")
    parts.append(
        '    <div id="'
        + id_
        + "-content-"
        + position
        + '" class="govuk-accordion__section-content">\n'
    )
    html, text = get(item_content, "html"), get(item_content, "text")
    if truthy(html):
        parts.append("      " + indent(trim(str_value(html)), 6, False) + "\n")
    elif truthy(text):  # pragma: no branch
        parts.append('      <p class="govuk-body">\n')
        parts.append(
            "        " + escape(indent(trim(str_value(text)), 8, False)) + "\n"
        )
        parts.append("      </p>\n")
    parts.append("    </div>\n  </div>\n")
    return "".join(parts)


def render_error_summary(p: Params) -> str:
    parts: list[str] = []
    parts.append('<div class="govuk-error-summary' + classes_if(p.get("classes")) + '"')
    auto_focus = p.get("disableAutoFocus")
    if not is_undefined(auto_focus):
        parts.append(' data-disable-auto-focus="' + out(auto_focus) + '"')
    parts.append(Attributes(p.get("attributes")) + ' data-module="govuk-error-summary">')

    parts.append('\n  <div role="alert">\n')
    parts.append('    <h2 class="govuk-error-summary__title">\n')
    parts.append(
        "      " + content_indent(p, "titleHtml", "titleText", 6) + "\n"
    )
    parts.append("    </h2>\n")
    parts.append('    <div class="govuk-error-summary__body">\n')

    if truthy(p.get("descriptionHtml")) or truthy(p.get("descriptionText")):
        parts.append(
            "      <p>\n        "
            + content_indent(p, "descriptionHtml", "descriptionText", 8)
            + "\n      </p>\n"
        )

    error_list = items(p.get("errorList"))
    if len(error_list) > 0:
        parts.append('        <ul class="govuk-list govuk-error-summary__list">\n')
        for item in error_list:
            parts.append("          <li>\n")
            href = get(item, "href")
            if truthy(href):
                parts.append(
                    '            <a href="'
                    + out(href)
                    + '"'
                    + Attributes(get(item, "attributes"))
                    + ">"
                    + content_indent(item, "html", "text", 12)
                    + "</a>\n"
                )
            else:
                parts.append(
                    "            "
                    + content_indent(item, "html", "text", 10)
                    + "\n"
                )
            parts.append("          </li>\n")
        parts.append("        </ul>\n")

    parts.append("    </div>\n  </div>\n</div>")
    return "".join(parts)


def render_notification_banner(p: Params) -> str:
    success = str_value(p.get("type")) == "success"
    type_class = ""
    if success:
        type_class = " govuk-notification-banner--" + escape(str_value(p.get("type")))

    role = "region"
    if truthy(p.get("role")):
        role = str_value(p.get("role"))
    elif success:
        role = "alert"

    if truthy(p.get("titleHtml")):
        title = str_value(p.get("titleHtml"))
    elif truthy(p.get("titleText")):
        title = out(p.get("titleText"))
    elif success:
        title = "Success"
    else:
        title = "Important"

    title_id = out(def_truthy(p.get("titleId"), "govuk-notification-banner-title"))
    level = out(def_truthy(p.get("titleHeadingLevel"), "2"))

    parts: list[str] = []
    parts.append(
        '<div class="govuk-notification-banner'
        + type_class
        + classes_if(p.get("classes"))
        + '" role="'
        + escape(role)
        + '" aria-labelledby="'
        + title_id
        + '" data-module="govuk-notification-banner"'
    )
    auto_focus = p.get("disableAutoFocus")
    if not is_undefined(auto_focus):
        parts.append(' data-disable-auto-focus="' + out(auto_focus) + '"')
    parts.append(Attributes(p.get("attributes")) + ">\n")
    parts.append('  <div class="govuk-notification-banner__header">\n')
    parts.append(
        "    <h"
        + level
        + ' class="govuk-notification-banner__title" id="'
        + title_id
        + '">\n'
    )
    parts.append("      " + title + "\n    </h" + level + ">\n  </div>\n")
    parts.append('  <div class="govuk-notification-banner__content">\n')
    html, text = p.get("html"), p.get("text")
    if truthy(html):
        parts.append("    " + indent(trim(str_value(html)), 4, False) + "\n")
    elif truthy(text):  # pragma: no branch
        parts.append('    <p class="govuk-notification-banner__heading">\n')
        parts.append(
            "      " + escape(indent(trim(str_value(text)), 6, False)) + "\n"
        )
        parts.append("    </p>\n")
    parts.append("  </div>\n</div>")
    return "".join(parts)


def render_summary_list(p: Params) -> str:
    card = p.get("card")
    card_title = get(card, "title")

    any_row_has_actions = False
    for row in items(p.get("rows")):
        if length(get(row, "actions", "items")) > 0:
            any_row_has_actions = True

    list_parts: list[str] = []
    list_parts.append(
        '<dl class="govuk-summary-list'
        + classes_if(p.get("classes"))
        + '"'
        + Attributes(p.get("attributes"))
        + ">\n"
    )
    for row in items(p.get("rows")):
        if not truthy(row):
            continue
        key, value, actions = get(row, "key"), get(row, "value"), get(row, "actions")
        list_parts.append(
            '  <div class="govuk-summary-list__row'
            + flag_if(
                " govuk-summary-list__row--no-actions",
                any_row_has_actions and not truthy(get(actions, "items")),
            )
            + classes_if(get(row, "classes"))
            + '">\n'
        )
        list_parts.append(
            '    <dt class="govuk-summary-list__key'
            + classes_if(get(key, "classes"))
            + '">\n      '
            + content_indent(key, "html", "text", 6)
            + "\n    </dt>\n"
        )
        list_parts.append(
            '    <dd class="govuk-summary-list__value'
            + classes_if(get(value, "classes"))
            + '">\n      '
            + content_indent(value, "html", "text", 6)
            + "\n    </dd>\n"
        )

        entries = items(get(actions, "items"))
        if len(entries) > 0:
            list_parts.append(
                '    <dd class="govuk-summary-list__actions'
                + classes_if(get(actions, "classes"))
                + '">\n'
            )
            if len(entries) == 1:
                list_parts.append(
                    indent(trim(_summary_action_link(entries[0], card_title)), 6, True)
                    + "\n"
                )
            else:
                list_parts.append(
                    '      <ul class="govuk-summary-list__actions-list">\n'
                )
                for action in entries:
                    list_parts.append(
                        '        <li class="govuk-summary-list__actions-list-item">\n'
                    )
                    list_parts.append(
                        "          "
                        + indent(trim(_summary_action_link(action, card_title)), 8, False)
                        + "\n"
                    )
                    list_parts.append("        </li>\n")
                list_parts.append("      </ul>\n")
            list_parts.append("    </dd>\n")
        list_parts.append("  </div>\n")
    list_parts.append("</dl>")

    if truthy(card):
        return _summary_card(card, indent(trim("".join(list_parts)), 4, False))
    return trim("".join(list_parts))


def _summary_action_link(action: Any, card_title: Any) -> str:
    parts: list[str] = []
    parts.append(
        '  <a class="govuk-link'
        + classes_if(get(action, "classes"))
        + '" href="'
        + out(get(action, "href"))
        + '"'
        + Attributes(get(action, "attributes"))
        + ">"
    )
    html = get(action, "html")
    if truthy(html):
        parts.append(indent(str_value(html), 4, False))
    else:
        parts.append(out(get(action, "text")))
    visually_hidden = get(action, "visuallyHiddenText")
    if truthy(visually_hidden) or truthy(card_title):
        parts.append('<span class="govuk-visually-hidden">')
        if truthy(visually_hidden):
            parts.append(" " + out(visually_hidden))
        if truthy(card_title):
            title = out(get(card_title, "text"))
            html = get(card_title, "html")
            if truthy(html):
                title = indent(str_value(html), 6, False)  # pragma: no cover
            parts.append(" (" + title + ")")
        parts.append("</span>")
    parts.append("</a>\n")
    return "".join(parts)


def _summary_card(card: Any, body: str) -> str:
    title = get(card, "title")
    level = heading(get(title, "headingLevel"), "2")
    actions = get(card, "actions")

    parts: list[str] = []
    parts.append(
        '<div class="govuk-summary-card'
        + classes_if(get(card, "classes"))
        + '"'
        + Attributes(get(card, "attributes"))
        + ">\n"
    )
    parts.append('  <div class="govuk-summary-card__title-wrapper">\n')
    if truthy(title):
        parts.append(
            "    <h"
            + level
            + ' class="govuk-summary-card__title'
            + classes_if(get(title, "classes"))
            + '">\n      '
            + content_indent(title, "html", "text", 6)
            + "\n    </h"
            + level
            + ">\n"
        )
    entries = items(get(actions, "items"))
    if len(entries) > 0:
        if len(entries) == 1:
            parts.append(
                '    <div class="govuk-summary-card__actions'
                + classes_if(get(actions, "classes"))
                + '">\n'
            )
            parts.append(
                "      "
                + indent(trim(_summary_action_link(entries[0], title)), 4, False)
                + "\n"
            )
            parts.append("    </div>\n")
        else:
            parts.append(
                '    <ul class="govuk-summary-card__actions'
                + classes_if(get(actions, "classes"))
                + '">\n'
            )
            for action in entries:
                parts.append('      <li class="govuk-summary-card__action">\n')
                parts.append(
                    "        "
                    + indent(trim(_summary_action_link(action, title)), 8, False)
                    + "\n"
                )
                parts.append("      </li>\n")
            parts.append("    </ul>\n")
    parts.append("  </div>\n\n")
    parts.append(
        '  <div class="govuk-summary-card__content">\n    '
        + body
        + "\n  </div>\n</div>\n"
    )
    return "".join(parts)


def render_table(p: Params) -> str:
    parts: list[str] = []
    parts.append(
        '<table class="govuk-table'
        + classes_if(p.get("classes"))
        + '"'
        + Attributes(p.get("attributes"))
        + ">\n"
    )

    caption = p.get("caption")
    if truthy(caption):
        parts.append(
            '  <caption class="govuk-table__caption'
            + classes_if(p.get("captionClasses"))
            + '">'
            + out(caption)
            + "</caption>\n"
        )

    head = items(p.get("head"))
    if truthy(p.get("head")):
        parts.append('  <thead class="govuk-table__head">\n')
        parts.append('    <tr class="govuk-table__row">\n')
        for item in head:
            parts.append(
                '      <th scope="col" class="govuk-table__header'
                + _format_class("govuk-table__header--", get(item, "format"))
                + classes_if(get(item, "classes"))
                + '"'
                + attribute_if("colspan", get(item, "colspan"))
                + attribute_if("rowspan", get(item, "rowspan"))
                + Attributes(get(item, "attributes"))
                + ">"
                + content(item, "html", "text")
                + "</th>\n"
            )
        parts.append("    </tr>\n  </thead>\n")

    parts.append('  <tbody class="govuk-table__body">\n')
    for row in items(p.get("rows")):
        if not truthy(row):
            continue
        parts.append('    <tr class="govuk-table__row">\n')
        for index, cell in enumerate(items(row)):
            common = (
                attribute_if("colspan", get(cell, "colspan"))
                + attribute_if("rowspan", get(cell, "rowspan"))
                + Attributes(get(cell, "attributes"))
            )
            if index == 0 and truthy(p.get("firstCellIsHeader")):
                parts.append(
                    '      <th scope="row" class="govuk-table__header'
                    + classes_if(get(cell, "classes"))
                    + '"'
                    + common
                    + ">"
                    + content(cell, "html", "text")
                    + "</th>\n"
                )
            else:
                parts.append(
                    '      <td class="govuk-table__cell'
                    + _format_class("govuk-table__cell--", get(cell, "format"))
                    + classes_if(get(cell, "classes"))
                    + '"'
                    + common
                    + ">"
                    + content(cell, "html", "text")
                    + "</td>\n"
                )
        parts.append("    </tr>\n")
    parts.append("  </tbody>\n</table>")
    return "".join(parts)


def _format_class(prefix: str, format_: Any) -> str:
    if not truthy(format_):
        return ""
    return " " + prefix + out(format_)


def render_tabs(p: Params) -> str:
    id_prefix = ""
    prefix = p.get("idPrefix")
    if truthy(prefix):
        id_prefix = str_value(prefix)

    parts: list[str] = []
    parts.append(
        "<div"
        + attribute_if("id", p.get("id"))
        + ' class="govuk-tabs'
        + classes_if(p.get("classes"))
        + '"'
        + Attributes(p.get("attributes"))
        + ' data-module="govuk-tabs">\n'
    )
    parts.append(
        '  <h2 class="govuk-tabs__title">\n    '
        + out(def_(p.get("title"), "Contents"))
        + "\n  </h2>\n"
    )

    entries = items(p.get("items"))
    if len(entries) > 0:
        parts.append('  <ul class="govuk-tabs__list">\n')
        for index, item in enumerate(entries):
            if not truthy(item):
                continue
            parts.append(
                indent(trim(_tab_list_item(item, index + 1, id_prefix)), 4, True) + "\n"
            )
        parts.append("  </ul>\n")
        for index, item in enumerate(entries):
            if not truthy(item):
                continue
            parts.append(
                indent(trim(_tab_panel(item, index + 1, id_prefix)), 2, True) + "\n"
            )

    parts.append("</div>")
    return "".join(parts)


def _tab_panel_id(item: Any, index: int, id_prefix: str) -> str:
    id_ = get(item, "id")
    if truthy(id_):
        return str_value(id_)
    return id_prefix + "-" + str(index)


def _tab_list_item(item: Any, index: int, id_prefix: str) -> str:
    return (
        '<li class="govuk-tabs__list-item'
        + flag_if(" govuk-tabs__list-item--selected", index == 1)
        + '">\n'
        + '  <a class="govuk-tabs__tab" href="#'
        + escape(_tab_panel_id(item, index, id_prefix))
        + '"'
        + Attributes(get(item, "attributes"))
        + ">\n    "
        + out(get(item, "label"))
        + "\n  </a>\n</li>\n"
    )


def _tab_panel(item: Any, index: int, id_prefix: str) -> str:
    panel = get(item, "panel")
    parts: list[str] = []
    parts.append(
        '<div class="govuk-tabs__panel'
        + flag_if(" govuk-tabs__panel--hidden", index > 1)
        + '" id="'
        + escape(_tab_panel_id(item, index, id_prefix))
        + '"'
        + Attributes(get(panel, "attributes"))
        + ">\n"
    )
    html, text = get(panel, "html"), get(panel, "text")
    if truthy(html):
        parts.append("  " + indent(trim(str_value(html)), 2, False) + "\n")
    elif truthy(text):  # pragma: no branch
        parts.append('  <p class="govuk-body">' + out(text) + "</p>\n")
    parts.append("</div>\n")
    return "".join(parts)


def render_task_list(p: Params) -> str:
    id_prefix = "task-list"
    prefix = p.get("idPrefix")
    if truthy(prefix):
        id_prefix = str_value(prefix)

    parts: list[str] = []
    parts.append(
        '<ul class="govuk-task-list'
        + classes_if(p.get("classes"))
        + '"'
        + Attributes(p.get("attributes"))
        + ">\n"
    )
    for index, item in enumerate(items(p.get("items"))):
        if truthy(item):
            parts.append(_task_list_item(item, index + 1, id_prefix) + "\n")
        else:
            parts.append("\n")
    parts.append("</ul>")
    return "".join(parts)


def _task_list_item(item: Any, index: int, id_prefix: str) -> str:
    position = str(index)
    hint_id = id_prefix + "-" + position + "-hint"
    status_id = id_prefix + "-" + position + "-status"
    title = get(item, "title")
    hint = get(item, "hint")
    status = get(item, "status")

    parts: list[str] = []
    parts.append(
        '  <li class="govuk-task-list__item'
        + flag_if(" govuk-task-list__item--with-link", get(item, "href"))
        + classes_if(get(item, "classes"))
        + '">\n'
    )
    parts.append('    <div class="govuk-task-list__name-and-hint">\n')

    href = get(item, "href")
    if truthy(href):
        described_by = status_id
        if truthy(hint):
            described_by = hint_id + " " + status_id
        parts.append(
            '      <a class="govuk-link govuk-task-list__link'
            + classes_if(get(title, "classes"))
            + '" href="'
            + out(href)
            + '" aria-describedby="'
            + escape(described_by)
            + '">\n'
        )
        parts.append(
            "        " + content_indent(title, "html", "text", 8) + "\n"
        )
        parts.append("      </a>\n")
    else:
        parts.append(
            "      <div" + attribute_if("class", get(title, "classes")) + ">\n"
        )
        parts.append(
            "        " + content_indent(title, "html", "text", 8) + "\n"
        )
        parts.append("      </div>\n")

    if truthy(hint):
        parts.append(
            '      <div id="'
            + escape(hint_id)
            + '" class="govuk-task-list__hint">\n'
        )
        parts.append(
            "        " + content_indent(hint, "html", "text", 8) + "\n"
        )
        parts.append("      </div>\n")
    parts.append("    </div>\n")

    parts.append(
        '    <div class="govuk-task-list__status'
        + classes_if(get(status, "classes"))
        + '" id="'
        + escape(status_id)
        + '">\n'
    )
    tag = get(status, "tag")
    if truthy(tag):
        tag_params = tag if isinstance(tag, Params) else None
        parts.append(
            "      " + indent(trim(render_tag(tag_params)), 6, False) + "\n"
        )
    else:
        parts.append(
            "      " + content_indent(status, "html", "text", 6) + "\n"
        )
    parts.append("    </div>\n  </li>")
    return "".join(parts)
