"""Renderer registry and Render entrypoint for all components.

Tracks GOV.UK Frontend Nunjucks macros / ``template.njk`` for fixture HTML parity.
"""

from __future__ import annotations

from collections.abc import Callable

from .components_button import render_button, render_exit_this_page
from .components_chrome import (
    render_breadcrumbs,
    render_cookie_banner,
    render_footer,
    render_generic_header,
    render_header,
    render_language_navigation,
    render_pagination,
    render_service_navigation,
)
from .components_forms import (
    render_character_count,
    render_checkboxes,
    render_date_input,
    render_file_upload,
    render_input,
    render_password_input,
    render_radios,
    render_select,
    render_textarea,
)
from .components_lists import (
    render_accordion,
    render_error_summary,
    render_notification_banner,
    render_summary_list,
    render_table,
    render_tabs,
    render_task_list,
)
from .components_text import (
    render_back_link,
    render_details,
    render_error_message,
    render_feedback,
    render_fieldset,
    render_hint,
    render_inset_text,
    render_label,
    render_panel,
    render_phase_banner,
    render_skip_link,
    render_tag,
    render_warning_text,
)
from .nunjucks import concat_if, heading  # re-export for callers
from .params import Params

RENDERERS: dict[str, Callable[[Params], str]] = {
    "accordion": render_accordion,
    "back-link": render_back_link,
    "breadcrumbs": render_breadcrumbs,
    "button": render_button,
    "character-count": render_character_count,
    "checkboxes": render_checkboxes,
    "cookie-banner": render_cookie_banner,
    "date-input": render_date_input,
    "details": render_details,
    "error-message": render_error_message,
    "error-summary": render_error_summary,
    "exit-this-page": render_exit_this_page,
    "feedback": render_feedback,
    "fieldset": render_fieldset,
    "file-upload": render_file_upload,
    "footer": render_footer,
    "generic-header": render_generic_header,
    "header": render_header,
    "hint": render_hint,
    "input": render_input,
    "inset-text": render_inset_text,
    "label": render_label,
    "language-navigation": render_language_navigation,
    "notification-banner": render_notification_banner,
    "pagination": render_pagination,
    "panel": render_panel,
    "password-input": render_password_input,
    "phase-banner": render_phase_banner,
    "radios": render_radios,
    "select": render_select,
    "service-navigation": render_service_navigation,
    "skip-link": render_skip_link,
    "summary-list": render_summary_list,
    "table": render_table,
    "tabs": render_tabs,
    "tag": render_tag,
    "task-list": render_task_list,
    "textarea": render_textarea,
    "warning-text": render_warning_text,
}


def Render(component: str, params: Params | None) -> str:
    """Return trimmed HTML for one GOV.UK Frontend component."""
    render = RENDERERS.get(component)
    if render is None:
        raise ValueError(f'govuk: {component!r} is not a GOV.UK Frontend component')
    if params is None:
        params = Params()
    return render(params).strip()


def MustRender(component: str, params: Params | None) -> str:
    """Render for call sites where the component name is a constant; raises on unknown."""
    return Render(component, params)


def Components() -> list[str]:
    """Return the names this package can render, sorted."""
    return sorted(RENDERERS)


# Snake_case aliases matching Python style.
render = Render
must_render = MustRender
components = Components

__all__ = [
    "RENDERERS",
    "Render",
    "MustRender",
    "Components",
    "render",
    "must_render",
    "components",
    "heading",
    "concat_if",
]
