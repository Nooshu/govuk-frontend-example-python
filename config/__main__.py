"""Entry point for `govuk-example` / gunicorn-friendly local runs."""

from __future__ import annotations

import os


def main() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    from django.core.management import execute_from_command_line

    port = os.environ.get("PORT", "8000")
    execute_from_command_line(["manage.py", "runserver", f"0.0.0.0:{port}"])


if __name__ == "__main__":
    main()
