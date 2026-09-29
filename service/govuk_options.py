"""Build GOV.UK component option maps for each question page."""

from __future__ import annotations

from datetime import datetime
from html import escape
from typing import Any

from govuk_components.rendering import MustRender
from govuk_components.rendering.params import Safe, params_from_mapping

from service.application import (
    CONTACT_BY_TELEPHONE,
    NOT_SURE,
    Application,
)
from service.options import (
    CONTACT_OPTIONS,
    LICENCE_LENGTHS,
    REGIONS,
    start_months,
)
from service.validate import FieldError


def error_summary(errors: list[FieldError]) -> dict[str, Any] | None:
    if not errors:
        return None
    return {
        "titleText": "There is a problem",
        "errorList": [{"text": err.text, "href": err.href} for err in errors],
    }


def name_fields(application: Application, errors: list[FieldError]) -> dict[str, Any]:
    return {
        "firstName": _text_input(
            "first-name",
            "First name",
            application.first_name,
            errors,
            {"autocomplete": "given-name", "classes": "govuk-input--width-20", "spellcheck": False},
        ),
        "lastName": _text_input(
            "last-name",
            "Last name",
            application.last_name,
            errors,
            {
                "autocomplete": "family-name",
                "classes": "govuk-input--width-20",
                "spellcheck": False,
            },
        ),
    }


def email_field(application: Application, errors: list[FieldError]) -> dict[str, Any]:
    return {
        "email": _text_input(
            "email",
            "Email address",
            application.email,
            errors,
            {
                "type": "email",
                "autocomplete": "email",
                "spellcheck": False,
                "classes": "govuk-input--width-20",
                "hint": {"text": "We will send the decision to this address"},
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
            {"name": "day", "autocomplete": "bday-day", "value": application.day},
            {"name": "month", "autocomplete": "bday-month", "value": application.month},
            {"name": "year", "autocomplete": "bday-year", "value": application.year},
        ],
    }
    _add_error(date, errors, "date-of-birth")
    return {"dateOfBirth": date}


def contact_fields(application: Application, errors: list[FieldError]) -> dict[str, Any]:
    telephone = _text_input(
        "telephone",
        "Telephone number",
        application.telephone,
        errors,
        {"type": "tel", "autocomplete": "tel", "classes": "govuk-input--width-20"},
    )
    conditional = MustRender("input", params_from_mapping(telephone))
    items: list[dict[str, Any]] = []
    for option in CONTACT_OPTIONS:
        if option.value == CONTACT_BY_TELEPHONE:
            items.append(
                {
                    "value": option.value,
                    "text": option.text,
                    "checked": application.contact_by == CONTACT_BY_TELEPHONE,
                    "conditional": {"html": Safe(conditional)},
                }
            )
            continue
        items.append(
            {
                "value": option.value,
                "text": option.text,
                "id": "contact-by",
                "checked": application.contact_by == option.value,
            }
        )
    radios: dict[str, Any] = {
        "idPrefix": "contact-by",
        "name": "contact-by",
        "fieldset": {
            "legend": {
                "text": "How should we contact you?",
                "isPageHeading": True,
                "classes": "govuk-fieldset__legend--l",
            }
        },
        "hint": {"text": "We will use this if we need to ask about your application"},
        "items": items,
    }
    _add_error(radios, errors, "contact-by")
    return {"radios": radios}


def region_fields(application: Application, errors: list[FieldError]) -> dict[str, Any]:
    chosen = set(application.regions)
    items: list[dict[str, Any]] = []
    for index, region in enumerate(REGIONS):
        item: dict[str, Any] = {
            "value": region.value,
            "text": region.text,
            "checked": region.value in chosen,
        }
        if index == 0:
            item["id"] = "regions"
        items.append(item)
    items.append({"divider": "or"})
    items.append(
        {
            "value": NOT_SURE,
            "text": "I have not decided yet",
            "behaviour": "exclusive",
            "checked": NOT_SURE in chosen,
        }
    )
    checkboxes: dict[str, Any] = {
        "idPrefix": "where",
        "name": "regions",
        "fieldset": {
            "legend": {
                "text": "Where will you fish?",
                "isPageHeading": True,
                "classes": "govuk-fieldset__legend--l",
            }
        },
        "hint": {"text": "Select all that apply"},
        "items": items,
    }
    _add_error(checkboxes, errors, "regions")
    return {"checkboxes": checkboxes}


def licence_fields(application: Application, errors: list[FieldError]) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    for index, option in enumerate(LICENCE_LENGTHS):
        item: dict[str, Any] = {
            "value": option.value,
            "text": f"{option.text} ({option.fee})",
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
                "text": "How long do you need a licence for?",
                "isPageHeading": True,
                "classes": "govuk-fieldset__legend--l",
            }
        },
        "items": items,
    }
    _add_error(radios, errors, "licence-length")
    return {"radios": radios}


