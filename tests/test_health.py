"""Health and robots endpoint tests."""

from __future__ import annotations

import pytest
from django.test import Client


@pytest.fixture
def client() -> Client:
    return Client()


def test_health_returns_ok(client: Client) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.content == b"ok"


def test_robots_disallows_all(client: Client) -> None:
    response = client.get("/robots.txt")
    assert response.status_code == 200
    assert b"Disallow: /" in response.content
