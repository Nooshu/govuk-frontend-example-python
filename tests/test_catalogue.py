"""Component catalogue preview tests."""

from __future__ import annotations

import pytest
from django.test import Client, override_settings


@pytest.fixture
def client() -> Client:
    return Client()


@override_settings(DEMOS_ENABLED=True)
def test_catalogue_lists_components(client: Client) -> None:
    response = client.get("/components/")
    assert response.status_code == 200
    assert b"Component catalogue" in response.content
    assert b"Button" in response.content


@override_settings(DEMOS_ENABLED=True)
def test_component_detail_shows_parity_banner(client: Client) -> None:
    response = client.get("/components/button/")
    assert response.status_code == 200
    assert b"Component preview" in response.content
    content = response.content
    assert b"HTML matches the fixture" in content or b"HTML does not match" in content


@override_settings(DEMOS_ENABLED=True)
def test_raw_fixture_returns_html_fragment(client: Client) -> None:
    response = client.get("/components/button/fixture/")
    assert response.status_code == 200
    assert b"govuk-button" in response.content
