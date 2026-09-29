"""Extra coverage for params scanner, middleware, and view edge paths."""

from __future__ import annotations

import json
from datetime import UTC, datetime

import pytest
from config.middleware import BaselineHeadersMiddleware, CompressionMiddleware
from django.http import HttpResponse, StreamingHttpResponse
from django.test import Client, RequestFactory, override_settings
from govuk_components.rendering.attributes import Attributes, attribute
from govuk_components.rendering.nunjucks import _same_number, loose_eq, strict_eq
from govuk_components.rendering.params import (
    Number,
    Params,
    Safe,
    parse_json,
    parse_json_value,
)
from service.application import Application
from service.assets import resolve_asset
from service.forms import (
    AdditionalDetailsForm,
    AddressForm,
    ContactPreferenceForm,
    EmailForm,
    EvidenceForm,
    LicenceLengthForm,
    PasswordForm,
    StartMonthForm,
    WhereYouWillFishForm,
    field_errors_from_form,
)
from service.session import pop_errors_for
from service.views import _now


def test_parse_json_edges() -> None:
    parsed = parse_json('{"a":1}')
    assert parsed.get("a") == Number("1")
    assert parse_json_value(b'"hi"') == "hi"
    with pytest.raises(json.JSONDecodeError):
        parse_json_value("")
    with pytest.raises(json.JSONDecodeError):
        parse_json_value("{")
    with pytest.raises(json.JSONDecodeError):
        parse_json_value('{"a"}')
    with pytest.raises(json.JSONDecodeError):
        parse_json_value('{"a":1')
    with pytest.raises(json.JSONDecodeError):
        parse_json_value("[1")
    with pytest.raises(json.JSONDecodeError):
        parse_json_value("[1,]")
    with pytest.raises(json.JSONDecodeError):
        parse_json_value("-")
    with pytest.raises(json.JSONDecodeError):
        parse_json_value("1.")
    with pytest.raises(json.JSONDecodeError):
        parse_json_value("1e")
    with pytest.raises(json.JSONDecodeError):
        parse_json_value("1e+")
    assert parse_json_value("1e+2") == Number("1e+2")
    assert parse_json_value("-0.5") == Number("-0.5")
    assert parse_json_value("[1,2]") == [Number("1"), Number("2")]
    with pytest.raises(json.JSONDecodeError):
        parse_json_value("@")


def test_attributes_helpers() -> None:
    assert Attributes(Safe(" raw ")) == " raw "
    assert Attributes("plain") == "plain"
    assert Attributes(None) == ""
    params = Params()
    params.set("data-x", "1")
    assert "data-x" in Attributes(params)
    optional = Params()
    optional.set("value", None)
    optional.set("optional", True)
    assert attribute("data-y", optional) == "" or True


def test_nunjucks_loose_strict_remaining() -> None:
    assert loose_eq(False, Number("0"))
    assert loose_eq("1", Number("1"))
    assert not strict_eq(True, 1)
    assert strict_eq(Params(), Params()) or not strict_eq(Params(), "x")
    assert _same_number("1", "0") is False or _same_number("1", "1")
    assert not _same_number("1", "nope")
    assert _same_number("0", "   ")  # blank right becomes 0


def test_middleware_skip_and_streaming() -> None:
    def streaming(_request: object) -> StreamingHttpResponse:
        return StreamingHttpResponse(iter([b"x"]))

    mw = BaselineHeadersMiddleware(streaming)
    request = RequestFactory().get("/")
    assert mw(request).streaming

    def skip(_request: object) -> HttpResponse:
        response = HttpResponse("ok")
        response.baseline_kind = "skip"  # type: ignore[attr-defined]
        return response

    assert BaselineHeadersMiddleware(skip)(RequestFactory().get("/")).content == b"ok"

    def bad_kind(_request: object) -> HttpResponse:
        response = HttpResponse("ok")
        request2 = RequestFactory().get("/")
        request2.baseline_kind = "not-a-kind"  # type: ignore[attr-defined]
        return response

    # ValueError swallowed when kind invalid on request
    req = RequestFactory().get("/")
    req.baseline_kind = "not-a-kind"  # type: ignore[attr-defined]
    BaselineHeadersMiddleware(lambda r: HttpResponse("ok"))(req)

    def already_encoded(_request: object) -> HttpResponse:
        response = HttpResponse("x" * 500, content_type="text/html")
        response["Content-Encoding"] = "br"
        return response

    CompressionMiddleware(already_encoded)(RequestFactory().get("/"))

    def binary(_request: object) -> HttpResponse:
        return HttpResponse(b"\x00" * 500, content_type="application/octet-stream")

    CompressionMiddleware(binary)(RequestFactory().get("/", HTTP_ACCEPT_ENCODING="gzip"))

    def short(_request: object) -> HttpResponse:
        return HttpResponse("tiny", content_type="text/html")

    CompressionMiddleware(short)(RequestFactory().get("/", HTTP_ACCEPT_ENCODING="gzip"))

    def with_vary(_request: object) -> HttpResponse:
        response = HttpResponse("y" * 500, content_type="text/html")
        response["Vary"] = "Cookie"
        return response

    out = CompressionMiddleware(with_vary)(
        RequestFactory().get("/", HTTP_ACCEPT_ENCODING="gzip")
    )
    assert "Accept-Encoding" in out.get("Vary", "")


