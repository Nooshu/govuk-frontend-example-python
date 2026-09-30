"""Presentation helpers for check-your-answers."""

from __future__ import annotations

from typing import Any

from service.application import Application
from service.options import LICENCE_LENGTHS, label_for


def summary_rows(application: Application) -> list[dict[str, Any]]:
    return [
        _row(
            "Licence length",
            label_for(LICENCE_LENGTHS, application.licence_length),
            "/licence-length",
            "licence length",
        ),
        _row("Name", application.full_name, "/name", "name"),
        _row(
            "Date of birth",
            _format_date_of_birth(application),
            "/date-of-birth",
            "date of birth",
        ),
        _row(
            "Where you will fish",
            application.country,
            "/where-you-will-fish",
            "where you will fish",
        ),
        _row("Email address", application.email, "/email", "email address"),
    ]


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


def _format_date_of_birth(application: Application) -> str:
    day = application.day.strip()
    month = application.month.strip()
    year = application.year.strip()
    if not day or not month or not year:
        return ""
    return f"{day} {month} {year}"
