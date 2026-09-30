"""Shared page chrome options (header, footer, banners) for the Django page shell."""

from __future__ import annotations

from typing import Any

from django.conf import settings
from django.http import HttpRequest
from govuk_components.rendering import Render
from govuk_components.rendering.params import Safe, params_from_mapping

from service.session import (
    CHOICE_ACCEPT,
    CHOICE_REJECT,
    get_cookie_banner,
    get_cookie_choice,
)


def page_title(heading: str, service_name: str, *, has_errors: bool = False) -> str:
    prefix = "Error: " if has_errors else ""
    return f"{prefix}{heading} – {service_name}"


def crumbs(current: str) -> dict[str, Any]:
    return {
        "items": [
            {"href": "/", "text": "Home"},
            {"text": current},
        ]
    }


def phase_banner(lang: str) -> dict[str, Any]:
    if lang == "cy":
        return {
            "tag": {"text": "Enghraifft"},
            "html": Safe(
                "Mae hon yn arddangosiad – nid gwasanaeth llywodraeth byw mohono. "
                'Bydd eich <a class="govuk-link" href="/about">adborth</a> yn helpu '
                "i wella’r enghraifft."
            ),
        }
    return {
        "tag": {"text": "Example"},
        "html": Safe(
            "This is a demonstration – it is not a live government service. Your "
            '<a class="govuk-link" href="/about">feedback</a> will help us improve the example.'
        ),
    }


def demo_banner(lang: str) -> dict[str, Any]:
    banner: dict[str, Any] = {
        "classes": "app-demo-banner",
        "titleId": "app-demo-banner-title",
    }
    if lang == "cy":
        banner["titleText"] = "Pwysig"
        banner["text"] = (
            "Mae hwn yn arddangosiad byw. Nid gwasanaeth llywodraeth go iawn mohono."
        )
    else:
        banner["titleText"] = "Important"
        banner["text"] = "This is a live demo. It is not a real government service."
    return banner


def feedback_options() -> dict[str, Any]:
    return {
        "titleText": "Help us improve this service",
        "html": Safe(
            '<p class="govuk-body">This example does not send feedback. '
            '<a class="govuk-link" href="/help">Get help with this example</a>.</p>'
        ),
    }


def service_navigation(lang: str) -> dict[str, Any]:
    service_name = settings.SERVICE_NAME
    service_url = "/"
    aria_label = "Language"
    items: list[dict[str, Any]] = [
        {"text": "English", "lang": "en", "current": True},
        {"text": "Cymraeg", "lang": "cy", "href": "/cy"},
    ]
    if lang == "cy":
        service_name = settings.SERVICE_NAME_CY
        service_url = "/cy"
        aria_label = "Iaith"
        items = [
            {"text": "English", "lang": "en", "href": "/"},
            {"text": "Cymraeg", "lang": "cy", "current": True},
        ]
    languages = Render(
        "language-navigation",
        params_from_mapping({"ariaLabel": aria_label, "items": items}),
    )
    return {
        "serviceName": service_name,
        "serviceUrl": service_url,
        "slots": {"end": Safe(languages)},
    }


def footer_options(lang: str) -> dict[str, Any]:
    items: list[dict[str, Any]] = [
        {"href": "/help", "text": "Help"},
        {"href": "/fees", "text": "Licence fees"},
        {"href": "/updates", "text": "Service updates"},
        {"href": "/guidance", "text": "Guidance"},
        {"href": "/cookies", "text": "Cookies"},
        {"href": "/accessibility", "text": "Accessibility"},
        {"href": "/about", "text": "About this example"},
    ]
    if settings.DEMOS_ENABLED:
        items.extend(
            [
                {"href": "/components/", "text": "Component catalogue"},
                {"href": "/examples", "text": "Example pages"},
            ]
        )
    footer: dict[str, Any] = {"meta": {"items": items}}
    if lang == "cy":
        footer["contentLicence"] = {
            "html": Safe(
                "Mae’r holl gynnwys ar gael dan "
                '<a class="govuk-footer__link" '
                'href="https://www.nationalarchives.gov.uk/doc/open-government-licence-cymraeg/'
                'version/3/" rel="license">Drwydded y Llywodraeth Agored v3.0</a>, '
                "ac eithrio lle nodir yn wahanol"
            )
        }
        footer["copyright"] = {"html": Safe("<span>Hawlfraint y Goron</span>")}
    return footer


def cookie_banner_options(request: HttpRequest) -> dict[str, Any] | None:
    banner_state = get_cookie_banner(request)
    if banner_state == CHOICE_ACCEPT:
        return _confirmation_banner("You have accepted analytics cookies.")
    if banner_state == CHOICE_REJECT:
        return _confirmation_banner("You have rejected analytics cookies.")
    if get_cookie_choice(request):
        return None
    return {
        "messages": [
            {
                "headingText": "Cookies on Apply for a fishing rod licence",
                "text": (
                    "We use analytics cookies to understand how you use this example service. "
                    "This example does not set analytics cookies."
                ),
                "actions": [
                    {
                        "text": "Accept analytics cookies",
                        "type": "submit",
                        "name": "cookies",
                        "value": "accept",
                    },
                    {
                        "text": "Reject analytics cookies",
                        "type": "submit",
                        "name": "cookies",
                        "value": "reject",
                    },
                    {"text": "View cookies", "href": "/cookies"},
                ],
            }
        ]
    }


def _confirmation_banner(text: str) -> dict[str, Any]:
    return {
        "messages": [
            {
                "text": text,
                "role": "alert",
                "actions": [
                    {
                        "text": "Hide cookie message",
                        "type": "submit",
                        "name": "cookies",
                        "value": "hide",
                    }
                ],
            }
        ]
    }


def safe_return_path(value: str) -> str:
    if (
        not value.startswith("/")
        or value.startswith("//")
        or "://" in value
        or "\\" in value
        or "\r" in value
        or "\n" in value
    ):
        return "/"
    return value


def layout_context(
    request: HttpRequest,
    *,
    heading: str,
    lang: str = "en",
    has_errors: bool = False,
    back_link: dict[str, Any] | None = None,
    breadcrumbs: dict[str, Any] | None = None,
    main_classes: str = "",
    show_feedback: bool = False,
    personal: bool = False,
    exit_this_page: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if back_link is not None and breadcrumbs is not None:
        raise ValueError("page cannot set both a back link and breadcrumbs")

    service_name = settings.SERVICE_NAME_CY if lang == "cy" else settings.SERVICE_NAME
    skip = "Neidio i'r prif gynnwys" if lang == "cy" else "Skip to main content"
    homepage = "/cy" if lang == "cy" else "/"
    return_path = safe_return_path(request.get_full_path())

    return {
        "heading": heading,
        "page_title": page_title(heading, service_name, has_errors=has_errors),
        "html_lang": lang,
        "skip_link_text": skip,
        "skip_link": {"href": "#main-content", "text": skip},
        "header": {"homepageUrl": homepage},
        "homepage_url": homepage,
        "main_classes": main_classes,
        "return_path": return_path,
        "service_navigation": service_navigation(lang),
        "phase_banner": phase_banner(lang),
        "demo_banner": demo_banner(lang),
        "footer": footer_options(lang),
        "cookie_banner": cookie_banner_options(request),
        "feedback": feedback_options(),
        "back_link": back_link,
        "breadcrumbs": breadcrumbs,
        "exit_this_page": exit_this_page,
        "show_feedback": show_feedback,
        "personal": personal,
        "frontend_version": getattr(settings, "GOVUK_FRONTEND_VERSION", "6.5.1"),
    }
