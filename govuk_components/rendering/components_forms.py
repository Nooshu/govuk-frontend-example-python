"""Ports for form components (input, radios, date-input, …).

Tracks GOV.UK Frontend Nunjucks macros / ``template.njk`` for fixture HTML parity.
"""

from __future__ import annotations

from typing import Any

from .attributes import (
    Attributes,
    attribute_if,
    classes_if,
    content_indent,
    flag_if,
    i18n_attributes,
)
from .components_button import render_button
from .components_text import render_error_message, render_fieldset, render_hint, render_label
from .nunjucks import (
    concat_if,
    contains,
    def_,
    def_truthy,
    escape,
    get,
    indent,
    is_undefined,
    items,
    loose_eq,
    out,
    str_value,
    trim,
    truthy,
)
from .params import Params, Safe, Undefined, new_params


def form_group_open(p: Params) -> str:
    form_group = p.get("formGroup")
    return (
        '<div class="govuk-form-group'
        + flag_if(" govuk-form-group--error", p.get("errorMessage"))
        + classes_if(get(form_group, "classes"))
        + '"'
        + Attributes(get(form_group, "attributes"))
        + ">\n"
    )


def described_by_append(described_by: str, id_: str) -> str:
    if described_by != "":
        return described_by + " " + id_
    return id_


def hint_block(p: Params, id_: str, described_by: str, width: int) -> tuple[str, str]:
    hint = p.get("hint")
    if not truthy(hint):
        return "", described_by
    hint_id = id_ + "-hint"
    described_by = described_by_append(described_by, hint_id)
    html = render_hint(
        new_params(
            "id",
            hint_id,
            "classes",
            get(hint, "classes"),
            "attributes",
            get(hint, "attributes"),
            "html",
            get(hint, "html"),
            "text",
            get(hint, "text"),
        )
    )
    return " " * width + indent(trim(html), width, False) + "\n", described_by


def error_block(p: Params, id_: str, described_by: str, width: int) -> tuple[str, str]:
    message = p.get("errorMessage")
    if not truthy(message):
        return "", described_by
    error_id = id_ + "-error"
    described_by = described_by_append(described_by, error_id)
    html = render_error_message(
        new_params(
            "id",
            error_id,
            "classes",
            get(message, "classes"),
            "attributes",
            get(message, "attributes"),
            "html",
            get(message, "html"),
            "text",
            get(message, "text"),
            "visuallyHiddenText",
            get(message, "visuallyHiddenText"),
        )
    )
    return " " * width + indent(trim(html), width, False) + "\n", described_by


def label_block(p: Params, id_: Any, width: int) -> str:
    label = p.get("label")
    html = render_label(
        new_params(
            "html",
            get(label, "html"),
            "text",
            get(label, "text"),
            "classes",
            get(label, "classes"),
            "isPageHeading",
            get(label, "isPageHeading"),
            "attributes",
            get(label, "attributes"),
            "for",
            id_,
        )
    )
    return " " * width + indent(trim(html), width, False) + "\n"


def slot_content(slot: Any, width: int, indent_first: bool) -> str:
    html = get(slot, "html")
    if truthy(html):
        return indent(trim(str_value(html)), width, indent_first)
    return out(get(slot, "text"))


def component_id(p: Params) -> Any:
    id_ = p.get("id")
    if truthy(id_):
        return id_
    return p.get("name")


