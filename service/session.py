"""Session helpers — application state lives in ``request.session`` as a dict."""

from __future__ import annotations

from typing import Any

from django.http import HttpRequest

from service.application import Application

SESSION_APPLICATION = "application"
SESSION_COOKIE_CHOICE = "cookie_choice"
SESSION_COOKIE_BANNER = "cookie_banner"
SESSION_NOTICE = "notice"
SESSION_ERRORS = "errors"

CHOICE_ACCEPT = "accept"
CHOICE_REJECT = "reject"


def get_application(request: HttpRequest) -> Application:
    raw = request.session.get(SESSION_APPLICATION)
    if isinstance(raw, dict):
        return Application.from_dict(raw)
    return Application()


def save_application(request: HttpRequest, application: Application) -> None:
    request.session[SESSION_APPLICATION] = application.to_dict()
    request.session.modified = True


def clear_application(request: HttpRequest) -> None:
    request.session[SESSION_APPLICATION] = Application().to_dict()
    request.session.modified = True


def get_cookie_choice(request: HttpRequest) -> str:
    return str(request.session.get(SESSION_COOKIE_CHOICE) or "")


def set_cookie_choice(request: HttpRequest, choice: str) -> None:
    request.session[SESSION_COOKIE_CHOICE] = choice
    request.session.modified = True


def get_cookie_banner(request: HttpRequest) -> str:
    return str(request.session.get(SESSION_COOKIE_BANNER) or "")


def set_cookie_banner(request: HttpRequest, value: str) -> None:
    request.session[SESSION_COOKIE_BANNER] = value
    request.session.modified = True


def get_notice(request: HttpRequest) -> dict[str, Any] | None:
    notice = request.session.get(SESSION_NOTICE)
    return notice if isinstance(notice, dict) else None


def set_notice(request: HttpRequest, path: str, text: str) -> None:
    request.session[SESSION_NOTICE] = {"path": path, "text": text}
    request.session.modified = True


def clear_notice(request: HttpRequest) -> None:
    request.session.pop(SESSION_NOTICE, None)
    request.session.modified = True


def pop_notice_for(request: HttpRequest, path: str) -> str:
    notice = get_notice(request)
    if not notice or notice.get("path") != path:
        return ""
    clear_notice(request)
    return str(notice.get("text") or "")


def set_errors(request: HttpRequest, path: str, items: list[dict[str, str]]) -> None:
    request.session[SESSION_ERRORS] = {"path": path, "items": items}
    request.session.modified = True


def clear_errors(request: HttpRequest) -> None:
    request.session.pop(SESSION_ERRORS, None)
    request.session.modified = True


def pop_errors_for(request: HttpRequest, path: str) -> list[dict[str, str]]:
    raw = request.session.get(SESSION_ERRORS)
    if not isinstance(raw, dict) or raw.get("path") != path:
        return []
    clear_errors(request)
    items = raw.get("items") or []
    if not isinstance(items, list):
        return []
    result: list[dict[str, str]] = []
    for item in items:
        if isinstance(item, dict):  # pragma: no branch
            result.append(
                {
                    "field": str(item.get("field") or ""),
                    "href": str(item.get("href") or ""),
                    "text": str(item.get("text") or ""),
                }
            )
    return result
