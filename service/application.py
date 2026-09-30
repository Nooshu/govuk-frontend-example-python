"""Application answers, step graph, and completion helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final

LICENCE_ONE_DAY: Final = "1-day"
LICENCE_EIGHT_DAYS: Final = "8-days"
LICENCE_TWELVE_MONTHS: Final = "12-months"

STEP_LICENCE_LENGTH: Final = "licence-length"
STEP_NAME: Final = "name"
STEP_DATE_OF_BIRTH: Final = "date-of-birth"
STEP_WHERE_YOU_WILL_FISH: Final = "where-you-will-fish"
STEP_EMAIL: Final = "email"


@dataclass(frozen=True, slots=True)
class Step:
    id: str
    path: str
    heading: str


STEPS: Final[tuple[Step, ...]] = (
    Step(STEP_LICENCE_LENGTH, "/licence-length", "How long do you need the licence for?"),
    Step(STEP_NAME, "/name", "What is your full name?"),
    Step(STEP_DATE_OF_BIRTH, "/date-of-birth", "What is your date of birth?"),
    Step(STEP_WHERE_YOU_WILL_FISH, "/where-you-will-fish", "Where will you fish?"),
    Step(STEP_EMAIL, "/email", "What is your email address?"),
)


@dataclass
class Application:
    licence_length: str = ""
    full_name: str = ""
    day: str = ""
    month: str = ""
    year: str = ""
    country: str = ""
    email: str = ""
    submitted: bool = False
    reference: str = ""
    completed: list[str] = field(default_factory=list)

    def is_completed(self, step_id: str) -> bool:
        return step_id in self.completed

    def to_dict(self) -> dict[str, object]:
        return {
            "licence_length": self.licence_length,
            "full_name": self.full_name,
            "day": self.day,
            "month": self.month,
            "year": self.year,
            "country": self.country,
            "email": self.email,
            "submitted": self.submitted,
            "reference": self.reference,
            "completed": list(self.completed),
        }

    @classmethod
    def from_dict(cls, data: dict[str, object] | None) -> Application:
        if not data:
            return cls()
        completed = data.get("completed") or []
        return cls(
            licence_length=str(data.get("licence_length") or ""),
            full_name=str(data.get("full_name") or ""),
            day=str(data.get("day") or ""),
            month=str(data.get("month") or ""),
            year=str(data.get("year") or ""),
            country=str(data.get("country") or ""),
            email=str(data.get("email") or ""),
            submitted=bool(data.get("submitted")),
            reference=str(data.get("reference") or ""),
            completed=[str(c) for c in completed] if isinstance(completed, list) else [],
        )


def steps() -> list[Step]:
    return list(STEPS)


def step_by_id(step_id: str) -> Step | None:
    for step in STEPS:
        if step.id == step_id:
            return step
    return None


def step_by_path(path: str) -> Step | None:
    for step in STEPS:
        if step.path == path:
            return step
    return None


def next_step(step_id: str) -> Step | None:
    index = _index_of(step_id)
    if index == -1 or index + 1 >= len(STEPS):
        return None
    return STEPS[index + 1]


def previous_step(step_id: str) -> Step | None:
    index = _index_of(step_id)
    if index <= 0:
        return None
    return STEPS[index - 1]


def mark_completed(completed: list[str], step_id: str) -> list[str]:
    if step_id in completed:
        return list(completed)
    return [*completed, step_id]


def unmark_completed(completed: list[str], step_id: str) -> list[str]:
    return [item for item in completed if item != step_id]


def required_steps_complete(application: Application) -> bool:
    return all(application.is_completed(step.id) for step in STEPS)


def first_incomplete_step(application: Application) -> Step | None:
    for step in STEPS:
        if not application.is_completed(step.id):
            return step
    return None


def _index_of(step_id: str) -> int:
    for index, step in enumerate(STEPS):
        if step.id == step_id:
            return index
    return -1


def reference_for(session_key: str) -> str:
    """Build an FR + 8-digit example reference from the session key."""
    digits = "".join(ch for ch in session_key if ch.isdigit())
    if len(digits) < 8:
        # Fall back to hex-ish characters mapped to digits.
        mapped = "".join(str(ord(ch) % 10) for ch in session_key)
        digits = (digits + mapped + "00000000")[:8]
    else:
        digits = digits[:8]
    return "FR" + digits.zfill(8)[-8:]
