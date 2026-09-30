"""Persist validated answers onto an Application."""

from __future__ import annotations

from service.application import (
    STEP_DATE_OF_BIRTH,
    STEP_EMAIL,
    STEP_LICENCE_LENGTH,
    STEP_NAME,
    STEP_WHERE_YOU_WILL_FISH,
    Application,
    mark_completed,
    unmark_completed,
)
from service.validate import as_licence_length, clean


def _finish(completed: list[str], step_id: str, valid: bool) -> list[str]:
    if valid:
        return mark_completed(completed, step_id)
    return unmark_completed(completed, step_id)


def save_name(application: Application, full_name: str, *, valid: bool) -> Application:
    application.full_name = clean(full_name)
    application.completed = _finish(application.completed, STEP_NAME, valid)
    return application


def save_date(
    application: Application, day: str, month: str, year: str, *, valid: bool
) -> Application:
    application.day = clean(day)
    application.month = clean(month)
    application.year = clean(year)
    application.completed = _finish(application.completed, STEP_DATE_OF_BIRTH, valid)
    return application


def save_email(application: Application, email: str, *, valid: bool) -> Application:
    application.email = clean(email)
    application.completed = _finish(application.completed, STEP_EMAIL, valid)
    return application


def save_country(application: Application, country: str, *, valid: bool) -> Application:
    application.country = clean(country)
    application.completed = _finish(application.completed, STEP_WHERE_YOU_WILL_FISH, valid)
    return application


def save_licence(application: Application, value: str, *, valid: bool) -> Application:
    application.licence_length = as_licence_length(value)
    application.completed = _finish(application.completed, STEP_LICENCE_LENGTH, valid)
    return application
