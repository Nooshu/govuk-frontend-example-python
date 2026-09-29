"""Application answers, step graph, and completion helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final

CONTACT_BY_EMAIL: Final = "email"
CONTACT_BY_TELEPHONE: Final = "telephone"

LICENCE_ONE_DAY: Final = "1-day"
LICENCE_EIGHT_DAY: Final = "8-day"
LICENCE_TWELVE_MTH: Final = "12-month"

NOT_SURE: Final = "not-sure"

STEP_NAME: Final = "name"
STEP_DATE_OF_BIRTH: Final = "date-of-birth"
STEP_EMAIL: Final = "email"
STEP_CONTACT_PREFERENCE: Final = "contact-preference"
STEP_WHERE_YOU_WILL_FISH: Final = "where-you-will-fish"
STEP_LICENCE_LENGTH: Final = "licence-length"
STEP_START_MONTH: Final = "start-month"
STEP_ADDRESS: Final = "address"
STEP_EVIDENCE: Final = "evidence"
STEP_ADDITIONAL_DETAILS: Final = "additional-details"
STEP_CREATE_A_PASSWORD: Final = "create-a-password"


@dataclass(frozen=True, slots=True)
class Step:
    id: str
    path: str
    heading: str


STEPS: Final[tuple[Step, ...]] = (
    Step(STEP_NAME, "/name", "What is your name?"),
    Step(STEP_DATE_OF_BIRTH, "/date-of-birth", "What is your date of birth?"),
    Step(STEP_EMAIL, "/email", "What is your email address?"),
    Step(STEP_CONTACT_PREFERENCE, "/contact-preference", "How should we contact you?"),
    Step(STEP_WHERE_YOU_WILL_FISH, "/where-you-will-fish", "Where will you fish?"),
    Step(STEP_LICENCE_LENGTH, "/licence-length", "How long do you need a licence for?"),
    Step(STEP_START_MONTH, "/start-month", "When should the licence start?"),
    Step(STEP_ADDRESS, "/address", "What is your address?"),
    Step(STEP_EVIDENCE, "/evidence", "Upload evidence of a concession"),
    Step(STEP_ADDITIONAL_DETAILS, "/additional-details", "Is there anything else we should know?"),
    Step(STEP_CREATE_A_PASSWORD, "/create-a-password", "Create a password"),
)

OPTIONAL_STEPS: Final[frozenset[str]] = frozenset({STEP_EVIDENCE, STEP_ADDITIONAL_DETAILS})


@dataclass
class Application:
    first_name: str = ""
    last_name: str = ""
    day: str = ""
    month: str = ""
    year: str = ""
    email: str = ""
    contact_by: str = ""
    telephone: str = ""
    regions: list[str] = field(default_factory=list)
    licence_length: str = ""
    start_month: str = ""
    address_line_1: str = ""
    address_line_2: str = ""
    town: str = ""
    postcode: str = ""
    evidence_filename: str = ""
    additional_details: str = ""
    password_created: bool = False
    submitted: bool = False
    reference: str = ""
    completed: list[str] = field(default_factory=list)

    def is_completed(self, step_id: str) -> bool:
        return step_id in self.completed

    def to_dict(self) -> dict[str, object]:
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "day": self.day,
            "month": self.month,
            "year": self.year,
            "email": self.email,
            "contact_by": self.contact_by,
            "telephone": self.telephone,
            "regions": list(self.regions),
            "licence_length": self.licence_length,
            "start_month": self.start_month,
            "address_line_1": self.address_line_1,
            "address_line_2": self.address_line_2,
            "town": self.town,
            "postcode": self.postcode,
            "evidence_filename": self.evidence_filename,
            "additional_details": self.additional_details,
            "password_created": self.password_created,
            "submitted": self.submitted,
            "reference": self.reference,
            "completed": list(self.completed),
        }

    @classmethod
    def from_dict(cls, data: dict[str, object] | None) -> Application:
        if not data:
            return cls()
        regions = data.get("regions") or []
        completed = data.get("completed") or []
        return cls(
            first_name=str(data.get("first_name") or ""),
            last_name=str(data.get("last_name") or ""),
            day=str(data.get("day") or ""),
            month=str(data.get("month") or ""),
            year=str(data.get("year") or ""),
            email=str(data.get("email") or ""),
            contact_by=str(data.get("contact_by") or ""),
            telephone=str(data.get("telephone") or ""),
            regions=[str(r) for r in regions] if isinstance(regions, list) else [],
            licence_length=str(data.get("licence_length") or ""),
            start_month=str(data.get("start_month") or ""),
            address_line_1=str(data.get("address_line_1") or ""),
            address_line_2=str(data.get("address_line_2") or ""),
            town=str(data.get("town") or ""),
            postcode=str(data.get("postcode") or ""),
            evidence_filename=str(data.get("evidence_filename") or ""),
            additional_details=str(data.get("additional_details") or ""),
            password_created=bool(data.get("password_created")),
            submitted=bool(data.get("submitted")),
            reference=str(data.get("reference") or ""),
            completed=[str(c) for c in completed] if isinstance(completed, list) else [],
        )


def steps() -> list[Step]:
    return list(STEPS)


def optional(step_id: str) -> bool:
    return step_id in OPTIONAL_STEPS


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
    return all(optional(step.id) or application.is_completed(step.id) for step in STEPS)


def first_incomplete_step(application: Application) -> Step | None:
    for step in STEPS:
        if not optional(step.id) and not application.is_completed(step.id):
            return step
    return None


def _index_of(step_id: str) -> int:
    for index, step in enumerate(STEPS):
        if step.id == step_id:
            return index
    return -1


def reference_for(session_key: str) -> str:
    prefix = session_key[:6] if len(session_key) > 6 else session_key
    return "RL" + prefix.upper()
