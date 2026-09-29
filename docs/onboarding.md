# Onboarding

Human-oriented map of this repository. Coding agents should treat [`AGENTS.md`](../AGENTS.md) as the dense entry point; humans should also read [`CONTRIBUTING.md`](../CONTRIBUTING.md). How docs are split for both audiences: [documentation-structure.md](documentation-structure.md).

## What this repo is

A **GDS-compliant** frontend example: **Python / Django** generate HTML; **GOV.UK Frontend** is the only UI library; **no frontend frameworks** for UI. Exact **HTML parity** against official Frontend fixtures. See [project-purpose.md](project-purpose.md).

**Implementation language:** **Python 3.13 + Django 5.2** with **Django Templates** and native Python renderers in `govuk_components/rendering/`. See [tech-stack.md](tech-stack.md) for layout, tooling, and conventions.

**GOV.UK Frontend** is installed from npm for CSS, JavaScript, fonts, and official `fixtures.json`. Node is used for Sass, baseline checks, and optional Nunjucks freshness — **not** for production HTML rendering in this line.

**Official guidance:** search the URLs in [guidance-sources.md](guidance-sources.md).

**Priorities:** frontend web performance → frontend security → reduced maintenance → accessibility → inclusive design ([priorities.md](priorities.md)).

**Documentation:** every lasting change is documented for **humans and agents** ([documentation-structure.md](documentation-structure.md)).

**HTML:** Python renderers track Frontend macros/`template.njk`; official fixtures drive **100% parity** tests of backend output. Do not copy-paste component HTML from each release as the long-term approach. Before Frontend upgrades, always read https://github.com/alphagov/govuk-frontend/releases/latest.

## Priorities

See [priorities.md](priorities.md). Short version: frontend web performance → frontend security → reduced maintenance → accessibility → inclusive design.

## Components vs patterns

| Kind          | What it is                                                               | How we build it                                  | Fixture parity?                                                         |
| ------------- | ------------------------------------------------------------------------ | ------------------------------------------------ | ----------------------------------------------------------------------- |
| **Component** | Design System building block (button, text input, …)                     | Library wrapper that renders exact Frontend HTML | **Yes** — official `fixtures.json`                                      |
| **Pattern**   | Guidance for a journey or page composition (addresses, check answers, …) | Compose shipped components into pages            | **No** — follow Design System guidance; no invented pattern HTML suites |

## Repo map

```text
AGENTS.md
config/                   # Django settings, baseline middleware, WSGI/ASGI
govuk_components/         # Native renderers + Django template tags
service/                  # Example rod licence journey
previews/                 # Component catalogue (when DEMOS_ENABLED)
tests/                    # pytest, fixture parity, journey coverage
baseline/                 # Shared performance + OWASP header contract
styles/                   # Sass → dist/stylesheets/application.css
docs/
```

Detail: [tech-stack.md](tech-stack.md).

## Local development

Install dependencies and run the example service:

```sh
# Once: install uv — https://docs.astral.sh/uv/getting-started/installation/
curl -LsSf https://astral.sh/uv/install.sh | sh
source "$HOME/.local/bin/env"

npm ci
uv sync --all-groups
npm start
```

Open <http://127.0.0.1:8000>. Component previews: `/components/` when demos are enabled (default in `DEBUG`).

Quality checks:

```sh
uv run ruff check .
uv run mypy
uv run pytest
npm test
npm run verify:docs
```

## Run modes

| Mode    | Purpose                                                                                   |
| ------- | ----------------------------------------------------------------------------------------- |
| Preview | `npm start` — journey + optional `/components/` catalogue                                 |
| Test    | `uv run pytest` (parity, journey, 100% coverage) + `npm test` (baseline, Sass)            |
| Verify  | CI: Ruff, mypy, pytest, Node tests, `npm run verify:docs`                                 |
| Upgrade | Mechanical Frontend bump — see [upgrading-govuk-frontend.md](upgrading-govuk-frontend.md) |

## Testing mindset

1. **Parity checks (primary)** compare **backend / library** output to fixture `html` with ordinal string equality — every fixture from the pinned Frontend release.
2. **Nunjucks suite (secondary)** compares Frontend macros to stored fixture `html` to catch **stale fixtures** only.
3. **Never** edit fixture `html` to make tests pass — fix the renderer.
4. **Never** normalise HTML in tests.
5. A green Nunjucks suite alone does **not** prove the backend language is correct.

Details: [testing-components.md](testing-components.md).

## Troubleshooting

| Symptom                        | Likely cause                                                |
| ------------------------------ | ----------------------------------------------------------- |
| Parity fails on whitespace     | Renderer ≠ Nunjucks `template.njk` / `{%-` stripping        |
| Encoding differs (`'` vs `'`)  | Used framework HTML encoder instead of Nunjucks `escape`    |
| Attribute order differs        | Built attributes in code property order, not template order |
| Preview/fixture 404 in tests   | Test host not enabling Dev/Testing routes                   |
| Logo unreadable / wrong header | Frontend 5 header classes with Frontend 6+ CSS              |
| Editing fixtures “fixes” tests | Wrong fix — update renderer                                 |

More pitfalls: [creating-components.md](creating-components.md).

## Consistency tooling

Node tooling keeps docs, Sass, and baseline checks consistent alongside Python:

```sh
npm ci
npm run build:styles # Sass → dist/stylesheets/application.css
npm test             # baseline headers + Sass pipeline
npm run verify:docs  # Prettier + markdownlint
npm run verify       # docs + build:styles + tests
```

See [CONTRIBUTING.md](../CONTRIBUTING.md). Dotfiles: `.editorconfig`, `.prettierrc.json`, `.markdownlint-cli2.jsonc`, `.nvmrc`, `.vscode/`, `.cursor/rules/`, `.github/`.

## Next reads

1. [documentation-structure.md](documentation-structure.md)
2. [tech-stack.md](tech-stack.md)
3. [page-shell.md](page-shell.md) and [layout-chrome.md](layout-chrome.md)
4. [govuk-components.md](govuk-components.md)
5. [service-assessment-readiness.md](service-assessment-readiness.md)
6. [frontend-performance.md](frontend-performance.md) and [frontend-security.md](frontend-security.md)
7. [styles.md](styles.md)
8. [upgrading-govuk-frontend.md](upgrading-govuk-frontend.md)
