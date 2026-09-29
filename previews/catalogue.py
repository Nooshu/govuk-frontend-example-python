"""Catalogue copy for the local component demo pages."""

from __future__ import annotations

from dataclasses import dataclass

DESIGN_SYSTEM = "https://design-system.service.gov.uk/components"

_DETAILS: dict[str, dict[str, str]] = {
    "accordion": {
        "title": "Accordion",
        "description": "Lets users show and hide sections of related content.",
        "design_system_url": f"{DESIGN_SYSTEM}/accordion/",
    },
    "back-link": {
        "title": "Back link",
        "description": "Link to the previous page in a journey.",
        "design_system_url": f"{DESIGN_SYSTEM}/back-link/",
    },
    "breadcrumbs": {
        "title": "Breadcrumbs",
        "description": "Helps users move between levels of a section.",
        "design_system_url": f"{DESIGN_SYSTEM}/breadcrumbs/",
    },
    "button": {
        "title": "Button",
        "description": "Starts or continues an action.",
        "design_system_url": f"{DESIGN_SYSTEM}/button/",
    },
    "character-count": {
        "title": "Character count",
        "description": "Shows how many characters are left in a textarea.",
        "design_system_url": f"{DESIGN_SYSTEM}/character-count/",
    },
    "checkboxes": {
        "title": "Checkboxes",
        "description": "Lets users select one or more options.",
        "design_system_url": f"{DESIGN_SYSTEM}/checkboxes/",
    },
    "cookie-banner": {
        "title": "Cookie banner",
        "description": "Asks users to accept or reject analytics cookies.",
        "design_system_url": f"{DESIGN_SYSTEM}/cookie-banner/",
    },
    "date-input": {
        "title": "Date input",
        "description": "Asks users for a date they already know.",
        "design_system_url": f"{DESIGN_SYSTEM}/date-input/",
    },
    "details": {
        "title": "Details",
        "description": "Hides content that only some users need.",
        "design_system_url": f"{DESIGN_SYSTEM}/details/",
    },
    "error-message": {
        "title": "Error message",
        "description": "Tells users how to fix a field that failed validation.",
        "design_system_url": f"{DESIGN_SYSTEM}/error-message/",
    },
    "error-summary": {
        "title": "Error summary",
        "description": "Summarises form errors at the top of the page.",
        "design_system_url": f"{DESIGN_SYSTEM}/error-summary/",
    },
    "exit-this-page": {
        "title": "Exit this page",
        "description": (
            "Lets users leave a page quickly. For services where someone may be in danger."
        ),
        "design_system_url": f"{DESIGN_SYSTEM}/exit-this-page/",
    },
    "feedback": {
        "title": "Feedback",
        "description": "Asks users what they think of a page. Trial component in Frontend 6.5.",
        "design_system_url": f"{DESIGN_SYSTEM}/feedback/",
    },
    "fieldset": {
        "title": "Fieldset",
        "description": "Groups related form fields, such as an address.",
        "design_system_url": f"{DESIGN_SYSTEM}/fieldset/",
    },
    "file-upload": {
        "title": "File upload",
        "description": "Lets users select a file to upload.",
        "design_system_url": f"{DESIGN_SYSTEM}/file-upload/",
    },
    "footer": {
        "title": "Footer",
        "description": "Page footer with Open Government Licence and Crown copyright.",
        "design_system_url": f"{DESIGN_SYSTEM}/footer/",
    },
    "generic-header": {
        "title": "Generic header",
        "description": (
            "Header for services that are not branded as GOV.UK. Shown in the catalogue only."
        ),
        "design_system_url": "https://design-system.service.gov.uk/styles/page-template/",
    },
    "header": {
        "title": "Header",
        "description": "The GOV.UK masthead.",
        "design_system_url": f"{DESIGN_SYSTEM}/header/",
    },
    "hint": {
        "title": "Hint",
        "description": (
            "Extra help for a form field. Form controls include it; "
            "the catalogue shows it on its own."
        ),
        "design_system_url": (
            "https://design-system.service.gov.uk/get-started/labels-legends-headings/"
        ),
    },
    "input": {
        "title": "Text input",
        "description": "Lets users enter a single line of text.",
        "design_system_url": f"{DESIGN_SYSTEM}/text-input/",
    },
    "inset-text": {
        "title": "Inset text",
        "description": "Draws attention to important content on the page.",
        "design_system_url": f"{DESIGN_SYSTEM}/inset-text/",
    },
    "label": {
        "title": "Label",
        "description": (
            "Labels a form field. Form controls include it; the catalogue shows it on its own."
        ),
        "design_system_url": (
            "https://design-system.service.gov.uk/get-started/labels-legends-headings/"
        ),
    },
    "language-navigation": {
        "title": "Language navigation",
        "description": (
            "Lets users switch between languages. Trial component in Frontend 6.5."
        ),
        "design_system_url": f"{DESIGN_SYSTEM}/language-navigation/",
    },
    "notification-banner": {
        "title": "Notification banner",
        "description": "Tells users about something that affects the whole service.",
        "design_system_url": f"{DESIGN_SYSTEM}/notification-banner/",
    },
    "pagination": {
        "title": "Pagination",
        "description": "Splits a long list across pages.",
        "design_system_url": f"{DESIGN_SYSTEM}/pagination/",
    },
    "panel": {
        "title": "Panel",
        "description": "Confirms a transaction is complete.",
        "design_system_url": f"{DESIGN_SYSTEM}/panel/",
    },
    "password-input": {
        "title": "Password input",
        "description": "Lets users enter a password, with a control to show or hide it.",
        "design_system_url": f"{DESIGN_SYSTEM}/password-input/",
    },
    "phase-banner": {
        "title": "Phase banner",
        "description": "Shows users that the service is still being tried out.",
        "design_system_url": f"{DESIGN_SYSTEM}/phase-banner/",
    },
    "radios": {
        "title": "Radios",
        "description": "Lets users select one option from a list.",
        "design_system_url": f"{DESIGN_SYSTEM}/radios/",
    },
    "select": {
        "title": "Select",
        "description": "Lets users choose one option from a long list.",
        "design_system_url": f"{DESIGN_SYSTEM}/select/",
    },
    "service-navigation": {
        "title": "Service navigation",
        "description": "Shows the service name under the GOV.UK masthead.",
        "design_system_url": f"{DESIGN_SYSTEM}/service-navigation/",
    },
    "skip-link": {
        "title": "Skip link",
        "description": "Lets keyboard users skip to the main content.",
        "design_system_url": f"{DESIGN_SYSTEM}/skip-link/",
    },
    "summary-list": {
        "title": "Summary list",
        "description": "Summarises answers so users can check them.",
        "design_system_url": f"{DESIGN_SYSTEM}/summary-list/",
    },
    "table": {
        "title": "Table",
        "description": "Shows information in rows and columns.",
        "design_system_url": f"{DESIGN_SYSTEM}/table/",
    },
    "tabs": {
        "title": "Tabs",
        "description": (
            "Lets users switch between related views. "
            "Content stays in the page without JavaScript."
        ),
        "design_system_url": f"{DESIGN_SYSTEM}/tabs/",
    },
    "tag": {
        "title": "Tag",
        "description": "Shows a short status, such as on a task list.",
        "design_system_url": f"{DESIGN_SYSTEM}/tag/",
    },
    "task-list": {
        "title": "Task list",
        "description": "Shows the tasks in an application and whether they are done.",
        "design_system_url": f"{DESIGN_SYSTEM}/task-list/",
    },
    "textarea": {
        "title": "Textarea",
        "description": (
            "Lets users enter more than one line of text. This service uses character "
            "count, which includes a textarea."
        ),
        "design_system_url": f"{DESIGN_SYSTEM}/textarea/",
    },
    "warning-text": {
        "title": "Warning text",
        "description": "Tells users about something important before they continue.",
        "design_system_url": f"{DESIGN_SYSTEM}/warning-text/",
    },
}


@dataclass(frozen=True, slots=True)
class Info:
    name: str
    title: str
    description: str
    design_system_url: str


def title_from_kebab(component: str) -> str:
    parts = component.split("-")
    words: list[str] = []
    for part in parts:
        if not part:
            words.append("")
            continue
        words.append(part[0].upper() + part[1:])
    return " ".join(words)


def describe(name: str) -> Info:
    known = _DETAILS.get(name)
    if known is not None:
        return Info(
            name=name,
            title=known["title"],
            description=known["description"],
            design_system_url=known["design_system_url"],
        )
    return Info(
        name=name,
        title=title_from_kebab(name),
        description="GOV.UK Frontend component.",
        design_system_url=f"{DESIGN_SYSTEM}/{name}/",
    )


def parity_banner(matches: bool) -> dict[str, str]:
    if matches:
        return {
            "type": "success",
            "titleText": "HTML matches the fixture",
            "text": "The macro output is the same as the official fixture HTML.",
        }
    return {
        "titleText": "HTML does not match the fixture",
        "text": "The macro output is different from the official fixture HTML.",
    }


def described_names() -> list[str]:
    return list(_DETAILS.keys())