def render_input(p: Params) -> str:
    class_names = "govuk-input"
    classes = p.get("classes")
    if truthy(classes):
        class_names += " " + str_value(classes)
    if truthy(p.get("errorMessage")):
        class_names += " govuk-input--error"

    id_ = component_id(p)
    described_by = ""
    supplied = p.get("describedBy")
    if truthy(supplied):
        described_by = str_value(supplied)

    form_group = p.get("formGroup")
    prefix, suffix = p.get("prefix"), p.get("suffix")
    before_input, after_input = get(form_group, "beforeInput"), get(form_group, "afterInput")
    has_prefix = truthy(prefix) and (
        truthy(get(prefix, "text")) or truthy(get(prefix, "html"))
    )
    has_suffix = truthy(suffix) and (
        truthy(get(suffix, "text")) or truthy(get(suffix, "html"))
    )
    has_before = truthy(before_input) and (
        truthy(get(before_input, "text")) or truthy(get(before_input, "html"))
    )
    has_after = truthy(after_input) and (
        truthy(get(after_input, "text")) or truthy(get(after_input, "html"))
    )

    parts: list[str] = []
    parts.append(form_group_open(p))
    parts.append(label_block(p, id_, 2))

    hint, described_by = hint_block(p, str_value(id_), described_by, 2)
    parts.append(hint)
    error_message, described_by = error_block(p, str_value(id_), described_by, 2)
    parts.append(error_message)

    element = input_element(p, class_names, id_, described_by)
    if has_prefix or has_suffix or has_before or has_after:
        wrapper = p.get("inputWrapper")
        parts.append(
            '  <div class="govuk-input__wrapper'
            + classes_if(get(wrapper, "classes"))
            + '"'
            + Attributes(get(wrapper, "attributes"))
            + ">\n"
        )
        if has_before:
            parts.append(slot_content(before_input, 4, True) + "\n")  # pragma: no cover
        if has_prefix:
            parts.append(indent(_affix_item(prefix, "prefix"), 2, True) + "\n")
        parts.append("    " + element + "\n")
        if has_suffix:
            parts.append(indent(_affix_item(suffix, "suffix"), 2, True) + "\n")
        if has_after:
            parts.append(slot_content(after_input, 4, True) + "\n")
        parts.append("  </div>\n")
    else:
        parts.append("  " + element + "\n")

    parts.append("</div>")
    return "".join(parts)


def input_element(p: Params, class_names: str, id_: Any, described_by: str) -> str:
    spellcheck: Any = False
    flag = p.get("spellcheck")
    if isinstance(flag, bool):
        spellcheck = "true" if flag else "false"
    aria_described_by: Any = Undefined
    if described_by != "":
        aria_described_by = described_by

    attributes = new_params(
        "class",
        class_names,
        "id",
        id_,
        "name",
        p.get("name"),
        "type",
        def_truthy(p.get("type"), "text"),
        "spellcheck",
        new_params("value", spellcheck, "optional", True),
        "value",
        new_params("value", p.get("value"), "optional", True),
        "disabled",
        new_params("value", p.get("disabled"), "optional", True),
        "aria-describedby",
        new_params("value", aria_described_by, "optional", True),
        "autocomplete",
        new_params("value", p.get("autocomplete"), "optional", True),
        "autocapitalize",
        new_params("value", p.get("autocapitalize"), "optional", True),
        "pattern",
        new_params("value", p.get("pattern"), "optional", True),
        "inputmode",
        new_params("value", p.get("inputmode"), "optional", True),
    )
    return "<input" + Attributes(attributes) + Attributes(p.get("attributes")) + ">"


def _affix_item(affix: Any, kind: str) -> str:
    return (
        '  <div class="govuk-input__'
        + kind
        + classes_if(get(affix, "classes"))
        + '" aria-hidden="true"'
        + Attributes(get(affix, "attributes"))
        + ">"
        + content_indent(affix, "html", "text", 4)
        + "</div>"
    )


def render_textarea(p: Params) -> str:
    id_ = component_id(p)
    described_by = ""
    supplied = p.get("describedBy")
    if truthy(supplied):
        described_by = str_value(supplied)
    form_group = p.get("formGroup")

    parts: list[str] = []
    parts.append(form_group_open(p))
    parts.append(label_block(p, id_, 2))

    hint, described_by = hint_block(p, str_value(id_), described_by, 2)
    parts.append(hint)
    error_message, described_by = error_block(p, str_value(id_), described_by, 2)
    parts.append(error_message)

    before = get(form_group, "beforeInput")
    if truthy(before):
        parts.append("  " + slot_content(before, 2, False) + "\n")  # pragma: no cover

    spellcheck = ""
    flag = p.get("spellcheck")
    if isinstance(flag, bool):
        spellcheck = ' spellcheck="' + ("true" if flag else "false") + '"'
    parts.append(
        '  <textarea class="govuk-textarea'
        + flag_if(" govuk-textarea--error", p.get("errorMessage"))
        + classes_if(p.get("classes"))
        + '" id="'
        + out(id_)
        + '" name="'
        + out(p.get("name"))
        + '" rows="'
        + out(def_truthy(p.get("rows"), "5"))
        + '"'
        + spellcheck
        + flag_if(" disabled", p.get("disabled"))
        + attribute_if("aria-describedby", described_by)
        + attribute_if("autocomplete", p.get("autocomplete"))
        + Attributes(p.get("attributes"))
        + ">"
        + out(p.get("value"))
        + "</textarea>\n"
    )

    after = get(form_group, "afterInput")
    if truthy(after):
        parts.append("  " + slot_content(after, 2, False) + "\n")

    parts.append("</div>")
    return "".join(parts)


