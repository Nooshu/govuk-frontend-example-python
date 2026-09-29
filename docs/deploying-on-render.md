# Deploying on Render.com

Host the Django example service on [Render](https://render.com) as a public demo. This line is a normal WSGI process (Gunicorn) — not a static site — so use a **Web Service** with the committed **Dockerfile**.

Authoritative Render docs: [Language support](https://render.com/docs/language-support), [Blueprints](https://render.com/docs/blueprint-spec), [Deploy a Docker app](https://render.com/docs/docker).

## What this repo already includes

| File                            | Role                                                     |
| ------------------------------- | -------------------------------------------------------- |
| [`render.yaml`](../render.yaml) | Blueprint: free Docker web service, `/health` check      |
| [`Dockerfile`](../Dockerfile)   | Multi-stage: Node Sass → `uv` install → Gunicorn runtime |
| `GET /health`                   | Plain `ok` for Render health checks                      |

Build artefacts kept at runtime: `.venv`, `node_modules/govuk-frontend`, `dist/stylesheets/application.css`, `baseline/`.

## Prerequisites

1. A [GitHub](https://github.com) account with this repo (or a fork) pushed to `main`.
2. A [Render](https://render.com) account (free tier is enough for a demo).
3. Local checks green before you deploy: `npm ci && npm run build:styles && uv run pytest -q -o addopts=`.

## Option A — Blueprint (recommended)

Uses the committed [`render.yaml`](../render.yaml).

1. **Push this repo to GitHub**, including `render.yaml` and `Dockerfile`.
2. Open the [Render Dashboard](https://dashboard.render.com/) and sign in.
3. Click **New +** → **Blueprint**.
4. Select the repository and confirm Render detects `render.yaml`.
5. Review the service name (`govuk-frontend-example-python`), free plan, and health check `/health`.
6. Click **Apply** / **Create** and wait for the first Docker build.
7. When **Live**, open the `.onrender.com` URL.

### After deploy checklist

- [ ] `https://<your-service>.onrender.com/health` returns `ok`
- [ ] Start page loads with GOV.UK styling (`/`)
- [ ] Component catalogue works (`/components/`) — Blueprint sets `DEMOS_ENABLED=true`
- [ ] Start page shows the **Important** demo warning and **Developer previews**
- [ ] `/robots.txt` disallows `/`
- [ ] A form POST in the licence journey retains the session (cookie)

## Option B — Manual Web Service

1. **New +** → **Web Service** → Docker.
2. Connect the GitHub repo and branch `main`.
3. Set **Health Check Path** to `/health`.
4. Environment:

   | Key             | Value                               |
   | --------------- | ----------------------------------- |
   | `DEMOS_ENABLED` | `true`                              |
   | `DEBUG`         | `false`                             |
   | `ALLOWED_HOSTS` | `.onrender.com,localhost,127.0.0.1` |
   | `SECRET_KEY`    | Generate on Render                  |

## Environment variables

| Variable               | Required | Default / behaviour                                   |
| ---------------------- | -------- | ----------------------------------------------------- |
| `PORT`                 | Injected | Render sets this; Gunicorn binds `0.0.0.0:$PORT`      |
| `DEMOS_ENABLED`        | No       | Blueprint sets `true` so catalogue/previews stay on   |
| `DEBUG`                | No       | Blueprint sets `false`                                |
| `SECRET_KEY`           | Yes      | Generate on Render                                    |
| `ALLOWED_HOSTS`        | Yes      | Include `.onrender.com`                               |
| `CSRF_TRUSTED_ORIGINS` | No       | Set to `https://<service>.onrender.com` if CSRF fails |

HTTPS terminates at Render. The app treats `X-Forwarded-Proto: https` as secure.

## Free plan behaviour

The service may **spin down** after idle time; the first request after idle can take ~30–60s (cold start). Sessions are in-memory LocMemCache (not durable across instances or restarts).

## Troubleshooting

### `sh: 1: gunicorn: not found`

The runtime image must run the Gunicorn console script from `/app/.venv/bin`. The Python build stage installs into **`/app/.venv`** (same path as the final stage) so shebangs and `pyvenv.cfg` stay valid after `COPY`. Do not install the venv under a different build `WORKDIR` (for example `/build`) and then copy it to `/app` — Linux then reports the entry point as “not found” because the interpreter path is broken.

Confirm the Dockerfile `CMD` uses `/app/.venv/bin/gunicorn` (or `PATH` with that `bin` directory first).
