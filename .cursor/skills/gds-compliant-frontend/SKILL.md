---
name: gds-compliant-frontend
description: >-
  Builds GDS-compliant government frontends with Python/Django and GOV.UK
  Frontend macros / fixtures as the HTML contract (native Python HTML
  generation; Node for install/Sass/fixtures only) and fixture HTML parity,
  no SPA/frontend frameworks. Use when scaffolding services, applying Service
  Standard or Technology Code of Practice guidance, implementing GOV.UK
  components/patterns, upgrading govuk-frontend, or verifying assessment-shaped UI.
---

# GDS-compliant frontend (Python / Django)

## What this project is

A **Python / Django** example for **GDS-compliant** frontends that:

- Use **Python** and **Django** for the server and HTML generation
- Use **[GOV.UK Frontend](https://frontend.design-system.service.gov.uk/)** (latest pinned version) as the **only** frontend component library
- Generate component HTML from Frontend’s macros/`template.njk` contract via **native Python** renderers. Do **not** copy-paste HTML from each Frontend release as the long-term approach, and do **not** shell out to Node solely to render HTML
- Wire official **test fixtures** for extensive **100% HTML parity** testing of Python-generated markup
- Do **not** use frontend frameworks (React, Vue, Angular, Svelte, Next.js client apps, etc.) for UI

Priorities (in order): frontend web performance → frontend security → reduced maintenance → accessibility → inclusive design. See [`docs/priorities.md`](../../../docs/priorities.md).

Detail for humans: [`docs/project-purpose.md`](../../../docs/project-purpose.md), [`docs/onboarding.md`](../../../docs/onboarding.md), [`CONTRIBUTING.md`](../../../CONTRIBUTING.md). Dual-audience map: [`docs/documentation-structure.md`](../../../docs/documentation-structure.md). Playbooks: [`AGENTS.md`](../../../AGENTS.md).

## Non-negotiable stack shape

| Layer               | Choice                                                                                              |
| ------------------- | --------------------------------------------------------------------------------------------------- |
| UI                  | GOV.UK Frontend only (`govuk-*`, official JS via `initAll()`)                                       |
| HTML generation     | Native Python renderers (`govuk_components.rendering`) tracking Frontend macros / fixture parity    |
| Framework           | Django 5.2 (Templates, Forms, sessions, CSRF)                                                       |
| Frontend frameworks | **Forbidden** for UI                                                                                |
| Parity              | Official `fixtures.json` + ordinal HTML equality against Python output                              |
| Upstream            | Node package + Nunjucks / `template.njk` / fixtures (install/Sass/freshness — not for request HTML) |

## Authoritative guidance (search these first)

1. [Technology Code of Practice](https://www.gov.uk/guidance/the-technology-code-of-practice)
2. [Assisted digital support: an introduction](https://www.gov.uk/service-manual/helping-people-to-use-your-service/assisted-digital-support-introduction)
3. [Service Standard](https://www.gov.uk/service-manual/service-standard)
4. [Service Manual](https://www.gov.uk/service-manual)
5. [GOV.UK Design System](https://design-system.service.gov.uk/)
6. [GOV.UK Frontend](https://frontend.design-system.service.gov.uk/)

Local index: [`docs/guidance-sources.md`](../../../docs/guidance-sources.md).

## Upgrading Frontend

**Pipeline gate:** do not start or finish a Frontend (or any other) dependency bump while CI is red — follow [`../safe-dependency-updates/SKILL.md`](../safe-dependency-updates/SKILL.md).

**Always** read https://github.com/alphagov/govuk-frontend/releases/latest before changing the pin, then follow [`docs/upgrading-govuk-frontend.md`](../../../docs/upgrading-govuk-frontend.md). Refresh fixtures from the same version; fix renderers/macros usage — never edit fixture `html`.

## Test coverage and HTML parity

- **Code:** 100% functions, branches, statements (CI fails below).
- **HTML (primary):** backend / library output must match official fixture `html` byte-for-byte for **every** fixture on every shipped component. See [`docs/testing-components.md`](../../../docs/testing-components.md).
- **HTML (secondary):** Nunjucks suite proves stored fixtures still match Frontend macros — freshness only; it does **not** replace backend vs fixture parity.
- Do not weaken either gate to satisfy the other; do not treat Nunjucks-only green as done.

## Workflow reminders

1. Follow the stack in [`docs/tech-stack.md`](../../../docs/tech-stack.md) (Python / Django).
2. Never hand-paste `govuk-*` component HTML; use macros / library API.
3. Upgrade only after reviewing the [latest release](https://github.com/alphagov/govuk-frontend/releases/latest), with CI green per [`safe-dependency-updates`](../safe-dependency-updates/SKILL.md).
4. New components: [`docs/creating-components.md`](../../../docs/creating-components.md). Patterns: [`docs/creating-patterns.md`](../../../docs/creating-patterns.md).
5. HTTP responses use [`baseline/`](../../../baseline/) — performance cache kinds and OWASP headers. Compress with Brotli (`br`); Gzip is only the fallback when the client does not advertise `br`. Playbooks: [`docs/frontend-performance.md`](../../../docs/frontend-performance.md), [`docs/frontend-security.md`](../../../docs/frontend-security.md). Language lines sync `baseline/`; they do not fork a weaker policy.
6. Compile CSS via Sass (`styles/application.scss` → Frontend `@use` → `govuk-overrides.scss` last). Never use `!important` in service CSS. Playbook: [`docs/styles.md`](../../../docs/styles.md).
7. Document every change for **humans and agents** in the same change set ([`docs/documentation-structure.md`](../../../docs/documentation-structure.md)). Update `/docs`, and `AGENTS.md` / skill / rules when contracts change.
8. Follow the **latest** best practices for the wrapper language in [`docs/tech-stack.md`](../../../docs/tech-stack.md) (and current Node/ESM for shared tooling). Do not fossilise outdated patterns.
9. When a coherent piece of work is finished, split it into focused commits with comprehensive messages — do not leave a large mixed working tree.
