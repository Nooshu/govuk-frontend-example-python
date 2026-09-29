"""Persist validated answers onto an Application."""

from __future__ import annotations

from dataclasses import dataclass

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
    mark_completed,
    unmark_completed,
)
from service.options import REGIONS
from service.validate import as_contact_by, as_licence_length, clean, normalise_postcode


def _finish(completed: list[str], step_id: str, valid: bool) -> list[str]:
    if valid:
        return mark_completed(completed, step_id)
    return unmark_completed(completed, step_id)


def save_name(
    application: Application, first_name: str, last_name: str, *, valid: bool
) -> Application:
    application.first_name = clean(first_name)
    application.last_name = clean(last_name)
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


def save_contact(
    application: Application, contact_by: str, telephone: str, *, valid: bool
) -> Application:
    application.contact_by = as_contact_by(contact_by)
    application.telephone = clean(telephone)
    application.completed = _finish(application.completed, STEP_CONTACT_PREFERENCE, valid)
    return application


def save_regions(
    application: Application, selected: list[str], *, valid: bool
) -> Application:
    known = {NOT_SURE, *(region.value for region in REGIONS)}
    application.regions = [region for region in selected if region in known]
    application.completed = _finish(application.completed, STEP_WHERE_YOU_WILL_FISH, valid)
    return application


def save_licence(application: Application, value: str, *, valid: bool) -> Application:
    application.licence_length = as_licence_length(value)
    application.completed = _finish(application.completed, STEP_LICENCE_LENGTH, valid)
    return application


def save_month(application: Application, value: str, *, valid: bool) -> Application:
    application.start_month = value
    application.completed = _finish(application.completed, STEP_START_MONTH, valid)
    return application


@dataclass(frozen=True, slots=True)
class AddressValues:
    line1: str
    line2: str
    town: str
    postcode: str


def save_address(
    application: Application, values: AddressValues, *, valid: bool
) -> Application:
    application.address_line_1 = clean(values.line1)
    application.address_line_2 = clean(values.line2)
    application.town = clean(values.town)
    if valid:
        application.postcode = normalise_postcode(values.postcode)
    else:
        application.postcode = clean(values.postcode)
    application.completed = _finish(application.completed, STEP_ADDRESS, valid)
    return application


def save_evidence(
    application: Application, filename: str, *, has_file: bool, valid: bool
) -> Application:
    if has_file and valid:
        application.evidence_filename = filename
    application.completed = _finish(application.completed, STEP_EVIDENCE, valid)
    return application


def save_details(application: Application, value: str, *, valid: bool) -> Application:
    application.additional_details = value
    application.completed = _finish(application.completed, STEP_ADDITIONAL_DETAILS, valid)
    return application


def save_password(application: Application, *, valid: bool) -> Application:
    application.password_created = valid
    application.completed = _finish(application.completed, STEP_CREATE_A_PASSWORD, valid)
    return application
