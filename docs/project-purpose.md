# Project purpose

This repository is a **base template** for creating **GDS-compliant** government frontends.

## Intent

Teams clone or fork this template to stand up services that:

1. Meet [Service Standard](https://www.gov.uk/service-manual/service-standard) and [Technology Code of Practice](https://www.gov.uk/guidance/the-technology-code-of-practice) expectations for common components, accessibility, and open standards — as far as the UI layer can.
2. Use **Python** and **Django** for HTML generation and application logic (native component renderers + Django Templates / Forms).
3. Use **[GOV.UK Frontend](https://frontend.design-system.service.gov.uk/)** (latest pinned release) as the **only** frontend component library — styles, progressive-enhancement JS, and macro-driven HTML.
4. Do **not** introduce SPA or component **frontend frameworks** (React, Vue, Angular, Svelte, Next.js UI layers, etc.) for rendering GOV.UK UI.
5. Derive component HTML from **GOV.UK Frontend macros** / `template.njk` via **native Python** renderers — never long-term copy-paste from each release — and wire **official test fixtures** for extensive **100% HTML parity** testing of Python output.

## Priorities

1. Frontend web performance
2. Frontend security
3. Reduced maintenance
4. Accessibility
5. Inclusive design

See [priorities.md](priorities.md).

GOV.UK Frontend remains a **Node** package with **Nunjucks** macros upstream. See [tech-stack.md](tech-stack.md).

## What “GDS compliant” means here

Follow official GDS guidance and the Design System / Frontend contracts rather than inventing parallel UI systems. Canonical places to search: [guidance-sources.md](guidance-sources.md).

Using this template does **not** by itself make a live service assessment-ready — see [service-assessment-readiness.md](service-assessment-readiness.md) and [assisted digital](https://www.gov.uk/service-manual/helping-people-to-use-your-service/assisted-digital-support-introduction).

## Agent skill

Coding agents should apply [`.cursor/skills/gds-compliant-frontend/SKILL.md`](../.cursor/skills/gds-compliant-frontend/SKILL.md) when scaffolding or reviewing work in this repo.
