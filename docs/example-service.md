# Example service

**Apply for a rod fishing licence** is the reference GOV.UK service in this repository. It is an example. It does not take payment, send email, or issue a licence.

Every HTML page shows an **Important** notification banner (“This is a live demo. It is not a real government service.”), styled yellow via `.app-demo-banner` so it stands out from the blue header/footer, and a phase banner that repeats that it is a demonstration. Search engines are told to stay away: `meta robots` and `X-Robots-Tag` are `noindex, nofollow`, and `/robots.txt` disallows all paths.

Pages are **Django**. Component HTML comes from **native Python renderers** (`govuk_components.rendering`) that track GOV.UK Frontend macros and match every official fixture. The pin is **6.5.1**. See [tech-stack.md](tech-stack.md).

## Run it

```sh
# Once: install uv if needed — https://docs.astral.sh/uv/getting-started/installation/
curl -LsSf https://astral.sh/uv/install.sh | sh
source "$HOME/.local/bin/env"

npm ci
uv sync --all-groups
npm start
```

`npm start` compiles the Sass stylesheet, then runs Django’s development server (and syncs `.venv` via `uv` if it is missing). Opens at <http://127.0.0.1:8000>. Set `PORT` (and optionally `HOST`) to change the bind address.

Public demo hosting: [deploying-on-render.md](deploying-on-render.md).

`DEBUG=false` hides the component catalogue and the extra example pages unless `DEMOS_ENABLED=true` (set on the Render demo). The licence journey stays available.

## Start to confirmation

1. Start at `/` (English) or `/cy` (Welsh start page only). Choose **Start now**.
2. The task list at `/task-list` links to each question.
3. Answer the questions in order: name, date of birth, email, contact preference, where you will fish, licence length, start month, address, evidence (optional), additional details (optional), and password.
4. Check your answers at `/check-answers`. Change links return to a question and then come back.
5. Submit. The confirmation page at `/confirmation` shows a reference. The password is not shown.

Invalid answers redirect back to the same question, with an error summary and the values you entered (flash errors, cleared on refresh). You cannot open confirmation until the required questions are complete.

## Pages

| Path                                   | What it shows                                                                                                          |
| -------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `/` and `/cy`                          | Start page. Welsh is the start page and chrome only; the rest of the journey is in English                             |
| `/task-list`                           | Task list, then the questions, check your answers, and confirmation                                                    |
| `/fees`, `/help`, `/guidance`          | Fees table, help accordion, and guidance tabs                                                                          |
| `/updates`, `/cookies`                 | Service updates with pagination, and cookie settings                                                                   |
| `/accessibility`, `/about`             | Accessibility statement and what this example is                                                                       |
| `/components/`                         | **Component preview homepage** — every component in this Frontend release as **links only**                            |
| `/components/<name>/`                  | One component’s page: Python `Render` HTML for a fixture, with a banner saying whether it matches the official fixture |
| `/components/<name>/?fixture=`         | A named fixture on that component page                                                                                 |
| `/components/<name>/fixture/?fixture=` | The fixture HTML fragment only. For tests and debugging                                                                |
| `/examples/exit-this-page`             | Exit this page. The button leaves this example and opens the BBC weather forecast                                      |

Question pages use one `h1`, `novalidate`, an error summary, and field errors. Answers are kept when validation fails. A page uses a back link or breadcrumbs, not both. Forms use Django Forms + `{% csrf_token %}`; GOV.UK markup is rendered via `{% govuk %}`.

## Responses

Pages and assets use the shared [baseline](frontend-security.md). Public HTML that sets the session cookie is `private, no-cache`. Question, task list, check your answers, confirmation, and cookie settings pages are `no-store` (`sensitive-document`). The compiled Sass stylesheet, Frontend script, and the external `initAll()` module are fingerprinted and cached as immutable.

The server compresses with Brotli when the browser sends `Accept-Encoding: br`. Gzip is only used when the browser does not advertise `br`.

## Tests

```sh
uv run pytest -q -o addopts=
uv run pytest   # includes 100% coverage gate
```

Component tests render **every** official fixture shipped with the pinned `govuk-frontend` release. The comparison is Python `Render` output against the fixture `html` string.

## Limits

- Sessions are stored in LocMemCache and end when the process stops.
- The password is checked and then discarded. It is not stored or shown again.
- A cookie choice is stored. This example does not set analytics cookies.
- An upload stores the file name only, and only for PDF, PNG, or JPG.
- Using this repo does not make a service assessment-ready. See [service-assessment-readiness.md](service-assessment-readiness.md).
