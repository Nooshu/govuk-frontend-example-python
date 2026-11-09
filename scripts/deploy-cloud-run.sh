#!/usr/bin/env bash
# Build this repo with Cloud Build and deploy the Docker image to Cloud Run.
# Step-by-step: docs/deploying-on-cloud-run.md

set -euo pipefail

PROJECT="${PROJECT:-}"
if [[ -z "$PROJECT" ]]; then
  PROJECT="$(gcloud config get-value project 2>/dev/null || true)"
fi
if [[ -z "$PROJECT" || "$PROJECT" == "(unset)" ]]; then
  echo "Set PROJECT or run: gcloud config set project PROJECT_ID" >&2
  exit 1
fi

REGION="${REGION:-europe-west2}"
SERVICE="${SERVICE:-govuk-frontend-example-python}"
SECRET="${SECRET:-govuk-frontend-example-python-secret-key}"
MEMORY="${MEMORY:-1Gi}"
CPU="${CPU:-1}"
CONCURRENCY="${CONCURRENCY:-8}"
MIN_INSTANCES="${MIN_INSTANCES:-0}"
MAX_INSTANCES="${MAX_INSTANCES:-3}"

echo "Enabling Cloud Run, Cloud Build, Artifact Registry, and Secret Manager on ${PROJECT}"
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  --project "$PROJECT"

if ! gcloud secrets describe "$SECRET" --project "$PROJECT" >/dev/null 2>&1; then
  echo "Creating Secret Manager secret ${SECRET}"
  openssl rand -base64 48 | tr -d '\n' | gcloud secrets create "$SECRET" \
    --project "$PROJECT" \
    --replication-policy="automatic" \
    --data-file=-
else
  echo "Using existing secret ${SECRET}"
fi

project_number="$(gcloud projects describe "$PROJECT" --format='value(projectNumber)')"
runtime_sa="${RUNTIME_SA:-${project_number}-compute@developer.gserviceaccount.com}"

echo "Granting roles/secretmanager.secretAccessor to ${runtime_sa}"
gcloud secrets add-iam-policy-binding "$SECRET" \
  --project "$PROJECT" \
  --member="serviceAccount:${runtime_sa}" \
  --role="roles/secretmanager.secretAccessor" \
  --quiet >/dev/null

echo "Granting roles/run.builder to ${runtime_sa}"
for attempt in 1 2 3 4 5 6; do
  if gcloud projects add-iam-policy-binding "$PROJECT" \
    --member="serviceAccount:${runtime_sa}" \
    --role="roles/run.builder" \
    --quiet >/dev/null; then
    break
  fi
  if [[ "$attempt" -eq 6 ]]; then
    echo "Could not grant roles/run.builder" >&2
    exit 1
  fi
  sleep "$attempt"
done

echo "Deploying ${SERVICE} in ${REGION}"
gcloud run deploy "$SERVICE" \
  --source . \
  --project "$PROJECT" \
  --region "$REGION" \
  --service-account "$runtime_sa" \
  --allow-unauthenticated \
  --ingress=all \
  --port 8080 \
  --memory "$MEMORY" \
  --cpu "$CPU" \
  --concurrency "$CONCURRENCY" \
  --timeout 60 \
  --min-instances "$MIN_INSTANCES" \
  --max-instances "$MAX_INSTANCES" \
  --cpu-boost \
  --set-env-vars "^|^DEMOS_ENABLED=true|DEBUG=false|ALLOWED_HOSTS=.run.app,localhost,127.0.0.1|CSRF_TRUSTED_ORIGINS=https://*.run.app" \
  --set-secrets "SECRET_KEY=${SECRET}:latest" \
  --startup-probe="initialDelaySeconds=0,timeoutSeconds=4,periodSeconds=5,failureThreshold=36,httpGet.path=/health,httpGet.port=8080" \
  --liveness-probe="timeoutSeconds=4,periodSeconds=30,failureThreshold=3,httpGet.path=/health,httpGet.port=8080" \
  --readiness-probe="timeoutSeconds=4,periodSeconds=5,failureThreshold=3,httpGet.path=/health,httpGet.port=8080"

url="$(gcloud run services describe "$SERVICE" --project "$PROJECT" --region "$REGION" --format='value(status.url)')"
echo "Deployed ${url}"
echo "Check ${url}/health"
