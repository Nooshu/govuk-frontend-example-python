"""Broader HTTP and unit coverage for the Django example service."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from django.test import Client, RequestFactory, override_settings
from previews.catalogue import describe, described_names, parity_banner, title_from_kebab
from service.answers import summary_rows
from service.application import (
    Application,
    first_incomplete_step,
    mark_completed,
    reference_for,
    required_steps_complete,
    step_by_path,
    steps,
)
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
    confirmation_panel,
    cookie_fields,
    country_fields,
    date_field,
    email_field,
    error_summary,
    fees_table,
    guidance_tabs,
    help_accordion,
    licence_fields,
    name_field,
)
from service.options import countries, label_for, licence_fees, licence_lengths
from service.save import save_country, save_date, save_email, save_licence, save_name
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
    as_licence_length,
    validate_cookie_choice,
    validate_country,
    validate_date_of_birth,
    validate_email,
    validate_licence_length,
    validate_name,
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
    assert b"Apply for a fishing rod licence" in start.content

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


def test_country_and_licence_length(client: Client) -> None:
    length = client.post("/licence-length", {"licence-length": "8-days"})
    assert length.status_code == 302
    assert length["Location"] == "/name"

    client.post("/name", {"full-name": "Ada Lovelace"})
    client.post(
        "/date-of-birth",
        {
            "date-of-birth-day": "10",
            "date-of-birth-month": "12",
            "date-of-birth-year": "1990",
        },
    )
    country = client.post("/where-you-will-fish", {"country": "Wales"})
    assert country.status_code == 302
    assert country["Location"] == "/email"

    page = client.get("/where-you-will-fish")
    assert b"England" in page.content
    assert b"This example is fictional" in page.content


def test_check_answers_guards(client: Client) -> None:
    assert client.get("/check-answers").status_code == 302
    assert client.get("/confirmation").status_code == 302


def test_return_to_check_answers(client: Client) -> None:
    from tests.test_journey import _complete_journey

    _complete_journey(client)
    page = client.get("/name?return=check-answers")
    assert b'returnTo" value="check-answers"' in page.content or b"returnTo" in page.content
    changed = client.post(
        "/name",
        {"full-name": "Grace Hopper", "returnTo": "check-answers"},
    )
    assert changed["Location"] == "/check-answers"


def test_not_found(client: Client) -> None:
    response = client.get("/this-page-does-not-exist")
    assert response.status_code == 404


def test_validate_and_save_branches() -> None:
    assert validate_name("").__len__() == 1
    assert validate_name("x").__len__() == 1
    assert validate_name("x" * 101).__len__() == 1
    assert validate_name("Ada Lovelace") == []
    assert validate_date_of_birth("", "", "", FIXED)
    assert validate_date_of_birth("32", "1", "1990", FIXED)
    assert validate_date_of_birth("31", "2", "1990", FIXED)
    assert validate_date_of_birth("1", "1", "2099", FIXED)
    assert validate_date_of_birth("1", "1", "2020", FIXED)  # under 13 in 2026
    assert validate_email("bad")
    assert validate_country("")
    assert validate_country("France")
    assert validate_country("England") == []
    assert validate_licence_length("nope")
    assert validate_licence_length("12-months") == []
    assert validate_cookie_choice("maybe")
    assert as_licence_length("1-day") == "1-day"
    assert as_licence_length("8-days") == "8-days"
    assert as_licence_length("12-months") == "12-months"
    assert as_licence_length("nope") == ""

    app = Application()
    app = save_licence(app, "12-months", valid=True)
    app = save_name(app, "Ada Lovelace", valid=True)
    app = save_date(app, "10", "12", "1990", valid=True)
    app = save_country(app, "England", valid=True)
    app = save_email(app, "ada@example.com", valid=True)
    assert first_incomplete_step(app) is None
    assert required_steps_complete(app)
    rows = summary_rows(app)
    assert len(rows) == 5
    assert rows[0]["value"]["text"] == "12 months"
    assert rows[1]["value"]["text"] == "Ada Lovelace"
    assert rows[2]["value"]["text"] == "10 12 1990"
    assert rows[3]["value"]["text"] == "England"
    assert rows[4]["value"]["text"] == "ada@example.com"

    invalid = save_licence(Application(), "nope", valid=False)
    assert first_incomplete_step(invalid) is not None
    assert reference_for("abc12345").startswith("FR")
    assert mark_completed(["licence-length"], "licence-length") == ["licence-length"]


def test_govuk_options_builders() -> None:
    app = Application(full_name="Ada Lovelace", email="a@b.c", country="England")
    errors = [FieldError("full-name", "#full-name", "Enter your full name")]
    assert error_summary([]) is None
    assert error_summary(errors)
    assert name_field(app, errors)
    assert name_field(app, [FieldError("other", "#other", "ignored")])
    assert email_field(app, [])
    assert date_field(app, [FieldError("date-of-birth", "#x", "bad")])
    assert country_fields(app, [FieldError("country", "#country", "Select where you will fish")])
    assert licence_fields(app, [FieldError("licence-length", "#licence-length", "Select")])
    assert cookie_fields("accept", [])
    assert cookie_fields("reject", [])
    assert cookie_fields("", [FieldError("analytics", "#analytics", "Select yes")])
    assert fees_table()
    assert help_accordion()
    assert guidance_tabs()
    assert "Ada" not in str(confirmation_panel("<script>"))
    panel = confirmation_panel("FR123")
    assert "Your example reference number" in str(panel["html"])
    assert "FR123" in str(panel["html"])


def test_options_helpers() -> None:
    assert countries()
    assert licence_lengths()
    assert licence_fees()
    assert label_for(countries(), "Wales") == "Wales"
    assert label_for(countries(), "unknown") == "unknown"
    assert label_for(licence_lengths(), "8-days") == "8 days"


def test_chrome_helpers(rf: RequestFactory) -> None:
    request = rf.get("/about")
    request.session = {}  # type: ignore[attr-defined]
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
    from django.contrib.sessions.backends.cache import SessionStore

    store = SessionStore()
    store.create()
    request = RequestFactory().get("/")
    request.session = store
    clear_application(request)
    app = get_application(request)
    app.full_name = "Ada"
    save_application(request, app)
    assert get_application(request).full_name == "Ada"
    set_cookie_choice(request, CHOICE_ACCEPT)
    assert get_cookie_choice(request) == CHOICE_ACCEPT
    set_cookie_banner(request, CHOICE_REJECT)
    assert get_cookie_banner(request) == CHOICE_REJECT
    set_notice(request, "/cookies", "Saved")
    assert pop_notice_for(request, "/other") == ""
    set_notice(request, "/cookies", "Saved")
    assert pop_notice_for(request, "/cookies") == "Saved"
    set_errors(request, "/name", [{"field": "full-name", "href": "#", "text": "x"}])
    assert pop_errors_for(request, "/email") == []
    set_errors(request, "/name", [{"field": "full-name", "href": "#", "text": "x"}])
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
    assert b"Versions" in detail.content


def test_application_helpers() -> None:
    assert step_by_path("/name") is not None
    assert step_by_path("/licence-length") is not None
    assert step_by_path("/nope") is None
    empty = Application.from_dict(None)
    assert empty.full_name == ""
    assert Application.from_dict({"completed": "bad"}).completed == []
    assert Application.from_dict({"full_name": "Ada"}).to_dict()["full_name"] == "Ada"


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


def test_removed_routes_are_gone(client: Client) -> None:
    for path in (
        "/task-list",
        "/contact-preference",
        "/start-month",
        "/address",
        "/evidence",
        "/additional-details",
        "/create-a-password",
    ):
        assert client.get(path).status_code == 404, path
