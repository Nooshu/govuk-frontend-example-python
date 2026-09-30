"""Licence journey happy path and validation error tests."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from django.test import Client


@pytest.fixture
def client() -> Client:
    return Client()


def _complete_journey(client: Client) -> None:
    steps = [
        ("/licence-length", {"licence-length": "12-months"}),
        ("/name", {"full-name": "Ada Lovelace"}),
        (
            "/date-of-birth",
            {
                "date-of-birth-day": "10",
                "date-of-birth-month": "12",
                "date-of-birth-year": "1990",
            },
        ),
        ("/where-you-will-fish", {"country": "England"}),
        ("/email", {"email": "ada@example.com"}),
    ]
    for path, data in steps:
        response = client.post(path, data)
        assert response.status_code == 302, f"POST {path} = {response.status_code}"


def test_happy_path_reaches_confirmation(client: Client, monkeypatch: pytest.MonkeyPatch) -> None:
    fixed = datetime(2026, 3, 1, 12, 0, 0, tzinfo=UTC)
    monkeypatch.setattr("service.views._now", lambda: fixed)

    assert client.get("/").status_code == 200
    start = client.get("/")
    assert b"/licence-length" in start.content
    _complete_journey(client)

    check = client.get("/check-answers")
    assert check.status_code == 200
    assert b"Check your answers" in check.content
    assert b"Ada Lovelace" in check.content
    assert b"Accept and continue" in check.content
    assert b"10 12 1990" in check.content
    assert b"England" in check.content

    submit = client.post("/check-answers")
    assert submit.status_code == 302
    assert submit["Location"] == "/confirmation"

    confirmation = client.get("/confirmation")
    assert confirmation.status_code == 200
    assert b"Application complete" in confirmation.content
    assert b"Your example reference number" in confirmation.content
    assert b"Back to the component list" in confirmation.content
    assert b'href="/components"' in confirmation.content


def test_failed_name_shows_error_summary(
    client: Client, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "service.views._now",
        lambda: datetime(2026, 3, 1, 12, 0, 0, tzinfo=UTC),
    )
    reply = client.post("/name", {"full-name": ""})
    assert reply.status_code == 302
    assert reply["Location"] == "/name"

    page = client.get("/name")
    assert page.status_code == 200
    assert b"error-summary" in page.content
    assert b"<title>Error: " in page.content
    assert b"Enter your full name" in page.content

    # Errors are flash: a refresh shows a clean question.
    assert b"error-summary" not in client.get("/name").content
