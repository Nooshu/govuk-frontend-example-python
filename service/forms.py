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
    validate_additional_details,
    validate_address,
    validate_contact_preference,
    validate_cookie_choice,
    validate_date_of_birth,
    validate_email,
    validate_evidence,
    validate_licence_length,
    validate_name,
    validate_password,
    validate_regions,
    validate_start_month,
)


def _attach(form: forms.Form, errors: list[FieldError]) -> None:
    for err in errors:
        # Map hyphenated GOV.UK field ids onto Django field names where they differ.
        name = err.field.replace("-", "_")
        if name in form.fields:
            form.add_error(name, err.text)
        else:  # pragma: no cover — FieldError ids always map to form fields in this service
            form.add_error(None, err.text)


class NameForm(forms.Form):
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)

    def clean(self) -> dict[str, object]:
        cleaned = super().clean() or {}
        errors = validate_name(
            str(cleaned.get("first_name") or ""),
            str(cleaned.get("last_name") or ""),
        )
        _attach(self, errors)
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


class ContactPreferenceForm(forms.Form):
    contact_by = forms.CharField(required=False)
    telephone = forms.CharField(required=False)

    def clean(self) -> dict[str, object]:
        cleaned = super().clean() or {}
        _attach(
            self,
            validate_contact_preference(
                str(cleaned.get("contact_by") or ""),
                str(cleaned.get("telephone") or ""),
            ),
        )
        return cleaned


class WhereYouWillFishForm(forms.Form):
    regions = forms.MultipleChoiceField(
        required=False,
        choices=[
            ("north-west", "North West"),
            ("north-east", "North East"),
            ("midlands", "Midlands"),
            ("south-west", "South West"),
            ("south-east", "South East"),
            ("wales", "Wales"),
            ("not-sure", "I have not decided yet"),
        ],
    )

    def clean(self) -> dict[str, object]:
        cleaned = super().clean() or {}
        selected = cleaned.get("regions") or []
        if not isinstance(selected, list):  # pragma: no cover — MultipleChoiceField always lists
            selected = list(selected)
        _attach(self, validate_regions([str(item) for item in selected]))
        return cleaned


class LicenceLengthForm(forms.Form):
    licence_length = forms.CharField(required=False)

    def clean(self) -> dict[str, object]:
        cleaned = super().clean() or {}
        _attach(self, validate_licence_length(str(cleaned.get("licence_length") or "")))
        return cleaned


class StartMonthForm(forms.Form):
    start_month = forms.CharField(required=False)

    def __init__(self, *args: Any, now: datetime | None = None, **kwargs: Any) -> None:
        self._now = now
        super().__init__(*args, **kwargs)

    def clean(self) -> dict[str, object]:
        cleaned = super().clean() or {}
        _attach(
            self,
            validate_start_month(str(cleaned.get("start_month") or ""), self._now),
        )
        return cleaned


class AddressForm(forms.Form):
    address_line_1 = forms.CharField(required=False)
    address_line_2 = forms.CharField(required=False)
    town = forms.CharField(required=False)
    postcode = forms.CharField(required=False)

    def clean(self) -> dict[str, object]:
        cleaned = super().clean() or {}
        _attach(
            self,
            validate_address(
                str(cleaned.get("address_line_1") or ""),
                str(cleaned.get("town") or ""),
                str(cleaned.get("postcode") or ""),
            ),
        )
        return cleaned


class EvidenceForm(forms.Form):
    evidence = forms.CharField(required=False)

    def clean(self) -> dict[str, object]:
        cleaned = super().clean() or {}
        _attach(self, validate_evidence(str(cleaned.get("evidence") or "")))
        return cleaned


class AdditionalDetailsForm(forms.Form):
    additional_details = forms.CharField(required=False)

    def clean(self) -> dict[str, object]:
        cleaned = super().clean() or {}
        _attach(
            self,
            validate_additional_details(str(cleaned.get("additional_details") or "")),
        )
        return cleaned


class PasswordForm(forms.Form):
    password = forms.CharField(required=False)
    password_confirm = forms.CharField(required=False)

    def clean(self) -> dict[str, object]:
        cleaned = super().clean() or {}
        _attach(
            self,
            validate_password(
                str(cleaned.get("password") or ""),
                str(cleaned.get("password_confirm") or ""),
            ),
        )
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