def month_field(
    application: Application, errors: list[FieldError], now: datetime | None = None
) -> dict[str, Any]:
    months = start_months(now)
    items: list[dict[str, Any]] = [
        {
            "value": "",
            "text": "Select a month",
            "selected": application.start_month == "",
        }
    ]
    for month in months:
        items.append(
            {
                "value": month.value,
                "text": month.text,
                "selected": application.start_month == month.value,
            }
        )
    field: dict[str, Any] = {
        "id": "start-month",
        "name": "start-month",
        "label": {
            "text": "When should the licence start?",
            "isPageHeading": True,
            "classes": "govuk-label--l",
        },
        "items": items,
    }
    _add_error(field, errors, "start-month")
    return {"select": field}


def address_fields(application: Application, errors: list[FieldError]) -> dict[str, Any]:
    line1 = _text_input(
        "address-line-1",
        "Address line 1",
        application.address_line_1,
        errors,
        {"autocomplete": "address-line1"},
    )
    line2 = _text_input(
        "address-line-2",
        "Address line 2 (optional)",
        application.address_line_2,
        errors,
        {"autocomplete": "address-line2"},
    )
    town = _text_input(
        "town",
        "Town or city",
        application.town,
        errors,
        {"autocomplete": "address-level2", "classes": "govuk-input--width-20"},
    )
    postcode = _text_input(
        "postcode",
        "Postcode",
        application.postcode,
        errors,
        {
            "autocomplete": "postal-code",
            "classes": "govuk-input--width-10",
            "spellcheck": False,
        },
    )
    lines = (
        MustRender("input", params_from_mapping(line1))
        + MustRender("input", params_from_mapping(line2))
        + MustRender("input", params_from_mapping(town))
        + MustRender("input", params_from_mapping(postcode))
    )
    fieldset = {
        "legend": {
            "text": "What is your address?",
            "isPageHeading": True,
            "classes": "govuk-fieldset__legend--l",
        },
        "html": Safe(lines),
    }
    return {
        "fieldset": fieldset,
        "inset": {
            "text": (
                "This example asks you to type your address. "
                "It does not look up addresses from a postcode."
            )
        },
    }


def evidence_field(application: Application, errors: list[FieldError]) -> dict[str, Any]:
    upload: dict[str, Any] = {
        "id": "evidence",
        "name": "evidence",
        "label": {
            "text": "Upload evidence of a concession",
            "isPageHeading": True,
            "classes": "govuk-label--l",
        },
        "hint": {
            "text": (
                "PDF, PNG, or JPG. You can skip this question if you do not have a concession."
            )
        },
    }
    _add_error(upload, errors, "evidence")
    return {"currentFile": application.evidence_filename, "upload": upload}


def details_field(application: Application, errors: list[FieldError]) -> dict[str, Any]:
    details: dict[str, Any] = {
        "name": "additional-details",
        "id": "additional-details",
        "maxlength": 200,
        "threshold": 75,
        "value": application.additional_details,
        "label": {
            "text": "Is there anything else we should know?",
            "isPageHeading": True,
            "classes": "govuk-label--l",
        },
        "hint": {
            "text": (
                "You can skip this question. Do not include payment card numbers or passwords."
            )
        },
    }
    _add_error(details, errors, "additional-details")
    return {"details": details}


def password_fields(errors: list[FieldError]) -> dict[str, Any]:
    password: dict[str, Any] = {
        "id": "password",
        "name": "password",
        "autocomplete": "new-password",
        "label": {
            "text": "Create a password",
            "isPageHeading": True,
            "classes": "govuk-label--l",
        },
        "hint": {
            "text": "Must be at least 8 characters. This example does not store your password."
        },
    }
    _add_error(password, errors, "password")
    confirm: dict[str, Any] = {
        "id": "password-confirm",
        "name": "password-confirm",
        "autocomplete": "new-password",
        "label": {"text": "Confirm password"},
    }
    _add_error(confirm, errors, "password-confirm")
    return {"password": password, "confirm": confirm}


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
        for option in LICENCE_LENGTHS
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
                        "with a rod in England or Wales."
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
                        '<p class="govuk-body">You need your name, date of birth, '
                        "email address, and home address.</p>"
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
        "html": Safe(f"Your reference number<br><strong>{escape(reference)}</strong>"),
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
