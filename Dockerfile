# Multi-stage build for Render.com free tier (and local Docker).
# Stage 1: Node — install Frontend pin and compile Sass (never prebuilt min.css)
# Stage 2: Python — install deps with uv
# Stage 3: Runtime — Gunicorn + assets + baseline

FROM node:22-bookworm AS styles
WORKDIR /build
COPY package.json package-lock.json ./
RUN npm ci
COPY styles ./styles
COPY scripts ./scripts
RUN npm run build:styles

FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS python-build
WORKDIR /build
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
COPY pyproject.toml uv.lock README.md ./
COPY config ./config
COPY govuk_components ./govuk_components
COPY service ./service
COPY previews ./previews
COPY manage.py ./
RUN uv sync --frozen --no-dev --no-editable

FROM python:3.13-slim-bookworm
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=config.settings \
    DEBUG=false \
    DEMOS_ENABLED=true

COPY --from=python-build /build/.venv /app/.venv
COPY --from=styles /build/node_modules/govuk-frontend ./node_modules/govuk-frontend
COPY --from=styles /build/dist ./dist
COPY baseline ./baseline
COPY config ./config
COPY govuk_components ./govuk_components
COPY service ./service
COPY previews ./previews
COPY manage.py ./
COPY styles ./styles

EXPOSE 8000
# Render injects PORT
CMD ["sh", "-c", "gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2 --threads 2 --timeout 60"]
