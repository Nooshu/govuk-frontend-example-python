# Preview server

Local Django server for human parity checks and pattern demos.

## Status

**Python / Django** — see [tech-stack.md](tech-stack.md).

```sh
# Once: install uv — https://docs.astral.sh/uv/getting-started/installation/
curl -LsSf https://astral.sh/uv/install.sh | sh
source "$HOME/.local/bin/env"

npm ci
uv sync --all-groups
npm start
# → http://127.0.0.1:8000
```

`npm start` builds Sass then runs Django’s development server (`PORT` / `HOST` optional). It looks for `uv` on `PATH` and in `~/.local/bin`.

Demos (catalogue and `/examples`) are on when `DEBUG=true` (default locally) or `DEMOS_ENABLED=true`.

## Expectations

- Service start page links to `/components/` when demos are enabled.
- `/components/` is the component preview homepage: lists components (and patterns via `/examples`) as **links only** — no embedded live demos.
- A preview surface per component (`/components/<name>/`) loads official fixtures with ordered option keys and renders via Python `Render` (same as the parity suite), with a parity banner vs official `html`. The page leads with **Current version: …**, a **Component preview** frame (dotted border) around the rendered HTML, then a **Versions (Fixtures)** list that marks the selected entry with a Current tag.
- A raw-fixture surface (`/components/<name>/fixture/`) returns an HTML **fragment** for automation.
- Preview and fixture surfaces are Development / Testing only.
- Preview responses use the same [`baseline/`](../baseline/) headers as production. On local HTTP, HSTS is not sent.
- Health endpoint: `GET /health` → `ok`.

## After code changes

Rebuild styles with `npm run build:styles` (or restart via `npm start`, which rebuilds Sass first) if Sass changed; hard-refresh the browser. Confirm focus states, header/footer, and a failing-form example during visual QA after Frontend upgrades ([upgrading-govuk-frontend.md](upgrading-govuk-frontend.md)).
