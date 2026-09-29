"""GOV.UK Frontend native HTML rendering for Django (fixture parity with official macros)."""

from __future__ import annotations

from govuk_components.rendering.fixtures import (
    Fixture,
    FixtureSet,
    fixture_components,
    load_fixtures,
)
from govuk_components.rendering.params import Params, Safe, Undefined, new_params, parse_json
from govuk_components.rendering.render import Components, MustRender, Render

__all__ = [
    "Components",
    "Fixture",
    "FixtureSet",
    "MustRender",
    "Params",
    "Render",
    "Safe",
    "Undefined",
    "fixture_components",
    "load_fixtures",
    "new_params",
    "parse_json",
]
