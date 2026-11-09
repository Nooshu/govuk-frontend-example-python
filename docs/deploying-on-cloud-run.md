# Deploying on Google Cloud Run

Host this Django example on [Cloud Run](https://cloud.google.com/run/docs). Gunicorn binds `0.0.0.0:$PORT`. Cloud Run’s default port is 8080. TLS stops at the platform. `SECURE_PROXY_SSL_HEADER` trusts `X-Forwarded-Proto`.

You need a Google Cloud project with billing enabled, the [gcloud CLI](https://cloud.google.com/sdk/docs/install), and `openssl`. Cloud Run can scale to zero. Build minutes, Artifact Registry storage, and requests above the free tier are billed.

This service’s name is `govuk-frontend-example-python`, region `europe-west2` (London).

## What this repo includes

| File                                                            | Role                                            |
| --------------------------------------------------------------- | ----------------------------------------------- |
| [`Dockerfile`](../Dockerfile)                                   | Node Sass, uv, then Gunicorn                    |
| [`scripts/deploy-cloud-run.sh`](../scripts/deploy-cloud-run.sh) | Stores `SECRET_KEY` and deploys from source     |
| `GET /health`                                                   | Plain `ok` for startup, readiness, and liveness |

## Deploy

From the repo root, with a project selected:

```sh
gcloud config set project PROJECT_ID
./scripts/deploy-cloud-run.sh
```

| Variable        | Default                                    |
| --------------- | ------------------------------------------ |
| `PROJECT`       | gcloud’s active project                    |
| `REGION`        | `europe-west2`                             |
| `SERVICE`       | `govuk-frontend-example-python`            |
| `SECRET`        | `govuk-frontend-example-python-secret-key` |
| `MEMORY`        | `1Gi`                                      |
| `CPU`           | `1`                                        |
| `MIN_INSTANCES` | `0`                                        |
| `MAX_INSTANCES` | `3`                                        |

The script sets `DEMOS_ENABLED=true`, `DEBUG=false`, `ALLOWED_HOSTS=.run.app,localhost,127.0.0.1`, and `CSRF_TRUSTED_ORIGINS=https://*.run.app`. `SECRET_KEY` comes from Secret Manager and is reused on later deploys.

### After deploy checklist

- [ ] `https://<service>-<hash>.<region>.run.app/health` returns `ok`
- [ ] Start page loads with GOV.UK styling
- [ ] `/components` works
- [ ] A form POST in the licence journey keeps the answers on the next page

## Run the image locally

```sh
docker build -t govuk-frontend-example-python .
docker run --rm -p 8080:8080 -e PORT=8080 -e DEBUG=true -e DEMOS_ENABLED=true govuk-frontend-example-python
```

Open <http://127.0.0.1:8080>.
