"""Static option lists (regions, licence lengths, months)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Final


@dataclass(frozen=True, slots=True)
class Option:
    value: str
    text: str


@dataclass(frozen=True, slots=True)
class LicenceOption:
    value: str
    text: str
    fee: str


REGIONS: Final[tuple[Option, ...]] = (
    Option("north-west", "North West"),
    Option("north-east", "North East"),
    Option("midlands", "Midlands"),
    Option("south-west", "South West"),
    Option("south-east", "South East"),
    Option("wales", "Wales"),
)

LICENCE_LENGTHS: Final[tuple[LicenceOption, ...]] = (
    LicenceOption("1-day", "1 day", "£7.10"),
    LicenceOption("8-day", "8 days", "£14.20"),
    LicenceOption("12-month", "12 months", "£36.80"),
)

CONTACT_OPTIONS: Final[tuple[Option, ...]] = (
    Option("email", "Email"),
    Option("telephone", "Telephone"),
)


def regions() -> list[Option]:
    return list(REGIONS)


def licence_lengths() -> list[LicenceOption]:
    return list(LICENCE_LENGTHS)


def contact_options() -> list[Option]:
    return list(CONTACT_OPTIONS)


def licence_length_options() -> list[Option]:
    return [Option(length.value, length.text) for length in LICENCE_LENGTHS]


def start_months(now: datetime | None = None) -> list[Option]:
    """Return the next 12 months the licence can start, from the month ``now`` falls in."""
    utc = (now or datetime.now(UTC)).astimezone(UTC)
    start = datetime(utc.year, utc.month, 1, tzinfo=UTC)
    months: list[Option] = []
    for index in range(12):
        year = start.year + (start.month - 1 + index) // 12
        month = (start.month - 1 + index) % 12 + 1
        months.append(
            Option(
                value=f"{year:04d}-{month:02d}",
                text=datetime(year, month, 1, tzinfo=UTC).strftime("%B %Y"),
            )
        )
    return months


def label_for(options: list[Option] | tuple[Option, ...], value: str) -> str:
    for option in options:
        if option.value == value:
            return option.text
    return value