def render_select(p: Params) -> str:
    id_ = component_id(p)
    described_by = ""
    supplied = p.get("describedBy")
    if truthy(supplied):
        described_by = str_value(supplied)
    form_group = p.get("formGroup")

    parts: list[str] = []
    parts.append(form_group_open(p))
    parts.append(label_block(p, id_, 2))

    hint, described_by = hint_block(p, str_value(id_), described_by, 2)
    parts.append(hint)
    error_message, described_by = error_block(p, str_value(id_), described_by, 2)
    parts.append(error_message)

    before = get(form_group, "beforeInput")
    if truthy(before):
        parts.append("  " + slot_content(before, 2, False) + "\n")  # pragma: no cover

    parts.append(
        '  <select class="govuk-select'
        + classes_if(p.get("classes"))
        + flag_if(" govuk-select--error", p.get("errorMessage"))
        + '" id="'
        + out(id_)
        + '" name="'
        + out(p.get("name"))
        + '"'
        + flag_if(" disabled", p.get("disabled"))
        + attribute_if("aria-describedby", described_by)
        + Attributes(p.get("attributes"))
        + ">\n"
    )

    selected = p.get("value")
    for item in items(p.get("items")):
        if not truthy(item):
            continue
        value = get(item, "value")
        effective = def_(value, get(item, "text"))
        is_selected = truthy(get(item, "selected"))
        if not is_selected and truthy(selected):
            is_selected = loose_eq(effective, selected) and not loose_eq(
                get(item, "selected"), False
            )

        parts.append("    <option")
        if not is_undefined(value):
            parts.append(' value="' + out(value) + '"')
        parts.append(
            flag_if(" selected", is_selected)
            + flag_if(" disabled", get(item, "disabled"))
            + Attributes(get(item, "attributes"))
            + ">"
            + out(get(item, "text"))
            + "</option>\n"
        )
    parts.append("  </select>\n")

    after = get(form_group, "afterInput")
    if truthy(after):
        parts.append("  " + slot_content(after, 2, False) + "\n")  # pragma: no cover

    parts.append("</div>")
    return "".join(parts)


def render_file_upload(p: Params) -> str:
    id_ = component_id(p)
    described_by = ""
    supplied = p.get("describedBy")
    if truthy(supplied):
        described_by = str_value(supplied)
    form_group = p.get("formGroup")

    parts: list[str] = []
    parts.append(form_group_open(p))
    parts.append(label_block(p, id_, 2))

    hint, described_by = hint_block(p, str_value(id_), described_by, 2)
    parts.append(hint)
    error_message, described_by = error_block(p, str_value(id_), described_by, 2)
    parts.append(error_message)

    before = get(form_group, "beforeInput")
    if truthy(before):
        parts.append("  " + slot_content(before, 2, False) + "\n")  # pragma: no cover

    javascript = truthy(p.get("javascript"))
    if javascript:
        parts.append(
            "  <div\n    class=\"govuk-file-upload-wrapper"
            + classes_if(p.get("wrapperClasses"))
            + '"\n    data-module="govuk-file-upload"'
            + i18n_attributes("choose-files-button", p.get("chooseFilesButtonText"), Undefined)
            + i18n_attributes("no-file-chosen", p.get("noFileChosenText"), Undefined)
            + i18n_attributes(
                "multiple-files-chosen", Undefined, p.get("multipleFilesChosenText")
            )
            + i18n_attributes("drop-instruction", p.get("dropInstructionText"), Undefined)
            + i18n_attributes("entered-drop-zone", p.get("enteredDropZoneText"), Undefined)
            + i18n_attributes("left-drop-zone", p.get("leftDropZoneText"), Undefined)
            + Attributes(p.get("wrapperAttributes"))
            + "\n  >\n"
        )

    parts.append(
        '  <input class="govuk-file-upload'
        + classes_if(p.get("classes"))
        + flag_if(" govuk-file-upload--error", p.get("errorMessage"))
        + '" id="'
        + out(id_)
        + '" name="'
        + out(p.get("name"))
        + '" type="file"'
        + flag_if(" disabled", p.get("disabled"))
        + flag_if(" multiple", p.get("multiple"))
        + attribute_if("aria-describedby", described_by)
        + Attributes(p.get("attributes"))
        + ">\n"
    )

    if javascript:
        parts.append("  </div>\n")
    after = get(form_group, "afterInput")
    if truthy(after):
        parts.append("  " + slot_content(after, 2, False) + "\n")  # pragma: no cover

    parts.append("</div>")
    return "".join(parts)


