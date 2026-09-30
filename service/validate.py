"""Server-side validation rules for the fishing rod licence journey."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, date, datetime

from service.application import (
    LICENCE_EIGHT_DAYS,
    LICENCE_ONE_DAY,
    LICENCE_TWELVE_MONTHS,
)
from service.options import COUNTRIES, LICENCE_LENGTHS

_EMAIL = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
_ONE_OR_TWO = re.compile(r"^[0-9]{1,2}$")
_FOUR = re.compile(r"^[0-9]{4}$")


@dataclass(frozen=True, slots=True)
class FieldError:
    field: str
    href: str
    text: str

    def as_dict(self) -> dict[str, str]:
        return {"field": self.field, "href": self.href, "text": self.text}


def clean(value: str) -> str:
    return value.strip()


def validate_name(full_name: str) -> list[FieldError]:
    trimmed = clean(full_name)
    if len(trimmed) < 2:
        return [FieldError("full-name", "#full-name", "Enter your full name")]
    if len(trimmed) > 100:
        return [
            FieldError(
                "full-name",
                "#full-name",
                "Full name must be 100 characters or fewer",
            )
        ]
    return []


def validate_date_of_birth(
    day: str, month: str, year: str, now: datetime | None = None
) -> list[FieldError]:
    def fail(text: str) -> list[FieldError]:
        return [FieldError("date-of-birth", "#date-of-birth-day", text)]

    day_s, month_s, year_s = clean(day), clean(month), clean(year)
    if day_s == "" or month_s == "" or year_s == "":
        return fail("Enter your date of birth")
    if (
        not _ONE_OR_TWO.match(day_s)
        or not _ONE_OR_TWO.match(month_s)
        or not _FOUR.match(year_s)
    ):
        return fail("Enter a real date of birth")
    day_n, month_n, year_n = int(day_s), int(month_s), int(year_s)
    try:
        dob = date(year_n, month_n, day_n)
    except ValueError:
        return fail("Enter a real date of birth")
    utc = (now or datetime.now(UTC)).astimezone(UTC).date()
    if dob > utc:
        return fail("Date of birth must be in the past")
    if _age_on(dob, utc) < 13:
        return fail("You must be at least 13 to use this example")
    return []


def validate_email(email: str) -> list[FieldError]:
    if not _EMAIL.match(clean(email)):
        return [
            FieldError(
                "email",
                "#email",
                "Enter an email address in the correct format, like name@example.com",
            )
        ]
    return []


def validate_country(country: str) -> list[FieldError]:
    if any(option.value == country for option in COUNTRIES):
        return []
    return [FieldError("country", "#country", "Select where you will fish")]


def validate_licence_length(value: str) -> list[FieldError]:
    if any(option.value == value for option in LICENCE_LENGTHS):
        return []
    return [
        FieldError(
            "licence-length",
            "#licence-length",
            "Select how long you need the licence for",
        )
    ]


def validate_cookie_choice(value: str) -> list[FieldError]:
    if value not in {"yes", "no"}:
        return [
            FieldError(
                "analytics",
                "#analytics",
                "Select yes if you want to accept analytics cookies",
            )
        ]
    return []


def as_licence_length(value: str) -> str:
    if value in {LICENCE_ONE_DAY, LICENCE_EIGHT_DAYS, LICENCE_TWELVE_MONTHS}:
        return value
    return ""


def _age_on(dob: date, today: date) -> int:
    age = today.year - dob.year
    if (today.month, today.day) < (dob.month, dob.day):
        age -= 1
    return age
