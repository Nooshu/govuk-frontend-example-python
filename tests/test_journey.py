"""Licence journey happy path and validation error tests."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from django.test import Client
from service.options import start_months


@pytest.fixture
def client() -> Client:
    return Client()


def _start_month() -> str:
    return start_months(datetime(2026, 3, 1, 12, 0, 0, tzinfo=UTC))[0].value


def _complete_journey(client: Client) -> None:
    steps = [
        ("/name", {"first-name": "Ada", "last-name": "Lovelace"}),
        (
            "/date-of-birth",
            {
                "date-of-birth-day": "10",
                "date-of-birth-month": "12",
                "date-of-birth-year": "1990",
            },
        ),
        ("/email", {"email": "ada@example.com"}),
        ("/contact-preference", {"contact-by": "email"}),
        ("/where-you-will-fish", {"regions": ["north-west", "wales"]}),
        ("/licence-length", {"licence-length": "12-month"}),
        ("/start-month", {"start-month": _start_month()}),
        (
            "/address",
            {
                "address-line-1": "1 Example Street",
                "town": "Exampleton",
                "postcode": "sw1a 1aa",
            },
        ),
        ("/evidence", {}),
        ("/additional-details", {"additional-details": "Nothing else"}),
        (
            "/create-a-password",
            {"password": "correct horse", "password-confirm": "correct horse"},
        ),
    ]
    for path, data in steps:
        response = client.post(path, data)
        assert response.status_code == 302, f"POST {path} = {response.status_code}"


def test_happy_path_reaches_confirmation(client: Client, monkeypatch: pytest.MonkeyPatch) -> None:
    fixed = datetime(2026, 3, 1, 12, 0, 0, tzinfo=UTC)
    monkeypatch.setattr("service.views._now", lambda: fixed)

    assert client.get("/").status_code == 200
    assert client.get("/task-list").status_code == 200
    _complete_journey(client)

    check = client.get("/check-answers")
    assert check.status_code == 200
    assert b"Check your answers" in check.content
    assert b"Ada Lovelace" in check.content

    submit = client.post("/check-answers")
    assert submit.status_code == 302
    assert submit["Location"] == "/confirmation"

    confirmation = client.get("/confirmation")
    assert confirmation.status_code == 200
    assert b"Application complete" in confirmation.content


def test_failed_name_shows_error_summary(
    client: Client, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "service.views._now",
        lambda: datetime(2026, 3, 1, 12, 0, 0, tzinfo=UTC),
    )
    reply = client.post("/name", {"first-name": "", "last-name": ""})
    assert reply.status_code == 302
    assert reply["Location"] == "/name"

    page = client.get("/name")
    assert page.status_code == 200
    assert b"error-summary" in page.content
    assert b"<title>Error: " in page.content

    # Errors are flash: a refresh shows a clean question.
    assert b"error-summary" not in client.get("/name").content
