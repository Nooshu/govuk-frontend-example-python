"""Build GOV.UK component option maps for each question page."""

from __future__ import annotations

from html import escape
from typing import Any

from govuk_components.rendering.params import Safe

from service.application import Application
from service.options import COUNTRIES, LICENCE_FEES, LICENCE_LENGTHS
from service.validate import FieldError


def error_summary(errors: list[FieldError]) -> dict[str, Any] | None:
    if not errors:
        return None
    return {
        "titleText": "There is a problem",
        "errorList": [{"text": err.text, "href": err.href} for err in errors],
    }


def name_field(application: Application, errors: list[FieldError]) -> dict[str, Any]:
    return {
        "fullName": _text_input(
            "full-name",
            "What is your full name?",
            application.full_name,
            errors,
            {
                "autocomplete": "name",
                "label": {
                    "text": "What is your full name?",
                    "isPageHeading": True,
                    "classes": "govuk-label--l",
                },
            },
        )
    }


def email_field(application: Application, errors: list[FieldError]) -> dict[str, Any]:
    return {
        "email": _text_input(
            "email",
            "What is your email address?",
            application.email,
            errors,
            {
                "type": "email",
                "autocomplete": "email",
                "spellcheck": False,
                "hint": {
                    "text": "This example stores the address in your browser session only."
                },
                "label": {
                    "text": "What is your email address?",
                    "isPageHeading": True,
                    "classes": "govuk-label--l",
                },
            },
        )
    }


def date_field(application: Application, errors: list[FieldError]) -> dict[str, Any]:
    date: dict[str, Any] = {
        "id": "date-of-birth",
        "namePrefix": "date-of-birth",
        "fieldset": {
            "legend": {
                "text": "What is your date of birth?",
                "isPageHeading": True,
                "classes": "govuk-fieldset__legend--l",
            }
        },
        "hint": {"text": "For example, 31 3 1980"},
        "items": [
            {"name": "day", "value": application.day},
            {"name": "month", "value": application.month},
            {"name": "year", "value": application.year},
        ],
    }
    _add_error(date, errors, "date-of-birth")
    return {"dateOfBirth": date}


def country_fields(application: Application, errors: list[FieldError]) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    for index, option in enumerate(COUNTRIES):
        item: dict[str, Any] = {
            "value": option.value,
            "text": option.text,
            "checked": application.country == option.value,
        }
        if index == 0:
            item["id"] = "country"
        items.append(item)
    radios: dict[str, Any] = {
        "idPrefix": "country",
        "name": "country",
        "fieldset": {
            "legend": {
                "text": "Where will you fish?",
                "isPageHeading": True,
                "classes": "govuk-fieldset__legend--l",
            }
        },
        "hint": {
            "text": "This example is fictional. It does not check a real fishing area."
        },
        "items": items,
    }
    _add_error(radios, errors, "country")
    return {"radios": radios}


def licence_fields(application: Application, errors: list[FieldError]) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    for index, option in enumerate(LICENCE_LENGTHS):
        item: dict[str, Any] = {
            "value": option.value,
            "text": option.text,
            "checked": application.licence_length == option.value,
        }
        if index == 0:
            item["id"] = "licence-length"
        items.append(item)
    radios: dict[str, Any] = {
        "idPrefix": "licence-length",
        "name": "licence-length",
        "fieldset": {
            "legend": {
                "text": "How long do you need the licence for?",
                "isPageHeading": True,
                "classes": "govuk-fieldset__legend--l",
            }
        },
        "items": items,
    }
    _add_error(radios, errors, "licence-length")
    return {"radios": radios}


