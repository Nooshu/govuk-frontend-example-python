# Tech stack

**Status: confirmed** — Python 3.13 + Django 5.2

The example implementation language is **Python**. HTML for GOV.UK Frontend components is generated **natively** in Python (tracking Frontend Nunjucks macros / `template.njk`). Pages, forms, sessions, CSRF, URLs, and tests use **Django**. Shared Node tooling remains for `govuk-frontend`, Sass, baseline/docs tests, and optional Nunjucks freshness checks.

## Two layers

| Layer                          | Stack                                                                                               | Notes                                                                                                                                      |
| ------------------------------ | --------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| **GOV.UK Frontend (upstream)** | **Node** package (`govuk-frontend`), **Nunjucks** macros (`template.njk`), official `fixtures.json` | Fixed by GDS. Always name Node/Nunjucks when discussing install, fixtures, macro options, escape behaviour, and verifying stored fixtures. |
| **This line (wrapper)**        | **Python 3.13**, **Django 5.2**, Django Templates + native `govuk_components.rendering`             | No React/Vue/Angular/Svelte. Do **not** shell out to Node for request-time HTML.                                                           |

## Rule for agents and humans

Every feature and code change must follow **current Django and Python best practices** (project layout, typing, apps, forms, CBVs, sessions, CSRF, pytest-django, Ruff, mypy) while honouring Frontend’s fixture contract in [`AGENTS.md`](../AGENTS.md). Prefer Django’s built-ins over custom replacements.

**HTML generation:**

- Component HTML: `govuk_components.rendering.Render` (Nunjucks-parity escape and attribute order).
- Pages: Django Templates + `{% govuk %}` template tags that call `Render`.
- Journey validation: **Django Forms** + `FormView` (or equivalent CBVs).
- Sessions: **Django cache sessions** (`LocMemCache`) — no Postgres required.
- CSRF: **Django CSRF** middleware + `{% csrf_token %}`.

Do **not** maintain hand-copied HTML dumps from each release as the long-term source.

## Consistency tooling

```sh
npm install                 # govuk-frontend + Sass
npm run build:styles        # styles/application.scss → dist/stylesheets/application.css
uv sync --all-groups        # Python deps (Django, pytest, ruff, mypy, …)
uv run pytest               # parity + HTTP tests; 100% coverage gate
uv run ruff check .
uv run mypy
npm test                    # baseline + Sass pipeline (Node)
npm run verify:docs
```

Combined gate: `npm run verify` (docs + styles + Node tests) and `uv run pytest` (Django/parity). CI runs both.

## Shared baseline

[`baseline/`](../baseline/) is the response-header contract. Python loads [`baseline/policy.json`](../baseline/policy.json) in [`config/baseline.py`](../config/baseline.py) and applies it via middleware. Production HTTPS uses `secure_transport=True` (detect `X-Forwarded-Proto` on Render).

## Styles (Sass — not prebuilt CSS)

Compile via the Sass pipeline only:

1. [`styles/application.scss`](../styles/application.scss) — `@use 'pkg:govuk-frontend'`
2. [`styles/govuk-overrides.scss`](../styles/govuk-overrides.scss) — **last** in the cascade; specificity only, **never** `!important`
3. Output: `dist/stylesheets/application.css` via `npm run build:styles`

Do **not** serve `govuk-frontend.min.css` as the long-term stylesheet.

## Version pin

| Item                    | Value                                                                                                        |
| ----------------------- | ------------------------------------------------------------------------------------------------------------ |
| Implementation language | Python 3.13                                                                                                  |
| Web framework           | Django 5.2 LTS                                                                                               |
| Templating / components | Django Templates + native `govuk_components.rendering` (fixture parity)                                      |
| Package manager         | `uv` (`pyproject.toml` + `uv.lock`)                                                                          |
| `govuk-frontend` (Node) | `6.5.1` — check [latest release](https://github.com/alphagov/govuk-frontend/releases/latest) before upgrades |
| Sass pipeline           | `styles/application.scss` → `npm run build:styles` → `dist/stylesheets/application.css`                      |
| Parity suite            | `uv run pytest tests/test_fixture_parity.py` — backend HTML ≡ every fixture `html`                           |
| Coverage                | 100% functions / branches / statements (`pytest-cov`, `--cov-fail-under=100`)                                |
| Deploy                  | Docker on Render.com free tier (`Dockerfile`, `render.yaml`)                                                 |
| Page template reference | https://design-system.service.gov.uk/styles/page-template/                                                   |
| Fixture testing guide   | https://frontend.design-system.service.gov.uk/testing-your-html/                                             |

## Hard constraints (always)

- GOV.UK Frontend pins a single version; CSS/JS and fixtures must match.
- Backend output must pass **100% HTML fixture parity** (byte-for-byte vs official fixture `html`).
- Compile CSS via Sass; `govuk-overrides.scss` last; never `!important` in service CSS.
- Prefer Django Forms, sessions, CSRF, CBVs, and the test client over bespoke equivalents.
- No frontend UI frameworks for GOV.UK chrome.

See [`AGENTS.md`](../AGENTS.md), [guidance-sources.md](guidance-sources.md), and [creating-components.md](creating-components.md).