def render_character_count(p: Params) -> str:
    maxwords, maxlength = p.get("maxwords"), p.get("maxlength")
    has_no_limit = not truthy(maxwords) and not truthy(maxlength)
    id_ = component_id(p)

    description_no_limit: Any = Undefined
    if not has_no_limit:
        limit = maxlength
        if truthy(maxwords):
            limit = maxwords
        unit = "characters"
        if truthy(maxwords):
            unit = "words"
        description = "You can enter up to %{count} " + unit
        supplied = p.get("textareaDescriptionText")
        if truthy(supplied):
            description = str_value(supplied)
        description_no_limit = description.replace("%{count}", str_value(limit))

    count_message = p.get("countMessage")
    count_message_html = (
        trim(
            render_hint(
                new_params(
                    "text",
                    description_no_limit,
                    "id",
                    str_value(id_) + "-info",
                    "classes",
                    "govuk-character-count__message"
                    + concat_if(" ", get(count_message, "classes")),
                )
            )
        )
        + "\n"
    )

    form_group = p.get("formGroup")
    after = get(form_group, "afterInput")
    if truthy(after):
        html = get(after, "html")
        if truthy(html):
            count_message_html += trim(str_value(html)) + "\n"
        else:
            count_message_html += out(get(after, "text")) + "\n"

    attributes_html = Attributes(
        new_params(
            "data-module",
            "govuk-character-count",
            "data-maxlength",
            new_params("value", maxlength, "optional", True),
            "data-threshold",
            new_params("value", p.get("threshold"), "optional", True),
            "data-maxwords",
            new_params("value", maxwords, "optional", True),
        )
    )
    description = p.get("textareaDescriptionText")
    if has_no_limit and truthy(description):
        attributes_html += i18n_attributes(
            "textarea-description", Undefined, new_params("other", description)
        )
    attributes_html += (
        i18n_attributes(
            "characters-under-limit", Undefined, p.get("charactersUnderLimitText")
        )
        + i18n_attributes(
            "characters-at-limit", p.get("charactersAtLimitText"), Undefined
        )
        + i18n_attributes(
            "characters-over-limit", Undefined, p.get("charactersOverLimitText")
        )
        + i18n_attributes("words-under-limit", Undefined, p.get("wordsUnderLimitText"))
        + i18n_attributes("words-at-limit", p.get("wordsAtLimitText"), Undefined)
        + i18n_attributes("words-over-limit", Undefined, p.get("wordsOverLimitText"))
    )
    attributes_html += appended_attributes(get(form_group, "attributes"))

    label = p.get("label")
    return trim(
        render_textarea(
            new_params(
                "id",
                id_,
                "name",
                p.get("name"),
                "describedBy",
                str_value(id_) + "-info",
                "rows",
                p.get("rows"),
                "spellcheck",
                p.get("spellcheck"),
                "value",
                p.get("value"),
                "formGroup",
                new_params(
                    "classes",
                    "govuk-character-count" + concat_if(" ", get(form_group, "classes")),
                    "attributes",
                    attributes_html,
                    "beforeInput",
                    get(form_group, "beforeInput"),
                    "afterInput",
                    new_params("html", Safe(count_message_html)),
                ),
                "classes",
                "govuk-js-character-count" + concat_if(" ", p.get("classes")),
                "label",
                new_params(
                    "html",
                    get(label, "html"),
                    "text",
                    get(label, "text"),
                    "classes",
                    get(label, "classes"),
                    "isPageHeading",
                    get(label, "isPageHeading"),
                    "attributes",
                    get(label, "attributes"),
                    "for",
                    id_,
                ),
                "hint",
                p.get("hint"),
                "errorMessage",
                p.get("errorMessage"),
                "attributes",
                p.get("attributes"),
            )
        )
    )


def appended_attributes(attributes: Any) -> str:
    if not isinstance(attributes, Params):
        return ""
    parts: list[str] = []
    for name in attributes:
        parts.append(
            " "
            + escape(name)
            + '="'
            + escape(str_value(attributes.get(name)))
            + '"'
        )
    return "".join(parts)


