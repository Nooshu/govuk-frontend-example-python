"""Fixture HTML parity: backend Render output must match every official fixture."""

from __future__ import annotations

from pathlib import Path

import pytest
from govuk_components.rendering import (
    Components,
    Render,
    fixture_components,
    load_fixtures,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
COMPONENTS_DIR = (
    REPO_ROOT / "node_modules" / "govuk-frontend" / "dist" / "govuk" / "components"
)


def _components_dir() -> Path:
    if not COMPONENTS_DIR.is_dir():
        pytest.fail(
            "GOV.UK Frontend is not installed; run `npm install` "
            f"(missing {COMPONENTS_DIR})"
        )
    return COMPONENTS_DIR


def _difference(want: str, got: str) -> str:
    want_lines = want.split("\n")
    got_lines = got.split("\n")
    for i in range(max(len(want_lines), len(got_lines))):
        want_line = want_lines[i] if i < len(want_lines) else "<missing line>"
        got_line = got_lines[i] if i < len(got_lines) else "<missing line>"
        if want_line != got_line:
            return (
                f"first difference on line {i + 1}\n"
                f"want: {want_line!r}\n"
                f"got:  {got_line!r}"
            )
    return f"line-by-line equal but strings differ\nwant: {want!r}\ngot:  {got!r}"


def _all_fixtures() -> list[tuple[str, str, object]]:
    root = _components_dir()
    cases: list[tuple[str, str, object]] = []
    for component in fixture_components(root):
        fixture_set = load_fixtures(root, component)
        for fixture in fixture_set.fixtures:
            cases.append((component, fixture.name, fixture))
    return cases


@pytest.mark.parametrize(
    ("component", "fixture_name", "fixture"),
    _all_fixtures(),
    ids=lambda v: v if isinstance(v, str) else getattr(v, "name", repr(v)),
)
def test_render_matches_fixture(component: str, fixture_name: str, fixture: object) -> None:
    got = Render(component, fixture.options)  # type: ignore[attr-defined]
    if got != fixture.html:  # type: ignore[attr-defined]
        pytest.fail(
            f"HTML does not match fixture {component}/{fixture_name}\n"
            + _difference(fixture.html, got)  # type: ignore[attr-defined]
        )


def test_components_cover_every_fixture_component() -> None:
    root = _components_dir()
    shipped = fixture_components(root)
    supported = set(Components())
    missing = [name for name in shipped if name not in supported]
    assert not missing, f"components ship fixtures but have no renderer: {missing}"


def test_render_rejects_unknown_component() -> None:
    with pytest.raises(ValueError, match="not a GOV.UK Frontend component"):
        Render("not-a-component", None)
