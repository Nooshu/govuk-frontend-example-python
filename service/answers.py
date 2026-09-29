"""Presentation helpers for check-answers and the task list."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime
from typing import Any

from service.application import (
    NOT_SURE,
    STEP_ADDITIONAL_DETAILS,
    STEP_ADDRESS,
    STEP_CONTACT_PREFERENCE,
    STEP_CREATE_A_PASSWORD,
    STEP_DATE_OF_BIRTH,
    STEP_EMAIL,
    STEP_EVIDENCE,
    STEP_LICENCE_LENGTH,
    STEP_NAME,
    STEP_START_MONTH,
    STEP_WHERE_YOU_WILL_FISH,
    Application,
    required_steps_complete,
)
from service.options import (
    CONTACT_OPTIONS,
    REGIONS,
    label_for,
    licence_length_options,
    start_months,
)


@dataclass(frozen=True, slots=True)
class TaskSection:
    heading: str
    id_prefix: str
    items: list[dict[str, Any]]


def summary_rows(
    application: Application, now: datetime | None = None
) -> list[dict[str, Any]]:
    clock = now or datetime.now(UTC)
    return [
        _row("Name", _join_name(application), "/name", "name"),
        _row(
            "Date of birth",
            _format_date_of_birth(application),
            "/date-of-birth",
            "date of birth",
        ),
        _row("Email address", application.email, "/email", "email address"),
        _row(
            "Contact preference",
            label_for(CONTACT_OPTIONS, application.contact_by),
            "/contact-preference",
            "contact preference",
        ),
        _row(
            "Telephone number",
            application.telephone,
            "/contact-preference",
            "telephone number",
        ),
        _row(
            "Where you will fish",
            _format_regions(application.regions),
            "/where-you-will-fish",
            "where you will fish",
        ),
        _row(
            "Licence length",
            label_for(licence_length_options(), application.licence_length),
            "/licence-length",
            "licence length",
        ),
        _row(
            "Start month",
            label_for(start_months(clock), application.start_month),
            "/start-month",
            "start month",
        ),
        _row("Address", _format_address(application), "/address", "address"),
        _row("Evidence", application.evidence_filename, "/evidence", "evidence"),
        _row(
            "Additional details",
            application.additional_details,
            "/additional-details",
            "additional details",
        ),
        _row(
            "Password",
            "Set" if application.password_created else "",
            "/create-a-password",
            "password",
        ),
    ]


def task_sections(application: Application) -> list[TaskSection]:
    ready = required_steps_complete(application)
    return [
        TaskSection(
            "Personal details",
            "personal-details",
            [
                _task(application, STEP_NAME, "Your name"),
                _task(application, STEP_DATE_OF_BIRTH, "Date of birth"),
                _task(application, STEP_EMAIL, "Email address"),
                _task(application, STEP_CONTACT_PREFERENCE, "Contact preference"),
            ],
        ),
        TaskSection(
            "Your licence",
            "your-licence",
            [
                _task(application, STEP_WHERE_YOU_WILL_FISH, "Where you will fish"),
                _task(application, STEP_LICENCE_LENGTH, "Licence length"),
                _task(application, STEP_START_MONTH, "Start month"),
            ],
        ),
        TaskSection(
            "More about you",
            "more-about-you",
            [
                _task(application, STEP_ADDRESS, "Your address"),
                _task(application, STEP_EVIDENCE, "Concession evidence"),
                _task(application, STEP_ADDITIONAL_DETAILS, "Additional details"),
                _task(application, STEP_CREATE_A_PASSWORD, "Password"),
            ],
        ),
        TaskSection("Apply", "apply", [_submit_task(application, ready)]),
    ]


def _submit_task(application: Application, ready: bool) -> dict[str, Any]:
    item: dict[str, Any] = {
        "title": {"text": "Check your answers and submit"},
    }
    if not ready:
        item["status"] = _not_started_tag("Cannot start yet")
    elif application.submitted:
        item["href"] = "/check-answers"
        item["status"] = {"text": "Completed"}
    else:
        item["href"] = "/check-answers"
        item["status"] = _not_started_tag("Not started")
    return item


def _task(application: Application, step_id: str, text: str) -> dict[str, Any]:
    status: dict[str, Any] = (
        {"text": "Completed"}
        if application.is_completed(step_id)
        else _not_started_tag("Not started")
    )
    return {
        "title": {"text": text},
        "href": f"/{step_id}",
        "status": status,
    }


def _not_started_tag(text: str) -> dict[str, Any]:
    return {"tag": {"text": text, "classes": "govuk-tag--grey"}}


def _row(key: str, value: str, href: str, hidden: str) -> dict[str, Any]:
    shown = value.strip() if value.strip() else "Not provided"
    return {
        "key": {"text": key},
        "value": {"text": shown},
        "actions": {
            "items": [
                {
                    "href": f"{href}?return=check-answers",
                    "text": "Change",
                    "visuallyHiddenText": hidden,
                }
            ]
        },
    }


def _join_name(application: Application) -> str:
    return f"{application.first_name} {application.last_name}".strip()


def _format_date_of_birth(application: Application) -> str:
    try:
        day = int(application.day)
        month = int(application.month)
        year = int(application.year)
    except ValueError:
        return ""
    if day == 0 or month == 0 or year == 0:
        return ""
    try:
        dob = date(year, month, day)
    except ValueError:
        return ""
    return f"{dob.day} {dob.strftime('%B %Y')}"


def _format_regions(selected: list[str]) -> str:
    if NOT_SURE in selected:
        return "Not decided yet"
    labels = [label_for(REGIONS, region) for region in selected]
    return ", ".join(labels)


def _format_address(application: Application) -> str:
    parts = [
        part.strip()
        for part in (
            application.address_line_1,
            application.address_line_2,
            application.town,
            application.postcode,
        )
        if part.strip()
    ]
    return ", ".join(parts)