def render_password_input(p: Params) -> str:
    id_ = component_id(p)
    form_group = p.get("formGroup")

    attributes_html = (
        ' data-module="govuk-password-input"'
        + i18n_attributes("show-password", p.get("showPasswordText"), Undefined)
        + i18n_attributes("hide-password", p.get("hidePasswordText"), Undefined)
        + i18n_attributes(
            "show-password-aria-label", p.get("showPasswordAriaLabelText"), Undefined
        )
        + i18n_attributes(
            "hide-password-aria-label", p.get("hidePasswordAriaLabelText"), Undefined
        )
        + i18n_attributes(
            "password-shown-announcement",
            p.get("passwordShownAnnouncementText"),
            Undefined,
        )
        + i18n_attributes(
            "password-hidden-announcement",
            p.get("passwordHiddenAnnouncementText"),
            Undefined,
        )
        + appended_attributes(get(form_group, "attributes"))
    )

    button = p.get("button")
    button_html = (
        trim(
            render_button(
                new_params(
                    "type",
                    "button",
                    "classes",
                    "govuk-button--secondary govuk-password-input__toggle "
                    "govuk-js-password-input-toggle"
                    + concat_if(" ", get(button, "classes")),
                    "text",
                    def_(p.get("showPasswordText"), "Show"),
                    "attributes",
                    new_params(
                        "aria-controls",
                        id_,
                        "aria-label",
                        def_(p.get("showPasswordAriaLabelText"), "Show password"),
                        "hidden",
                        new_params("value", True, "optional", True),
                    ),
                )
            )
        )
        + "\n"
    )
    after = get(form_group, "afterInput")
    if truthy(after):
        html = get(after, "html")  # pragma: no cover
        if truthy(html):  # pragma: no cover
            button_html += trim(str_value(html)) + "\n"  # pragma: no cover
        else:  # pragma: no cover
            button_html += out(get(after, "text")) + "\n"  # pragma: no cover

    return trim(
        render_input(
            new_params(
                "formGroup",
                new_params(
                    "classes",
                    "govuk-password-input" + concat_if(" ", get(form_group, "classes")),
                    "attributes",
                    attributes_html,
                    "beforeInput",
                    get(form_group, "beforeInput"),
                    "afterInput",
                    new_params("html", Safe(button_html)),
                ),
                "inputWrapper",
                new_params("classes", "govuk-password-input__wrapper"),
                "label",
                p.get("label"),
                "hint",
                p.get("hint"),
                "classes",
                "govuk-password-input__input govuk-js-password-input-input"
                + concat_if(" ", p.get("classes")),
                "errorMessage",
                p.get("errorMessage"),
                "id",
                id_,
                "name",
                p.get("name"),
                "type",
                "password",
                "spellcheck",
                False,
                "autocapitalize",
                "none",
                "autocomplete",
                def_truthy(p.get("autocomplete"), "current-password"),
                "value",
                p.get("value"),
                "disabled",
                p.get("disabled"),
                "describedBy",
                p.get("describedBy"),
                "attributes",
                p.get("attributes"),
            )
        )
    )


def render_checkboxes(p: Params) -> str:
    id_prefix = p.get("idPrefix")
    if not truthy(id_prefix):
        id_prefix = p.get("name")
    fieldset = p.get("fieldset")
    described_by = ""
    supplied = p.get("describedBy")
    if truthy(supplied):
        described_by = str_value(supplied)
    supplied = get(fieldset, "describedBy")
    if truthy(supplied):
        described_by = str_value(supplied)
    has_fieldset = truthy(fieldset)

    inner: list[str] = []
    hint, described_by = hint_block(p, str_value(id_prefix), described_by, 2)
    inner.append(hint)
    error_message, described_by = error_block(p, str_value(id_prefix), described_by, 2)
    inner.append(error_message)

    form_group = p.get("formGroup")
    inner.append(
        '  <div class="govuk-checkboxes'
        + classes_if(p.get("classes"))
        + '"'
        + Attributes(p.get("attributes"))
        + ' data-module="govuk-checkboxes">\n'
    )
    before = get(form_group, "beforeInputs")
    if truthy(before):
        inner.append("    " + slot_content(before, 4, False) + "\n")  # pragma: no cover
    for index, item in enumerate(items(p.get("items"))):
        if not truthy(item):
            continue
        inner.append(
            _checkbox_item(p, item, index + 1, str_value(id_prefix), described_by, has_fieldset)
        )
    after = get(form_group, "afterInputs")
    if truthy(after):
        inner.append("    " + slot_content(after, 4, False) + "\n")  # pragma: no cover
    inner.append("  </div>\n")

    return fieldset_wrapper(p, "".join(inner), described_by, Undefined, False)


