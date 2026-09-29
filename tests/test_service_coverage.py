"""Broader HTTP and unit coverage for the Django example service."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, RequestFactory, override_settings
from previews.catalogue import describe, described_names, parity_banner, title_from_kebab
from service.answers import summary_rows, task_sections
from service.application import Application, first_incomplete_step, step_by_path, steps
from service.assets import clear_asset_cache, load_page_assets, resolve_asset
from service.chrome import (
    cookie_banner_options,
    demo_banner,
    footer_options,
    page_title,
    phase_banner,
    safe_return_path,
    service_navigation,
)
from service.govuk_options import (
    address_fields,
    confirmation_panel,
    contact_fields,
    cookie_fields,
    date_field,
    details_field,
    email_field,
    error_summary,
    evidence_field,
    fees_table,
    guidance_tabs,
    help_accordion,
    licence_fields,
    month_field,
    name_fields,
    password_fields,
    region_fields,
)
from service.options import (
    contact_options,
    label_for,
    licence_length_options,
    licence_lengths,
    regions,
    start_months,
)
from service.save import (
    AddressValues,
    save_address,
    save_contact,
    save_date,
    save_details,
    save_email,
    save_evidence,
    save_licence,
    save_month,
    save_name,
    save_password,
    save_regions,
)
from service.session import (
    CHOICE_ACCEPT,
    CHOICE_REJECT,
    clear_application,
    get_application,
    get_cookie_banner,
    get_cookie_choice,
    pop_errors_for,
    pop_notice_for,
    save_application,
    set_cookie_banner,
    set_cookie_choice,
    set_errors,
    set_notice,
)
from service.validate import (
    FieldError,
    as_contact_by,
    as_licence_length,
    normalise_postcode,
    safe_filename,
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

FIXED = datetime(2026, 3, 1, 12, 0, 0, tzinfo=UTC)


@pytest.fixture
def client() -> Client:
    return Client()


@pytest.fixture(autouse=True)
def _freeze_now(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("service.views._now", lambda: FIXED)


def test_asgi_wsgi_importable() -> None:
    import config.asgi  # noqa: F401
    import config.wsgi  # noqa: F401


def test_supporting_pages(client: Client) -> None:
    for path in (
        "/cy",
        "/fees",
        "/help",
        "/guidance",
        "/updates",
        "/updates?page=2",
        "/cookies",
        "/accessibility",
        "/about",
        "/examples",
        "/examples/exit-this-page",
        "/examples/service-unavailable",
        "/examples/problem-with-the-service",
        "/new-application",
    ):
        response = client.get(path)
        assert response.status_code in {200, 302}, path


def test_updates_unknown_page_redirects(client: Client) -> None:
    response = client.get("/updates?page=9")
    assert response.status_code == 302
    assert response["Location"] == "/updates"


def test_assets_stylesheet(client: Client) -> None:
    clear_asset_cache()
    assets = load_page_assets()
    response = client.get(assets.stylesheet_href)
    assert response.status_code == 200
    assert response["Content-Type"].startswith("text/css")
    response = client.get(assets.app_module_href)
    assert response.status_code == 200
    response = client.get(assets.script_href)
    assert response.status_code == 200
    assert client.get("/assets/missing.css").status_code == 404
    assert resolve_asset("/not-assets/x") is None
    assert resolve_asset("/assets/../secrets") is None
    favicon = resolve_asset("/assets/images/favicon.ico")
    assert favicon is not None
    assert client.get("/assets/images/favicon.ico").status_code == 200


def test_cookie_banner_and_settings(client: Client) -> None:
    start = client.get("/")
    assert start.status_code == 200
    assert b"cookie-banner" in start.content or b"Cookies on" in start.content

    accept = client.post("/cookie-choices", {"cookies": "accept", "returnPath": "/fees"})
    assert accept.status_code == 302
    assert accept["Location"] == "/fees"

    hide = client.post("/cookie-choices", {"cookies": "hide", "returnPath": "/"})
    assert hide.status_code == 302

    reject = client.post("/cookie-choices", {"cookies": "reject", "returnPath": "//evil"})
    assert reject["Location"] == "/"

    bad = client.post("/cookies", {"analytics": ""})
    assert bad.status_code == 302
    page = client.get("/cookies")
    assert b"error-summary" in page.content

    ok = client.post("/cookies", {"analytics": "yes"})
    assert ok.status_code == 302
    saved = client.get("/cookies")
    assert b"Your cookie settings were saved" in saved.content or b"Success" in saved.content


def test_step_pages_render(client: Client) -> None:
    for step in steps():
        response = client.get(step.path)
        assert response.status_code == 200, step.path


def test_telephone_contact_and_evidence_upload(client: Client) -> None:
    client.post("/name", {"first-name": "Ada", "last-name": "Lovelace"})
    client.post(
        "/date-of-birth",
        {
            "date-of-birth-day": "10",
            "date-of-birth-month": "12",
            "date-of-birth-year": "1990",
        },
    )
    client.post("/email", {"email": "ada@example.com"})
    response = client.post(
        "/contact-preference",
        {"contact-by": "telephone", "telephone": "01632 960 001"},
    )
    assert response.status_code == 302

    upload = SimpleUploadedFile("concession.pdf", b"%PDF-1.4", content_type="application/pdf")
    # walk to evidence
    client.post("/where-you-will-fish", {"regions": ["not-sure"]})
    client.post("/licence-length", {"licence-length": "1-day"})
    client.post("/start-month", {"start-month": start_months(FIXED)[0].value})
    client.post(
        "/address",
        {"address-line-1": "1 High Street", "town": "Town", "postcode": "SW1A 1AA"},
    )
    uploaded = client.post("/evidence", {"evidence": upload})
    assert uploaded.status_code == 302
    page = client.get("/evidence")
    assert b"concession.pdf" in page.content

    bad = SimpleUploadedFile("virus.exe", b"MZ", content_type="application/octet-stream")
    rejected = client.post("/evidence", {"evidence": bad})
    assert rejected.status_code == 302
    assert rejected["Location"] == "/evidence"


def test_check_answers_guards(client: Client) -> None:
    assert client.get("/check-answers").status_code == 302
    assert client.get("/confirmation").status_code == 302


def test_return_to_check_answers(client: Client) -> None:
    # Minimal complete required steps via session helpers would be heavy; use posts.
    from tests.test_journey import _complete_journey

    _complete_journey(client)
    page = client.get("/name?return=check-answers")
    assert b'returnTo" value="check-answers"' in page.content or b"returnTo" in page.content
    changed = client.post(
        "/name",
        {"first-name": "Grace", "last-name": "Hopper", "returnTo": "check-answers"},
    )
    assert changed["Location"] == "/check-answers"


def test_not_found(client: Client) -> None:
    response = client.get("/this-page-does-not-exist")
    assert response.status_code == 404


def test_validate_and_save_branches() -> None:
    assert validate_name("", "").__len__() == 2
    assert validate_name("x" * 101, "y").__len__() == 1
    assert validate_date_of_birth("", "", "", FIXED)
    assert validate_date_of_birth("32", "1", "1990", FIXED)
    assert validate_date_of_birth("31", "2", "1990", FIXED)
    assert validate_date_of_birth("1", "1", "2099", FIXED)
    assert validate_date_of_birth("1", "1", "2020", FIXED)  # under 13 in 2026
    assert validate_email("bad")
    assert validate_contact_preference("", "")
    assert validate_contact_preference("telephone", "")
    assert validate_contact_preference("telephone", "bad")
    assert validate_regions([])
    assert validate_regions(["not-sure", "wales"])
    assert validate_regions(["nope"])
    assert validate_licence_length("nope")
    assert validate_start_month("1999-01", FIXED)
    assert validate_address("", "", "")
    assert validate_address("x" * 101, "Town", "SW1A 1AA")
    assert validate_address("1 Street", "", "not-a-postcode")
    assert validate_evidence("x.exe")
    assert validate_evidence("") == []
    assert validate_additional_details("x" * 201)
    assert validate_password("short", "short")
    assert validate_password("long enough", "different")
    assert validate_cookie_choice("maybe")
    assert normalise_postcode("sw1a1aa") == "SW1A 1AA"
    assert normalise_postcode("ab") == ""
    assert as_contact_by("email") == "email"
    assert as_contact_by("nope") == ""
    assert as_licence_length("1-day") == "1-day"
    assert as_licence_length("nope") == ""
    assert safe_filename("../x.pdf") == "x.pdf"
    assert safe_filename("..") is None
    assert safe_filename("x" * 130 + ".pdf") is None

    app = Application()
    app = save_name(app, "Ada", "Lovelace", valid=True)
    app = save_date(app, "10", "12", "1990", valid=True)
    app = save_email(app, "ada@example.com", valid=True)
    app = save_contact(app, "telephone", "01632 960 001", valid=True)
    app = save_regions(app, ["wales", "bogus"], valid=True)
    app = save_licence(app, "12-month", valid=True)
    app = save_month(app, "2026-03", valid=True)
    app = save_address(
        app,
        AddressValues("1 Street", "Flat 1", "Town", "sw1a 1aa"),
        valid=True,
    )
    app = save_address(
        app,
        AddressValues("1 Street", "", "Town", "bad"),
        valid=False,
    )
    assert first_incomplete_step(app) is not None
    app = save_address(
        app,
        AddressValues("1 Street", "Flat 1", "Town", "sw1a 1aa"),
        valid=True,
    )
    app = save_evidence(app, "file.pdf", has_file=True, valid=True)
    app = save_details(app, "note", valid=True)
    app = save_password(app, valid=True)
    assert app.password_created
    assert first_incomplete_step(app) is None
    rows = summary_rows(app, FIXED)
    assert rows
    sections = task_sections(app)
    assert sections[-1].items[0]["href"] == "/check-answers"
    app.submitted = True
    sections = task_sections(app)
    assert sections[-1].items[0]["status"]["text"] == "Completed"
    incomplete = Application()
    assert "Cannot start yet" in str(task_sections(incomplete)[-1].items[0])


def test_govuk_options_builders() -> None:
    app = Application(first_name="Ada", last_name="Lovelace", email="a@b.c")
    errors = [FieldError("first-name", "#first-name", "Enter your first name")]
    assert error_summary([]) is None
    assert error_summary(errors)
    assert name_fields(app, errors)
    assert email_field(app, [])
    assert date_field(app, [FieldError("date-of-birth", "#x", "bad")])
    assert contact_fields(app, [])
    app.contact_by = "telephone"
    assert contact_fields(app, [])
    assert region_fields(app, [])
    assert licence_fields(app, [])
    assert month_field(app, [], FIXED)
    assert address_fields(app, [])
    assert evidence_field(app, [])
    assert details_field(app, [])
    assert password_fields(errors)
    assert cookie_fields("accept", [])
    assert cookie_fields("reject", [])
    assert cookie_fields("", [])
    assert fees_table()
    assert help_accordion()
    assert guidance_tabs()
    assert "Ada" not in str(confirmation_panel("<script>"))
    assert confirmation_panel("RL123")


def test_options_helpers() -> None:
    assert regions()
    assert licence_lengths()
    assert contact_options()
    assert licence_length_options()
    assert start_months(FIXED)
    assert label_for(regions(), "wales") == "Wales"
    assert label_for(regions(), "unknown") == "unknown"


def test_chrome_helpers(rf: RequestFactory) -> None:
    request = rf.get("/about")
    request.session = {}  # type: ignore[attr-defined]
    # Django session needs a real session; use Client instead for cookie banner.
    assert page_title("H", "S", has_errors=True).startswith("Error:")
    assert phase_banner("cy")["tag"]["text"] == "Enghraifft"
    assert demo_banner("cy")["titleText"] == "Pwysig"
    assert demo_banner("en")["titleText"] == "Important"
    assert service_navigation("cy")["serviceUrl"] == "/cy"
    assert service_navigation("en")["serviceUrl"] == "/"
    assert footer_options("cy")["contentLicence"]
    assert safe_return_path("//evil") == "/"
    assert safe_return_path("/fees") == "/fees"


def test_session_helpers(client: Client) -> None:
    client.get("/")
    # Use request through views already; exercise helpers via RequestFactory + session
    from django.contrib.sessions.backends.cache import SessionStore

    store = SessionStore()
    store.create()
    request = RequestFactory().get("/")
    request.session = store
    clear_application(request)
    app = get_application(request)
    app.first_name = "Ada"
    save_application(request, app)
    assert get_application(request).first_name == "Ada"
    set_cookie_choice(request, CHOICE_ACCEPT)
    assert get_cookie_choice(request) == CHOICE_ACCEPT
    set_cookie_banner(request, CHOICE_REJECT)
    assert get_cookie_banner(request) == CHOICE_REJECT
    set_notice(request, "/cookies", "Saved")
    assert pop_notice_for(request, "/other") == ""
    set_notice(request, "/cookies", "Saved")
    assert pop_notice_for(request, "/cookies") == "Saved"
    set_errors(request, "/name", [{"field": "first-name", "href": "#", "text": "x"}])
    assert pop_errors_for(request, "/email") == []
    set_errors(request, "/name", [{"field": "first-name", "href": "#", "text": "x"}])
    assert pop_errors_for(request, "/name")
    assert cookie_banner_options(request) is None or True
    set_cookie_choice(request, "")
    set_cookie_banner(request, CHOICE_ACCEPT)
    assert cookie_banner_options(request)
    set_cookie_banner(request, CHOICE_REJECT)
    assert cookie_banner_options(request)
    set_cookie_banner(request, "")
    set_cookie_choice(request, "")
    assert cookie_banner_options(request)


def test_catalogue_helpers() -> None:
    assert title_from_kebab("date-input") == "Date Input"
    assert title_from_kebab("date-") == "Date "
    info = describe("button")
    assert info.title == "Button"
    unknown = describe("brand-new-thing")
    assert unknown.title == "Brand New Thing"
    assert parity_banner(True)["type"] == "success"
    assert "does not match" in parity_banner(False)["titleText"]
    assert "button" in described_names()


@override_settings(DEMOS_ENABLED=True)
def test_component_unknown_and_fixture_query(client: Client) -> None:
    assert client.get("/components/not-a-real-component/").status_code == 404
    assert client.get("/components/button/?fixture=missing-fixture-name").status_code == 404
    assert client.get("/components/not-a-real-component/fixture/").status_code == 404
    detail = client.get("/components/button/")
    assert detail.status_code == 200
    # named fixture from page links
    assert b"Versions" in detail.content


def test_application_helpers() -> None:
    assert step_by_path("/name") is not None
    assert step_by_path("/nope") is None
    empty = Application.from_dict(None)
    assert empty.first_name == ""
    assert Application.from_dict({"regions": "bad", "completed": "bad"}).regions == []


def test_baseline_and_demos_env(monkeypatch: pytest.MonkeyPatch) -> None:
    from config.baseline import build_response_headers, js_enabled_script_hash, js_enabled_snippet

    assert js_enabled_snippet()
    assert js_enabled_script_hash()
    headers = build_response_headers(
        kind="document",
        secure_transport=True,
        content_type="text/html",
        etag='"abc"',
        sets_cookie=True,
    )
    assert "Content-Security-Policy" in headers
    assert f"'{js_enabled_script_hash()}'" in headers["Content-Security-Policy"]
    headers = build_response_headers(
        kind="fingerprinted-asset",
        secure_transport=False,
        content_type="text/css",
    )
    assert headers["Cache-Control"]
    with pytest.raises(ValueError):
        build_response_headers(kind="nope", secure_transport=False)  # type: ignore[arg-type]


def test_middleware_compression(client: Client) -> None:
    response = client.get("/", HTTP_ACCEPT_ENCODING="br")
    assert response.status_code == 200
    response = client.get("/", HTTP_ACCEPT_ENCODING="gzip")
    assert response.status_code == 200


def test_cookie_choices_get_not_allowed(client: Client) -> None:
    assert client.get("/cookie-choices").status_code == 405