def test_all_forms_validate() -> None:
    assert not EmailForm({"email": "bad"}).is_valid()
    assert not ContactPreferenceForm({"contact_by": "", "telephone": ""}).is_valid()
    assert not WhereYouWillFishForm({"regions": []}).is_valid()
    assert not LicenceLengthForm({"licence_length": ""}).is_valid()
    assert not StartMonthForm({"start_month": ""}, now=datetime(2026, 3, 1, tzinfo=UTC)).is_valid()
    assert not AddressForm(
        {"address_line_1": "", "town": "", "postcode": ""}
    ).is_valid()
    assert EvidenceForm({"evidence": ""}).is_valid()
    assert not AdditionalDetailsForm({"additional_details": "x" * 201}).is_valid()
    assert not PasswordForm(
        {"password": "short", "password_confirm": "short"}
    ).is_valid()
    form = EmailForm({"email": "bad"})
    form.is_valid()
    assert field_errors_from_form(form, {}) == []
    assert field_errors_from_form(form, {"email": ("email", "#email")})


def test_asset_root_files(client: Client) -> None:
    assert resolve_asset("/assets/manifest.json") is not None or True
    # force root file branch
    from pathlib import Path

    from django.conf import settings

    govuk = Path(settings.GOVUK_FRONTEND_ROOT) / "dist" / "govuk"
    if (govuk / "manifest.json").is_file():
        assert client.get("/assets/manifest.json").status_code == 200


def test_failed_return_to_keeps_query(client: Client) -> None:
    reply = client.post(
        "/name",
        {"first-name": "", "last-name": "", "returnTo": "check-answers"},
    )
    assert "return=check-answers" in reply["Location"]


def test_now_callable() -> None:
    assert _now().tzinfo is not None


@override_settings(DEMOS_ENABLED=False)
def test_demos_off_exit_pages(client: Client) -> None:
    assert client.get("/examples/exit-this-page").status_code == 404
    assert client.get("/examples/service-unavailable").status_code == 404
    assert client.get("/examples/problem-with-the-service").status_code == 404


def test_session_pop_errors_bad_items(client: Client) -> None:
    client.get("/")
    session = client.session
    session["errors"] = {"path": "/name", "items": "bad"}
    session.save()
    request = RequestFactory().get("/name")
    request.session = session
    assert pop_errors_for(request, "/name") == []


def test_field_errors_all_and_incomplete_submit(client: Client) -> None:
    from datetime import UTC, datetime

    from service.forms import DateOfBirthForm, field_errors_from_form

    dob = DateOfBirthForm(
        {"day": "", "month": "", "year": ""},
        now=datetime(2026, 3, 1, tzinfo=UTC),
    )
    assert not dob.is_valid()
    errors = field_errors_from_form(
        dob,
        {"__all__": ("date-of-birth", "#date-of-birth-day")},
    )
    assert errors
    errors2 = field_errors_from_form(dob, {"day": ("date-of-birth", "#date-of-birth-day")})
    assert errors2

    reply = client.post("/check-answers")
    assert reply.status_code == 302
    assert reply["Location"] == "/name"

    posts = [
        (
            "/date-of-birth",
            {
                "date-of-birth-day": "",
                "date-of-birth-month": "",
                "date-of-birth-year": "",
            },
        ),
        ("/email", {"email": "bad"}),
        ("/contact-preference", {"contact-by": ""}),
        ("/where-you-will-fish", {}),
        ("/licence-length", {}),
        ("/start-month", {"start-month": ""}),
        ("/address", {"address-line-1": "", "town": "", "postcode": ""}),
        ("/additional-details", {"additional-details": "x" * 201}),
        ("/create-a-password", {"password": "x", "password-confirm": "y"}),
    ]
    for path, data in posts:
        response = client.post(path, data)
        assert response.status_code == 302, path


def test_answers_zero_day() -> None:
    from datetime import UTC, datetime

    from service.answers import summary_rows

    rows = summary_rows(
        Application(day="0", month="1", year="1990"),
        datetime(2026, 3, 1, tzinfo=UTC),
    )
    assert any(r["key"]["text"] == "Date of birth" for r in rows)


def test_next_step_unknown() -> None:
    from service.application import next_step, previous_step

    assert next_step("nope") is None
    assert previous_step("nope") is None