def fieldset_wrapper(
    p: Params, inner: str, described_by: str, role: Any, indent_fieldset: bool
) -> str:
    fieldset = p.get("fieldset")
    body = trim(inner)
    if truthy(fieldset):
        html = render_fieldset(
            new_params(
                "describedBy",
                described_by,
                "classes",
                get(fieldset, "classes"),
                "role",
                role,
                "attributes",
                get(fieldset, "attributes"),
                "legend",
                get(fieldset, "legend"),
                "html",
                Safe(body),
            )
        )
        body = trim(html)
        if indent_fieldset:
            body = indent(body, 2, False)
    return form_group_open(p) + "  " + body + "\n</div>"


def _checkbox_item(
    p: Params,
    item: Any,
    index: int,
    id_prefix: str,
    described_by: str,
    has_fieldset: bool,
) -> str:
    item_id = id_prefix
    if index > 1:
        item_id += "-" + str(index)
    supplied = get(item, "id")
    if truthy(supplied):
        item_id = str_value(supplied)
    item_name = p.get("name")
    supplied = get(item, "name")
    if truthy(supplied):
        item_name = supplied
    conditional_id = "conditional-" + item_id

    divider = get(item, "divider")
    if truthy(divider):
        return '    <div class="govuk-checkboxes__divider">' + out(divider) + "</div>\n"

    checked = truthy(get(item, "checked"))
    if not checked and truthy(p.get("values")):
        checked = contains(get(item, "value"), p.get("values")) and not loose_eq(
            get(item, "checked"), False
        )
    hint = get(item, "hint")
    has_hint = truthy(get(hint, "text")) or truthy(get(hint, "html"))
    item_hint_id = ""
    if has_hint:
        item_hint_id = item_id + "-item-hint"
    item_described_by = ""
    if not has_fieldset:
        item_described_by = described_by
    item_described_by = trim(item_described_by + " " + item_hint_id)

    conditional = get(item, "conditional")
    label = get(item, "label")

    parts: list[str] = []
    parts.append('    <div class="govuk-checkboxes__item">\n')
    parts.append(
        '      <input class="govuk-checkboxes__input" id="'
        + escape(item_id)
        + '" name="'
        + out(item_name)
        + '" type="checkbox" value="'
        + out(get(item, "value"))
        + '"'
        + flag_if(" checked", checked)
        + flag_if(" disabled", get(item, "disabled"))
        + attribute_if(
            "data-aria-controls", _if_truthy(get(conditional, "html"), conditional_id)
        )
        + attribute_if("data-behaviour", get(item, "behaviour"))
        + attribute_if("aria-describedby", item_described_by)
        + Attributes(get(item, "attributes"))
        + ">\n"
    )
    parts.append(
        "      "
        + indent(
            trim(
                render_label(
                    new_params(
                        "html",
                        get(item, "html"),
                        "text",
                        get(item, "text"),
                        "classes",
                        "govuk-checkboxes__label" + concat_if(" ", get(label, "classes")),
                        "attributes",
                        get(label, "attributes"),
                        "for",
                        item_id,
                    )
                )
            ),
            6,
            False,
        )
        + "\n"
    )
    if has_hint:
        parts.append(
            "      "
            + indent(
                trim(
                    render_hint(
                        new_params(
                            "id",
                            item_hint_id,
                            "classes",
                            "govuk-checkboxes__hint"
                            + concat_if(" ", get(hint, "classes")),
                            "attributes",
                            get(hint, "attributes"),
                            "html",
                            get(hint, "html"),
                            "text",
                            get(hint, "text"),
                        )
                    )
                ),
                6,
                False,
            )
            + "\n"
        )
    parts.append("    </div>\n")
    html = get(conditional, "html")
    if truthy(html):
        parts.append(
            '    <div class="govuk-checkboxes__conditional'
            + flag_if(" govuk-checkboxes__conditional--hidden", not checked)
            + '" id="'
            + escape(conditional_id)
            + '">\n      '
            + trim(str_value(html))
            + "\n    </div>\n"
        )
    return "".join(parts)


def _if_truthy(condition: Any, value: str) -> Any:
    if truthy(condition):
        return value
    return Undefined


