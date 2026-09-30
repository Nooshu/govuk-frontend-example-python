"""Static option lists (countries, licence lengths, fees)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True, slots=True)
class Option:
    value: str
    text: str


@dataclass(frozen=True, slots=True)
class FeeOption:
    text: str
    fee: str


COUNTRIES: Final[tuple[Option, ...]] = (
    Option("England", "England"),
    Option("Wales", "Wales"),
    Option("Scotland", "Scotland"),
)

LICENCE_LENGTHS: Final[tuple[Option, ...]] = (
    Option("1-day", "1 day"),
    Option("8-days", "8 days"),
    Option("12-months", "12 months"),
)

LICENCE_FEES: Final[tuple[FeeOption, ...]] = (
    FeeOption("1 day", "£7.10"),
    FeeOption("8 days", "£14.20"),
    FeeOption("12 months", "£36.80"),
)


def countries() -> list[Option]:
    return list(COUNTRIES)


def licence_lengths() -> list[Option]:
    return list(LICENCE_LENGTHS)


def licence_fees() -> list[FeeOption]:
    return list(LICENCE_FEES)


def label_for(options: list[Option] | tuple[Option, ...], value: str) -> str:
    for option in options:
        if option.value == value:
            return option.text
    return value
