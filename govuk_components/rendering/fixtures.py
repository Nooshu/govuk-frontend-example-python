"""Fixture loading helpers used by the parity suite.

Tracks GOV.UK Frontend Nunjucks macros / ``template.njk`` for fixture HTML parity.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .nunjucks import is_undefined, items
from .params import Params, parse_json_value


@dataclass
class Fixture:
    """One entry from a component's fixtures.json."""

    name: str
    options: Params
    hidden: bool = False
    description: str = ""
    html: str = ""


@dataclass
class FixtureSet:
    """A component's whole fixtures.json file."""

    component: str
    fixtures: list[Fixture] = field(default_factory=list)


def fixture_components(components_dir: str | Path) -> list[str]:
    """Return sorted component names under components_dir that ship a fixtures.json."""
    root = Path(components_dir)
    names: list[str] = []
    try:
        entries = sorted(root.iterdir(), key=lambda p: p.name)
    except OSError as exc:
        raise OSError(f"govuk: reading {root}: {exc}") from exc
    for entry in entries:
        if not entry.is_dir():
            continue
        if (entry / "fixtures.json").is_file():
            names.append(entry.name)
    return names


def load_fixtures(components_dir: str | Path, component: str) -> FixtureSet:
    """Read one component's fixtures.json; options stay as Params."""
    path = Path(components_dir) / component / "fixtures.json"
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise OSError(f"govuk: reading {path}: {exc}") from exc

    data = parse_json_value(raw)
    if not isinstance(data, Params):
        raise ValueError(f"govuk: parsing {path}: expected a JSON object")

    component_name = data.get("component")
    if is_undefined(component_name) or component_name is None:
        component_name = component
    else:
        component_name = str(component_name)

    fixtures: list[Fixture] = []
    for item in items(data.get("fixtures")):
        if not isinstance(item, Params):
            continue
        options = item.get("options")
        if not isinstance(options, Params):
            options = Params()

        hidden = item.get("hidden")
        if not isinstance(hidden, bool):
            hidden = False

        name = item.get("name")
        description = item.get("description")
        html = item.get("html")
        fixtures.append(
            Fixture(
                name="" if is_undefined(name) or name is None else str(name),
                options=options,
                hidden=hidden,
                description=(
                    "" if is_undefined(description) or description is None else str(description)
                ),
                html="" if is_undefined(html) or html is None else str(html),
            )
        )

    return FixtureSet(component=component_name, fixtures=fixtures)