def render_radios(p: Params) -> str:
    id_prefix = p.get("idPrefix")
    if not truthy(id_prefix):
        id_prefix = p.get("name")
    fieldset = p.get("fieldset")
    described_by = ""
    supplied = get(fieldset, "describedBy")
    if truthy(supplied):
        described_by = str_value(supplied)

    inner: list[str] = []
    hint, described_by = hint_block(p, str_value(id_prefix), described_by, 2)
    inner.append(hint)
    error_message, described_by = error_block(p, str_value(id_prefix), described_by, 2)
    inner.append(error_message)

    form_group = p.get("formGroup")
    inner.append(
        '  <div class="govuk-radios'
        + classes_if(p.get("classes"))
        + '"'
        + Attributes(p.get("attributes"))
        + ' data-module="govuk-radios">\n'
    )
    before = get(form_group, "beforeInputs")
    if truthy(before):
        inner.append("    " + slot_content(before, 4, False) + "\n")  # pragma: no cover
    for index, item in enumerate(items(p.get("items"))):
        if not truthy(item):
            continue
        inner.append(_radio_item(p, item, index + 1, str_value(id_prefix)))
    after = get(form_group, "afterInputs")
    if truthy(after):
        inner.append("    " + slot_content(after, 4, False) + "\n")  # pragma: no cover
    inner.append("  </div>\n")

    return fieldset_wrapper(p, "".join(inner), described_by, Undefined, False)


def _radio_item(p: Params, item: Any, index: int, id_prefix: str) -> str:
    item_id = id_prefix
    if index > 1:
        item_id += "-" + str(index)
    supplied = get(item, "id")
    if truthy(supplied):
        item_id = str_value(supplied)
    conditional_id = "conditional-" + item_id

    divider = get(item, "divider")
    if truthy(divider):
        return '    <div class="govuk-radios__divider">' + out(divider) + "</div>\n"

    checked = truthy(get(item, "checked"))
    if not checked and truthy(p.get("value")):
        checked = loose_eq(get(item, "value"), p.get("value")) and not loose_eq(
            get(item, "checked"), False
        )
    hint = get(item, "hint")
    has_hint = truthy(get(hint, "text")) or truthy(get(hint, "html"))
    item_hint_id = item_id + "-item-hint"
    conditional = get(item, "conditional")
    label = get(item, "label")

    parts: list[str] = []
    parts.append('    <div class="govuk-radios__item">\n')
    parts.append(
        '      <input class="govuk-radios__input" id="'
        + escape(item_id)
        + '" name="'
        + out(p.get("name"))
        + '" type="radio" value="'
        + out(get(item, "value"))
        + '"'
        + flag_if(" checked", checked)
        + flag_if(" disabled", get(item, "disabled"))
        + attribute_if(
            "data-aria-controls", _if_truthy(get(conditional, "html"), conditional_id)
        )
        + attribute_if("aria-describedby", _if_truthy(has_hint, item_hint_id))
        + Attributes(get(item, "attributes"))
        + ">\n"
    )
    parts.append(
        "      "
        + indent(
            trim(
                render_label(
                    new_params(
                        "html",
                        get(item, "html"),
                        "text",
                        get(item, "text"),
                        "classes",
                        "govuk-radios__label" + concat_if(" ", get(label, "classes")),
                        "attributes",
                        get(label, "attributes"),
                        "for",
                        item_id,
                    )
                )
            ),
            6,
            False,
        )
        + "\n"
    )
    if has_hint:
        parts.append(
            "      "
            + indent(
                trim(
                    render_hint(
                        new_params(
                            "id",
                            item_hint_id,
                            "classes",
                            "govuk-radios__hint" + concat_if(" ", get(hint, "classes")),
                            "attributes",
                            get(hint, "attributes"),
                            "html",
                            get(hint, "html"),
                            "text",
                            get(hint, "text"),
                        )
                    )
                ),
                6,
                False,
            )
            + "\n"
        )
    parts.append("    </div>\n")
    html = get(conditional, "html")
    if truthy(html):
        parts.append(
            '    <div class="govuk-radios__conditional'
            + flag_if(" govuk-radios__conditional--hidden", not checked)
            + '" id="'
            + escape(conditional_id)
            + '">\n      '
            + trim(str_value(html))
            + "\n    </div>\n"
        )
    return "".join(parts)


