"""Hit remaining component renderer helper branches."""

from __future__ import annotations

from govuk_components.rendering.attributes import Attributes, attribute
from govuk_components.rendering.components_chrome import (
    render_footer,
    render_header,
    render_pagination,
    render_service_navigation,
)
from govuk_components.rendering.components_forms import (
    appended_attributes,
    render_character_count,
    render_checkboxes,
    render_date_input,
    render_file_upload,
    render_input,
    render_password_input,
    render_radios,
    render_select,
    render_textarea,
    slot_content,
)
from govuk_components.rendering.components_lists import (
    render_accordion,
    render_error_summary,
    render_notification_banner,
    render_summary_list,
    render_table,
    render_tabs,
    render_task_list,
)
from govuk_components.rendering.components_text import (
    render_details,
    render_inset_text,
    render_label,
    render_tag,
    render_warning_text,
)
from govuk_components.rendering.params import Params, Safe, new_params


def test_forms_helpers() -> None:
    assert "hi" in slot_content(new_params("text", "hi"), 0, True)
    assert "<b>" in slot_content(new_params("html", Safe("<b>x</b>")), 0, True)

    p = new_params(
        "name",
        "n",
        "id",
        "i",
        "maxlength",
        10,
        "formGroup",
        new_params("afterInput", new_params("html", Safe("<em>x</em>"))),
    )
    assert "em" in render_character_count(p)
    p2 = new_params(
        "name",
        "n",
        "id",
        "i",
        "maxlength",
        10,
        "formGroup",
        new_params("afterInput", new_params("text", "after")),
    )
    assert "after" in render_character_count(p2)

    assert 'data-x="1"' in appended_attributes(new_params("data-x", "1"))
    assert appended_attributes("x") == ""

    assert "govuk-input" in render_input(new_params("name", "n", "id", "i"))
    assert "govuk-file-upload" in render_file_upload(new_params("name", "f", "id", "f"))
    assert "govuk-textarea" in render_textarea(new_params("name", "t", "id", "t"))
    assert "govuk-password-input" in render_password_input(
        new_params("name", "p", "id", "p")
    )
    assert "govuk-radios" in render_radios(
        new_params(
            "name",
            "r",
            "items",
            [new_params("value", "a", "text", "A")],
        )
    )
    assert "govuk-checkboxes" in render_checkboxes(
        new_params(
            "name",
            "c",
            "items",
            [new_params("value", "a", "text", "A")],
        )
    )
    assert "govuk-select" in render_select(
        new_params(
            "name",
            "s",
            "id",
            "s",
            "items",
            [new_params("value", "a", "text", "A")],
        )
    )
    assert "govuk-date-input" in render_date_input(
        new_params("id", "d", "namePrefix", "d")
    )


def test_lists_chrome_text_helpers() -> None:
    assert "govuk-accordion" in render_accordion(
        new_params(
            "id",
            "a",
            "items",
            [new_params("heading", new_params("text", "H"), "content", new_params("text", "C"))],
        )
    )
    assert "govuk-error-summary" in render_error_summary(
        new_params("titleText", "T", "errorList", [new_params("text", "e", "href", "#")])
    )
    assert "govuk-notification-banner" in render_notification_banner(
        new_params("text", "n")
    )
    summary_row = new_params(
        "key", new_params("text", "k"), "value", new_params("text", "v")
    )
    assert "govuk-summary-list" in render_summary_list(new_params("rows", [summary_row]))
    assert "govuk-table" in render_table(
        new_params("rows", [[{"text": "a"}]])
    )
    assert "govuk-tabs" in render_tabs(
        new_params(
            "items",
            [new_params("label", "L", "id", "t1", "panel", new_params("text", "P"))],
        )
    )
    task_item = new_params(
        "title", new_params("text", "T"), "status", new_params("text", "S")
    )
    assert "govuk-task-list" in render_task_list(new_params("items", [task_item]))
    assert "govuk-header" in render_header(Params())
    assert "govuk-footer" in render_footer(Params())
    assert "govuk-pagination" in render_pagination(
        new_params("items", [new_params("number", 1, "href", "/", "current", True)])
    )
    assert "govuk-service-navigation" in render_service_navigation(
        new_params("serviceName", "S", "serviceUrl", "/")
    )
    assert "govuk-details" in render_details(new_params("summaryText", "S", "text", "B"))
    assert "govuk-inset-text" in render_inset_text(new_params("text", "I"))
    assert "govuk-label" in render_label(new_params("text", "L"))
    assert "govuk-tag" in render_tag(new_params("text", "T"))
    assert "govuk-warning-text" in render_warning_text(new_params("text", "W"))


def test_attributes_optional_and_safe_value() -> None:
    item = new_params("value", Safe("ok"), "optional", False)
    assert "ok" in attribute("data-z", item)
    empty = new_params("value", None, "optional", True)
    assert attribute("data-z", empty) == ""
    assert Attributes(123) == ""
