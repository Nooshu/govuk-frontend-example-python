"""Django Forms for the licence journey and cookie settings.

Field names use underscores. Views bind POST data with hyphenated GOV.UK names
mapped into these fields (see ``service.views``).
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from django import forms

from service.validate import (
    FieldError,
    validate_cookie_choice,
    validate_country,
    validate_date_of_birth,
    validate_email,
    validate_licence_length,
    validate_name,
)


def _attach(form: forms.Form, errors: list[FieldError]) -> None:
    for err in errors:
        name = err.field.replace("-", "_")
        if name in form.fields:
            form.add_error(name, err.text)
        else:  # pragma: no cover — FieldError ids always map to form fields in this service
            form.add_error(None, err.text)


class NameForm(forms.Form):
    full_name = forms.CharField(required=False)

    def clean(self) -> dict[str, object]:
        cleaned = super().clean() or {}
        _attach(self, validate_name(str(cleaned.get("full_name") or "")))
        return cleaned


class DateOfBirthForm(forms.Form):
    day = forms.CharField(required=False)
    month = forms.CharField(required=False)
    year = forms.CharField(required=False)

    def __init__(self, *args: Any, now: datetime | None = None, **kwargs: Any) -> None:
        self._now = now
        super().__init__(*args, **kwargs)

    def clean(self) -> dict[str, object]:
        cleaned = super().clean() or {}
        errors = validate_date_of_birth(
            str(cleaned.get("day") or ""),
            str(cleaned.get("month") or ""),
            str(cleaned.get("year") or ""),
            self._now,
        )
        if errors:
            self.add_error(None, errors[0].text)
        return cleaned


class EmailForm(forms.Form):
    email = forms.CharField(required=False)

    def clean(self) -> dict[str, object]:
        cleaned = super().clean() or {}
        _attach(self, validate_email(str(cleaned.get("email") or "")))
        return cleaned


class WhereYouWillFishForm(forms.Form):
    country = forms.CharField(required=False)

    def clean(self) -> dict[str, object]:
        cleaned = super().clean() or {}
        _attach(self, validate_country(str(cleaned.get("country") or "")))
        return cleaned


class LicenceLengthForm(forms.Form):
    licence_length = forms.CharField(required=False)

    def clean(self) -> dict[str, object]:
        cleaned = super().clean() or {}
        _attach(self, validate_licence_length(str(cleaned.get("licence_length") or "")))
        return cleaned


class CookieSettingsForm(forms.Form):
    analytics = forms.CharField(required=False)

    def clean(self) -> dict[str, object]:
        cleaned = super().clean() or {}
        _attach(self, validate_cookie_choice(str(cleaned.get("analytics") or "")))
        return cleaned


def field_errors_from_form(
    form: forms.Form, mapping: dict[str, tuple[str, str]]
) -> list[FieldError]:
    """Convert Django form errors into FieldError list using ``django_name -> (field, href)``."""
    errors: list[FieldError] = []
    for name, messages in form.errors.items():
        if name == "__all__":
            field_href = mapping.get("__all__") or mapping.get("day")
            if field_href is None:  # pragma: no cover
                continue
            field, href = field_href
            for message in messages:
                errors.append(FieldError(field, href, str(message)))
            continue
        field_href = mapping.get(name)
        if field_href is None:
            continue
        field, href = field_href
        for message in messages:
            errors.append(FieldError(field, href, str(message)))
    return errors


def now_utc() -> datetime:
    return datetime.now(UTC)
