"""Server-side validation rules for the rod licence journey."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import PurePosixPath

from service.application import (
    CONTACT_BY_EMAIL,
    CONTACT_BY_TELEPHONE,
    LICENCE_EIGHT_DAY,
    LICENCE_ONE_DAY,
    LICENCE_TWELVE_MTH,
    NOT_SURE,
)
from service.options import REGIONS, start_months

_EMAIL = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
_PHONE = re.compile(r"^[0-9+() -]{8,20}$")
_POSTCODE = re.compile(r"^[A-Z]{1,2}[0-9][A-Z0-9]? [0-9][A-Z]{2}$")
_EVIDENCE = re.compile(r"(?i)\.(pdf|png|jpe?g)$")
_ONE_OR_TWO = re.compile(r"^[0-9]{1,2}$")
_FOUR = re.compile(r"^[0-9]{4}$")
_FILENAME = re.compile(r"^[\w. -]+$")


@dataclass(frozen=True, slots=True)
class FieldError:
    field: str
    href: str
    text: str

    def as_dict(self) -> dict[str, str]:
        return {"field": self.field, "href": self.href, "text": self.text}


def clean(value: str) -> str:
    return value.strip()


def validate_name(first_name: str, last_name: str) -> list[FieldError]:
    errors: list[FieldError] = []
    errors.extend(_name_part("first-name", "First name", "Enter your first name", first_name))
    errors.extend(_name_part("last-name", "Last name", "Enter your last name", last_name))
    return errors


def _name_part(field: str, label: str, missing: str, value: str) -> list[FieldError]:
    trimmed = clean(value)
    if trimmed == "":
        return [FieldError(field, f"#{field}", missing)]
    if len(trimmed) > 100:
        return [FieldError(field, f"#{field}", f"{label} must be 100 characters or fewer")]
    return []


def validate_date_of_birth(
    day: str, month: str, year: str, now: datetime | None = None
) -> list[FieldError]:
    def fail(text: str) -> list[FieldError]:
        return [FieldError("date-of-birth", "#date-of-birth-day", text)]

    day_s, month_s, year_s = clean(day), clean(month), clean(year)
    if day_s == "" or month_s == "" or year_s == "":
        return fail("Date of birth must include a day, month and year")
    if (
        not _ONE_OR_TWO.match(day_s)
        or not _ONE_OR_TWO.match(month_s)
        or not _FOUR.match(year_s)
    ):
        return fail("Date of birth must be a real date")
    day_n, month_n, year_n = int(day_s), int(month_s), int(year_s)
    try:
        dob = date(year_n, month_n, day_n)
    except ValueError:
        return fail("Date of birth must be a real date")
    utc = (now or datetime.now(UTC)).astimezone(UTC).date()
    if dob > utc:
        return fail("Date of birth must be in the past")
    if _age_on(dob, utc) < 13:
        return fail("You must be 13 or over to apply for a rod licence")
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


def validate_contact_preference(contact_by: str, telephone: str) -> list[FieldError]:
    errors: list[FieldError] = []
    if contact_by not in {CONTACT_BY_EMAIL, CONTACT_BY_TELEPHONE}:
        errors.append(
            FieldError("contact-by", "#contact-by", "Select how we should contact you")
        )
    trimmed = clean(telephone)
    if contact_by == CONTACT_BY_TELEPHONE and trimmed == "":
        errors.append(FieldError("telephone", "#telephone", "Enter a telephone number"))
    elif trimmed != "" and not _PHONE.match(trimmed):
        errors.append(
            FieldError(
                "telephone",
                "#telephone",
                "Enter a telephone number, like 01632 960 001",
            )
        )
    return errors


def validate_regions(selected: list[str]) -> list[FieldError]:
    def problem(text: str) -> list[FieldError]:
        return [FieldError("regions", "#regions", text)]

    if not selected:
        return problem("Select where you will fish")
    known = {region.value for region in REGIONS}
    chosen: list[str] = []
    exclusive = False
    for region in selected:
        if region == NOT_SURE:
            exclusive = True
            continue
        chosen.append(region)
    if exclusive and chosen:
        return problem(
            "Select where you will fish, or select that you have not decided yet"
        )
    for region in chosen:
        if region not in known:
            return problem("Select where you will fish")
    return []


def validate_licence_length(value: str) -> list[FieldError]:
    from service.options import LICENCE_LENGTHS

    if any(option.value == value for option in LICENCE_LENGTHS):
        return []
    return [
        FieldError(
            "licence-length",
            "#licence-length",
            "Select how long you need a licence for",
        )
    ]


def validate_start_month(value: str, now: datetime | None = None) -> list[FieldError]:
    if any(month.value == value for month in start_months(now)):
        return []
    return [
        FieldError("start-month", "#start-month", "Select when the licence should start")
    ]


def validate_address(line1: str, town: str, postcode: str) -> list[FieldError]:
    errors: list[FieldError] = []
    trimmed_line1 = clean(line1)
    if trimmed_line1 == "":
        errors.append(FieldError("address-line-1", "#address-line-1", "Enter address line 1"))
    elif len(trimmed_line1) > 100:
        errors.append(
            FieldError(
                "address-line-1",
                "#address-line-1",
                "Address line 1 must be 100 characters or fewer",
            )
        )
    if clean(town) == "":
        errors.append(FieldError("town", "#town", "Enter a town or city"))
    normalised = normalise_postcode(postcode)
    if normalised == "" or not _POSTCODE.match(normalised):
        errors.append(FieldError("postcode", "#postcode", "Enter a full UK postcode"))
    return errors


def validate_evidence(filename: str) -> list[FieldError]:
    if filename == "":
        return []
    if not _EVIDENCE.search(filename):
        return [
            FieldError(
                "evidence",
                "#evidence",
                "The selected file must be a PDF, PNG, or JPG",
            )
        ]
    return []


def validate_additional_details(value: str) -> list[FieldError]:
    if len(value) > 200:
        return [
            FieldError(
                "additional-details",
                "#additional-details",
                "Additional details must be 200 characters or fewer",
            )
        ]
    return []


def validate_password(password: str, confirm: str) -> list[FieldError]:
    if len(password) < 8:
        return [FieldError("password", "#password", "Password must be at least 8 characters")]
    if password != confirm:
        return [
            FieldError(
                "password-confirm",
                "#password-confirm",
                "Enter the same password in both fields",
            )
        ]
    return []


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


def normalise_postcode(value: str) -> str:
    compact = clean(value).upper().replace(" ", "")
    if len(compact) < 5:
        return ""
    return f"{compact[:-3]} {compact[-3:]}"


def as_contact_by(value: str) -> str:
    if value in {CONTACT_BY_EMAIL, CONTACT_BY_TELEPHONE}:
        return value
    return ""


def as_licence_length(value: str) -> str:
    if value in {LICENCE_ONE_DAY, LICENCE_EIGHT_DAY, LICENCE_TWELVE_MTH}:
        return value
    return ""


def safe_filename(filename: str) -> str | None:
    base = PurePosixPath(filename.replace("\\", "/")).name
    if base in {"", ".", ".."}:
        return None
    if len(base) > 120 or not _FILENAME.match(base):
        return None
    return base


def _age_on(dob: date, today: date) -> int:
    age = today.year - dob.year
    if (today.month, today.day) < (dob.month, dob.day):
        age -= 1
    return age
