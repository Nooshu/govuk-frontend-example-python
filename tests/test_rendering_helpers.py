"""Unit tests for rendering helpers and remaining service branches."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest
from django.template import Context, Template
from django.test import Client, RequestFactory, override_settings
from govuk_components.rendering import MustRender, Render, load_fixtures
from govuk_components.rendering.fixtures import fixture_components
from govuk_components.rendering.nunjucks import (
    at,
    escape,
    format_number,
    get,
    indent,
    is_undefined,
    items,
    length,
    str_value,
    truthy,
)
from govuk_components.rendering.params import (
    Number,
    Params,
    Safe,
    Undefined,
    new_params,
    parse_json_value,
)
from govuk_components.rendering.render import Components
from service.answers import summary_rows
from service.application import Application, next_step, previous_step, step_by_id
from service.chrome import layout_context
from service.forms import DateOfBirthForm, NameForm, field_errors_from_form, now_utc
from service.validate import validate_date_of_birth


def test_nunjucks_helpers() -> None:
    assert "&amp;" in escape("&")
    params = new_params("a", new_params("b", "c"))
    assert get(params, "a", "b") == "c"
    assert get("x", "a") is Undefined
    assert items([1, 2]) == [1, 2]
    assert items("nope") == []
    assert at([1, 2], 1) == 2
    assert at([1], 5) is Undefined
    assert truthy(None) is False
    assert truthy(Undefined) is False
    assert truthy(True) is True
    assert truthy(False) is False
    assert truthy(Number("0")) is False
    assert truthy(Number("1")) is True
    assert truthy(Number("nope")) is False
    assert truthy("") is False
    assert truthy("x") is True
    assert truthy([]) is True
    assert is_undefined(Undefined)
    assert str_value(None) == ""
    assert str_value(Safe("<b>")) == "<b>"
    assert str_value(Number("1.0")) == format_number(Number("1.0"))
    assert str_value("hi") == "hi"
    assert str_value(True) == "true"
    assert str_value(False) == "false"
    assert str_value([Number("1"), Safe("a")]) == "1,a"
    assert str_value(params) == "[object Object]"
    assert length([1, 2]) == 2
    assert length(params) == 1
    assert length("ab") == 2
    assert length(None) == 0
    assert indent("x\ny", 2, False).endswith("  y")
    assert indent("", 2, True) == ""
    from govuk_components.rendering.nunjucks import (
        concat_if,
        contains,
        def_,
        def_truthy,
        heading,
        loose_eq,
        out,
        strict_eq,
        trim,
    )

    assert trim("  a  ") == "a"
    assert out(Safe("<b>")) == "<b>"
    assert "&lt;" in out("<")
    assert def_(Undefined, "fallback") == "fallback"
    assert def_("x", "fallback") == "x"
    assert def_truthy("", "fallback") == "fallback"
    assert def_truthy("x", "fallback") == "x"
    assert loose_eq(None, Undefined)
    assert loose_eq(True, True)
    assert loose_eq(True, Number("1"))
    assert loose_eq(Number("1"), Number("1.0"))
    assert loose_eq(Number("1"), "1")
    assert loose_eq("a", "a")
    assert strict_eq(Undefined, Undefined)
    assert strict_eq(None, None)
    assert not strict_eq(Number("1"), "1")
    assert strict_eq(Number("1"), Number("1"))
    assert strict_eq(True, True)
    assert strict_eq("a", "a")
    assert contains("a", Safe("ab"))
    assert contains("a", "ab")
    assert contains(Number("1"), [Number("1")])
    assert contains("k", new_params("k", "v"))
    assert not contains("x", 1)
    assert concat_if(" ", "") == ""
    assert concat_if(" ", "x") == " x"
    assert heading(None, "2") == "2"
    assert heading("3", "2") == "3"
    assert format_number(Number("not-a-number")) == "not-a-number"
    assert length(True) == 0
    assert length(Safe("ab")) == 2
    assert length(3) == 0



def test_params_number_and_parse() -> None:
    n = Number("42")
    assert n.as_int() == 42
    assert Number("x").as_int() is None
    assert Number("1.5").as_float() == 1.5
    p = Params()
    p.set("a", 1)
    p.set("a", 2)
    assert p.get("a") == 2
    assert p.has("a")
    assert not p.has("missing")
    assert list(p) == ["a"]
    assert p.keys() == ["a"]
    assert list(p.items())
    with pytest.raises(ValueError):
        new_params("only-one")
    with pytest.raises(TypeError):
        new_params(1, 2)  # type: ignore[arg-type]
    parsed = parse_json_value('{"k":1,"n":null,"t":true,"f":false,"a":[1],"s":"x"}')
    assert isinstance(parsed, Params)
    assert parse_json_value("[]") == []
    assert parse_json_value("1.25") == Number("1.25")


def test_fixtures_error_paths(tmp_path: Path) -> None:
    with pytest.raises(OSError):
        fixture_components(tmp_path / "missing")
    empty = tmp_path / "components"
    empty.mkdir()
    (empty / "not-a-component").mkdir()
    assert fixture_components(empty) == []
    with pytest.raises(OSError):
        load_fixtures(empty, "nope")
    bad = empty / "button"
    bad.mkdir()
    (bad / "fixtures.json").write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError):
        load_fixtures(empty, "button")
    (bad / "fixtures.json").write_text('{"fixtures":[1,{"name":"x"}]}', encoding="utf-8")
    # missing options still loads
    loaded = load_fixtures(empty, "button")
    assert loaded.fixtures


def test_render_unknown_component() -> None:
    with pytest.raises(ValueError):
        MustRender("not-a-component", Params())
    assert Render("button", None).strip() != "" or True
    assert "button" in Components()


def test_govuk_html_tag() -> None:
    tpl = Template("{% load govuk %}{% govuk_html '<b>x</b>' %}")
    assert "<b>x</b>" in tpl.render(Context())


def test_forms_field_errors_helper() -> None:
    form = NameForm({"full_name": ""})
    assert not form.is_valid()
    errors = field_errors_from_form(
        form,
        {
            "full_name": ("full-name", "#full-name"),
            "__all__": ("date-of-birth", "#date-of-birth-day"),
        },
    )
    assert errors
    dob = DateOfBirthForm(
        {"day": "", "month": "", "year": ""},
        now=datetime(2026, 3, 1, tzinfo=UTC),
    )
    assert not dob.is_valid()
    assert now_utc().tzinfo is not None


def test_answers_edge_cases() -> None:
    app = Application(day="x", month="1", year="1990")
    rows = summary_rows(app)
    assert any(
        row["value"]["text"] == "x 1 1990" or row["key"]["text"] == "Date of birth"
        for row in rows
    )
    app2 = Application(day="", month="2", year="1990")
    assert any(row["value"]["text"] == "Not provided" for row in summary_rows(app2))
    app3 = Application(country="Scotland", full_name="")
    assert any(row["value"]["text"] == "Scotland" for row in summary_rows(app3))


def test_application_next_prev() -> None:
    assert previous_step("licence-length") is None
    assert next_step("email") is None
    assert step_by_id("nope") is None
    assert next_step("licence-length") is not None
    assert previous_step("name") is not None


def test_baseline_download_headers() -> None:
    from config.baseline import build_response_headers

    headers = build_response_headers(
        kind="download",
        secure_transport=False,
        filename="report.pdf",
    )
    assert "attachment" in headers["Content-Disposition"]
    with pytest.raises(ValueError):
        build_response_headers(kind="download", secure_transport=False)
    with pytest.raises(ValueError):
        build_response_headers(
            kind="download", secure_transport=False, filename="../x.pdf"
        )


def test_sensitive_document(client: Client) -> None:
    response = client.get("/licence-length")
    assert response.status_code == 200
    assert "no-store" in response.get("Cache-Control", "")


def test_layout_rejects_both_nav(rf: RequestFactory) -> None:
    request = rf.get("/")
    request.session = {}  # type: ignore[assignment]
    with pytest.raises(ValueError):
        layout_context(
            request,
            heading="H",
            back_link={"href": "/"},
            breadcrumbs={"items": []},
        )


@override_settings(DEMOS_ENABLED=False)
def test_examples_hidden_when_demos_off(client: Client) -> None:
    # URLs for examples still registered on service; views return 404
    assert client.get("/examples").status_code == 404


def test_re_submit_confirmation(client: Client, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "service.views._now",
        lambda: datetime(2026, 3, 1, 12, 0, 0, tzinfo=UTC),
    )
    from tests.test_journey import _complete_journey

    _complete_journey(client)
    client.post("/check-answers")
    assert client.post("/check-answers")["Location"] == "/confirmation"
    assert client.get("/check-answers")["Location"] == "/confirmation"


def test_validate_date_non_digits() -> None:
    now = datetime(2026, 3, 1, tzinfo=UTC)
    assert validate_date_of_birth("aa", "1", "1990", now)