def cookie_fields(choice: str, errors: list[FieldError]) -> dict[str, Any]:
    selected = ""
    if choice == "accept":
        selected = "yes"
    elif choice == "reject":
        selected = "no"
    radios: dict[str, Any] = {
        "idPrefix": "analytics",
        "name": "analytics",
        "fieldset": {
            "legend": {
                "text": "Do you want to accept analytics cookies?",
                "isPageHeading": True,
                "classes": "govuk-fieldset__legend--l",
            }
        },
        "hint": {
            "text": "This example stores your choice. It does not set analytics cookies."
        },
        "items": [
            {"value": "yes", "text": "Yes", "id": "analytics", "checked": selected == "yes"},
            {"value": "no", "text": "No", "checked": selected == "no"},
        ],
    }
    _add_error(radios, errors, "analytics")
    return {"radios": radios}


def fees_table() -> dict[str, Any]:
    rows = [
        [
            {"text": option.text},
            {"text": option.fee, "format": "numeric"},
        ]
        for option in LICENCE_FEES
    ]
    return {
        "caption": "Rod licence fees",
        "captionClasses": "govuk-table__caption--m",
        "firstCellIsHeader": True,
        "head": [
            {"text": "Licence"},
            {"text": "Fee", "format": "numeric"},
        ],
        "rows": rows,
    }


def help_accordion() -> dict[str, Any]:
    return {
        "id": "help",
        "items": [
            {
                "heading": {"text": "Who can apply"},
                "content": {
                    "text": (
                        "You can apply if you are 13 or over and you will fish "
                        "with a rod in England, Wales or Scotland."
                    )
                },
            },
            {
                "heading": {"text": "What a licence covers"},
                "content": {
                    "html": Safe(
                        '<ul class="govuk-list govuk-list--bullet">'
                        "<li>Rod and line fishing</li>"
                        "<li>Up to 2 rods where the licence allows it</li>"
                        "<li>The dates printed on your licence</li></ul>"
                    )
                },
            },
            {
                "heading": {"text": "If you need help to apply"},
                "content": {
                    "text": (
                        "You can ask someone to apply for you. "
                        "This example service does not offer a phone application line."
                    )
                },
            },
        ],
    }


def guidance_tabs() -> dict[str, Any]:
    return {
        "id": "guidance",
        "items": [
            {
                "label": "Before you apply",
                "id": "before-you-apply",
                "panel": {
                    "html": Safe(
                        '<h2 class="govuk-heading-l">Before you apply</h2>'
                        '<p class="govuk-body">You need how long you need the licence, '
                        "your name, date of birth, the country where you will fish, "
                        "and your email address.</p>"
                    )
                },
            },
            {
                "label": "Fees",
                "id": "fees",
                "panel": {
                    "html": Safe(
                        '<h2 class="govuk-heading-l">Fees</h2>'
                        '<p class="govuk-body">Fees depend on the length of the licence. '
                        '<a class="govuk-link" href="/fees">See licence fees</a>.</p>'
                    )
                },
            },
            {
                "label": "After you apply",
                "id": "after-you-apply",
                "panel": {
                    "html": Safe(
                        '<h2 class="govuk-heading-l">After you apply</h2>'
                        '<p class="govuk-body">This example shows a confirmation page with a '
                        "reference number. It does not send email and it does not take payment.</p>"
                    )
                },
            },
        ],
    }


def confirmation_panel(reference: str) -> dict[str, Any]:
    return {
        "titleText": "Application complete",
        "html": Safe(
            f"Your example reference number<br><strong>{escape(reference)}</strong>"
        ),
    }


def _text_input(
    field_id: str,
    label: str,
    value: str,
    errors: list[FieldError],
    extra: dict[str, Any],
) -> dict[str, Any]:
    field: dict[str, Any] = {
        "id": field_id,
        "name": field_id,
        "label": {"text": label},
        "value": value,
    }
    field.update(extra)
    _add_error(field, errors, field_id)
    return field


def _add_error(params: dict[str, Any], errors: list[FieldError], field: str) -> None:
    for err in errors:
        if err.field == field:
            params["errorMessage"] = {"text": err.text}
            return
