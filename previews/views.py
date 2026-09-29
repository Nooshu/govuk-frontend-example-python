"""Component catalogue and fixture preview views."""

from __future__ import annotations

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.views import View
from govuk_components.rendering import Render, fixture_components, load_fixtures
from govuk_components.rendering.fixtures import Fixture
from service.chrome import crumbs, layout_context

from previews.catalogue import describe, parity_banner


def _set_baseline(request: HttpRequest) -> None:
    request.baseline_kind = "document"  # type: ignore[attr-defined]


def _components_dir() -> str:
    return str(settings.GOVUK_COMPONENTS_DIR)


def _select_fixture(fixtures: list[Fixture], requested: str) -> Fixture | None:
    if requested:
        for fixture in fixtures:
            if fixture.name == requested:
                return fixture  # pragma: no cover
        return None
    for fixture in fixtures:
        if not fixture.hidden:  # pragma: no branch
            return fixture
    if fixtures:  # pragma: no cover
        return fixtures[0]  # pragma: no cover
    return None  # pragma: no cover


class CatalogueView(View):
    template_name = "previews/components.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        _set_baseline(request)
        names = fixture_components(_components_dir())
        components = [describe(name) for name in names]
        context = layout_context(
            request,
            heading="Component catalogue",
            breadcrumbs=crumbs("Component catalogue"),
        )
        context["components"] = components
        return render(request, self.template_name, context)


class ComponentDetailView(View):
    template_name = "previews/component.html"

    def get(self, request: HttpRequest, name: str) -> HttpResponse:
        _set_baseline(request)
        names = fixture_components(_components_dir())
        if name not in names:
            return render(
                request,
                "service/not_found.html",
                layout_context(request, heading="Page not found"),
                status=404,
            )
        fixture_set = load_fixtures(_components_dir(), name)
        requested = request.GET.get("fixture", "")
        fixture = _select_fixture(fixture_set.fixtures, requested)
        if fixture is None:
            return render(
                request,
                "service/not_found.html",
                layout_context(request, heading="Page not found"),
                status=404,
            )
        rendered = Render(name, fixture.options)
        info = describe(name)
        matches = rendered == fixture.html
        context = layout_context(
            request,
            heading=info.title,
            back_link={"text": "Back", "href": "/components/"},
        )
        context.update(
            {
                "component_name": name,
                "component_title": info.title,
                "design_system_url": info.design_system_url,
                "description": fixture.description,
                "description_inset": {"text": fixture.description},
                "fixture_name": fixture.name,
                "rendered": mark_safe(rendered),  # noqa: S308 — trusted renderer output
                "parity": parity_banner(matches),
                "current_tag": {"text": "Current"},
                "fixtures": [
                    {"name": item.name, "current": item.name == fixture.name}
                    for item in fixture_set.fixtures
                ],
            }
        )
        return render(request, self.template_name, context)


class FixtureRawView(View):
    def get(self, request: HttpRequest, name: str) -> HttpResponse:
        _set_baseline(request)
        names = fixture_components(_components_dir())
        if name not in names:
            return HttpResponse("Not found", status=404, content_type="text/plain")
        fixture_set = load_fixtures(_components_dir(), name)
        requested = request.GET.get("fixture", "")
        fixture = _select_fixture(fixture_set.fixtures, requested)
        if fixture is None:
            return HttpResponse(
                "Not found",
                status=404,
                content_type="text/plain",
            )  # pragma: no cover
        return HttpResponse(fixture.html, content_type="text/html; charset=utf-8")