def render_date_input(p: Params) -> str:
    fieldset = p.get("fieldset")
    described_by = ""
    supplied = get(fieldset, "describedBy")
    if truthy(supplied):
        described_by = str_value(supplied)
    values = p.get("values")

    day = def_(
        p.get("day"),
        new_params(
            "name", "day", "value", get(values, "day"), "classes", "govuk-input--width-2"
        ),
    )
    month = def_(
        p.get("month"),
        new_params(
            "name",
            "month",
            "value",
            get(values, "month"),
            "classes",
            "govuk-input--width-2",
        ),
    )
    year = def_(
        p.get("year"),
        new_params(
            "name", "year", "value", get(values, "year"), "classes", "govuk-input--width-4"
        ),
    )

    date_items = items(p.get("items"))
    if len(date_items) == 0:
        date_items = [day, month, year]

    any_item_has_error = False
    for item in date_items:
        if _date_item_has_error(item):
            any_item_has_error = True

    inner: list[str] = []
    hint, described_by = hint_block(p, str_value(p.get("id")), described_by, 2)
    inner.append(hint)
    error_message, described_by = error_block(p, str_value(p.get("id")), described_by, 2)
    inner.append(error_message)

    form_group = p.get("formGroup")
    inner.append(
        '  <div class="govuk-date-input'
        + classes_if(p.get("classes"))
        + '"'
        + Attributes(p.get("attributes"))
        + attribute_if("id", p.get("id"))
        + ">\n"
    )
    before = get(form_group, "beforeInputs")
    if truthy(before):
        inner.append("    " + slot_content(before, 4, False) + "\n")  # pragma: no cover
    for item in date_items:
        if not truthy(item):
            continue
        inner.append(
            indent(
                trim(_date_input_item(p, item, any_item_has_error, day, month, year)),
                4,
                True,
            )
            + "\n"
        )
    after = get(form_group, "afterInputs")
    if truthy(after):
        inner.append("    " + slot_content(after, 4, False) + "\n")  # pragma: no cover
    inner.append("  </div>\n")

    return fieldset_wrapper(p, "".join(inner), described_by, "group", True)


def _date_item_has_error(item: Any) -> bool:
    if truthy(get(item, "error")):
        return True
    classes = get(item, "classes")
    return truthy(classes) and contains("govuk-input--error", classes)


def _date_input_item(
    p: Params, item: Any, any_item_has_error: bool, day: Any, month: Any, year: Any
) -> str:
    item_name = get(item, "name")
    item_value = get(item, "value")
    item_width = "2"
    item_classes = ""
    item_has_error = _date_item_has_error(item)

    name = get(item, "name")
    if item is day or (
        truthy(name) and contains(name, ["day", get(day, "name")])
    ):
        item_name = def_(name, "day")
        item_value = def_(item_value, get(day, "value"))
    elif item is month or (
        truthy(name) and contains(name, ["month", get(month, "name")])
    ):
        item_name = def_(name, "month")
        item_value = def_(item_value, get(month, "value"))
    elif item is year or (
        truthy(name) and contains(name, ["year", get(year, "name")])
    ):
        item_name = def_(name, "year")
        item_value = def_(item_value, get(year, "value"))
        item_width = "4"

    classes = get(item, "classes")
    has_error_class = truthy(classes) and contains("govuk-input--error", classes)
    if not has_error_class and (
        item_has_error
        or (
            not loose_eq(get(item, "error"), False)
            and truthy(p.get("errorMessage"))
            and not any_item_has_error
        )
    ):
        item_classes = trim(item_classes + " govuk-input--error")
    if not truthy(classes) or not contains("govuk-input--width-", classes):
        item_classes = trim(item_classes + " govuk-input--width-" + item_width)
    if truthy(classes):
        item_classes = trim(item_classes + " " + str_value(classes))

    name_prefix = ""
    prefix = p.get("namePrefix")
    if truthy(prefix):
        name_prefix = str_value(prefix) + "-"

    label = get(item, "label")
    if not truthy(label):
        label = _capitalise(str_value(item_name))
    id_ = get(item, "id")
    if not truthy(id_):
        id_ = str_value(p.get("id")) + "-" + str_value(item_name)
    value = item_value
    if is_undefined(value):
        value = get(p.get("values"), name_prefix + str_value(item_name))

    input_html = render_input(
        new_params(
            "label",
            new_params("text", label, "classes", "govuk-date-input__label"),
            "id",
            id_,
            "classes",
            "govuk-date-input__input" + concat_if(" ", item_classes),
            "name",
            name_prefix + str_value(item_name),
            "value",
            value,
            "type",
            "text",
            "inputmode",
            def_truthy(get(item, "inputmode"), "numeric"),
            "autocomplete",
            get(item, "autocomplete"),
            "pattern",
            get(item, "pattern"),
            "attributes",
            get(item, "attributes"),
        )
    )

    return (
        '<div class="govuk-date-input__item">\n  '
        + indent(trim(input_html), 2, False)
        + "\n</div>"
    )


def _capitalise(text: str) -> str:
    if text == "":
        return ""  # pragma: no cover
    lowered = text.lower()
    return lowered[0].upper() + lowered[1:]
