"""Ports for chrome components (header, footer, skip link, …).

Tracks GOV.UK Frontend Nunjucks macros / ``template.njk`` for fixture HTML parity.
"""

# ruff: noqa: E501

from __future__ import annotations

from typing import Any

from .attributes import (
    Attributes,
    attribute_if,
    classes_if,
    content,
    content_indent,
    flag_if,
)
from .components_button import render_button
from .nunjucks import (
    def_,
    def_truthy,
    escape,
    get,
    indent,
    items,
    length,
    loose_eq,
    out,
    str_value,
    trim,
    truthy,
)
from .params import Params, Safe, new_params

LOGO_CROWN = """    <g>
      <circle cx="20" cy="17.6" r="3.7"/>
      <circle cx="10.2" cy="23.5" r="3.7"/>
      <circle cx="3.7" cy="33.2" r="3.7"/>
      <circle cx="31.7" cy="30.6" r="3.7"/>
      <circle cx="43.3" cy="17.6" r="3.7"/>
      <circle cx="53.2" cy="23.5" r="3.7"/>
      <circle cx="59.7" cy="33.2" r="3.7"/>
      <circle cx="31.7" cy="30.6" r="3.7"/>
      <path d="M33.1,9.8c.2-.1.3-.3.5-.5l4.6,2.4v-6.8l-4.6,1.5c-.1-.2-.3-.3-.5-.5l1.9-5.9h-6.7l1.9,5.9c-.2.1-.3.3-.5.5l-4.6-1.5v6.8l4.6-2.4c.1.2.3.3.5.5l-2.6,8c-.9,2.8,1.2,5.7,4.1,5.7h0c3,0,5.1-2.9,4.1-5.7l-2.6-8ZM37,37.9s-3.4,3.8-4.1,6.1c2.2,0,4.2-.5,6.4-2.8l-.7,8.5c-2-2.8-4.4-4.1-5.7-3.8.1,3.1.5,6.7,5.8,7.2,3.7.3,6.7-1.5,7-3.8.4-2.6-2-4.3-3.7-1.6-1.4-4.5,2.4-6.1,4.9-3.2-1.9-4.5-1.8-7.7,2.4-10.9,3,4,2.6,7.3-1.2,11.1,2.4-1.3,6.2,0,4,4.6-1.2-2.8-3.7-2.2-4.2.2-.3,1.7.7,3.7,3,4.2,1.9.3,4.7-.9,7-5.9-1.3,0-2.4.7-3.9,1.7l2.4-8c.6,2.3,1.4,3.7,2.2,4.5.6-1.6.5-2.8,0-5.3l5,1.8c-2.6,3.6-5.2,8.7-7.3,17.5-7.4-1.1-15.7-1.7-24.5-1.7h0c-8.8,0-17.1.6-24.5,1.7-2.1-8.9-4.7-13.9-7.3-17.5l5-1.8c-.5,2.5-.6,3.7,0,5.3.8-.8,1.6-2.3,2.2-4.5l2.4,8c-1.5-1-2.6-1.7-3.9-1.7,2.3,5,5.2,6.2,7,5.9,2.3-.4,3.3-2.4,3-4.2-.5-2.4-3-3.1-4.2-.2-2.2-4.6,1.6-6,4-4.6-3.7-3.7-4.2-7.1-1.2-11.1,4.2,3.2,4.3,6.4,2.4,10.9,2.5-2.8,6.3-1.3,4.9,3.2-1.8-2.7-4.1-1-3.7,1.6.3,2.3,3.3,4.1,7,3.8,5.4-.5,5.7-4.2,5.8-7.2-1.3-.2-3.7,1-5.7,3.8l-.7-8.5c2.2,2.3,4.2,2.7,6.4,2.8-.7-2.3-4.1-6.1-4.1-6.1h10.6,0Z"/>
    </g>"""

LOGO_LOGOTYPE = """    <circle class="govuk-logo-dot" cx="226" cy="36" r="7.3"/>
    <path d="M93.94 41.25c.4 1.81 1.2 3.21 2.21 4.62 1 1.4 2.21 2.41 3.61 3.21s3.21 1.2 5.22 1.2 3.61-.4 4.82-1c1.4-.6 2.41-1.4 3.21-2.41.8-1 1.4-2.01 1.61-3.01s.4-2.01.4-3.01v.14h-10.86v-7.02h20.07v24.08h-8.03v-5.56c-.6.8-1.38 1.61-2.19 2.41-.8.8-1.81 1.2-2.81 1.81-1 .4-2.21.8-3.41 1.2s-2.41.4-3.81.4a18.56 18.56 0 0 1-14.65-6.63c-1.6-2.01-3.01-4.41-3.81-7.02s-1.4-5.62-1.4-8.83.4-6.02 1.4-8.83a20.45 20.45 0 0 1 19.46-13.65c3.21 0 4.01.2 5.82.8 1.81.4 3.61 1.2 5.02 2.01 1.61.8 2.81 2.01 4.01 3.21s2.21 2.61 2.81 4.21l-7.63 4.41c-.4-1-1-1.81-1.61-2.61-.6-.8-1.4-1.4-2.21-2.01-.8-.6-1.81-1-2.81-1.4-1-.4-2.21-.4-3.61-.4-2.01 0-3.81.4-5.22 1.2-1.4.8-2.61 1.81-3.61 3.21s-1.61 2.81-2.21 4.62c-.4 1.81-.6 3.71-.6 5.42s.8 5.22.8 5.22Zm57.8-27.9c3.21 0 6.22.6 8.63 1.81 2.41 1.2 4.82 2.81 6.62 4.82S170.2 24.39 171 27s1.4 5.62 1.4 8.83-.4 6.02-1.4 8.83-2.41 5.02-4.01 7.02-4.01 3.61-6.62 4.82-5.42 1.81-8.63 1.81-6.22-.6-8.63-1.81-4.82-2.81-6.42-4.82-3.21-4.41-4.01-7.02-1.4-5.62-1.4-8.83.4-6.02 1.4-8.83 2.41-5.02 4.01-7.02 4.01-3.61 6.42-4.82 5.42-1.81 8.63-1.81Zm0 36.73c1.81 0 3.61-.4 5.02-1s2.61-1.81 3.61-3.01 1.81-2.81 2.21-4.41c.4-1.81.8-3.61.8-5.62 0-2.21-.2-4.21-.8-6.02s-1.2-3.21-2.21-4.62c-1-1.2-2.21-2.21-3.61-3.01s-3.21-1-5.02-1-3.61.4-5.02 1c-1.4.8-2.61 1.81-3.61 3.01s-1.81 2.81-2.21 4.62c-.4 1.81-.8 3.61-.8 5.62 0 2.41.2 4.21.8 6.02.4 1.81 1.2 3.21 2.21 4.41s2.21 2.21 3.61 3.01c1.4.8 3.21 1 5.02 1Zm36.32 7.96-12.24-44.15h9.83l8.43 32.77h.4l8.23-32.77h9.83L200.3 58.04h-12.24Zm74.14-7.96c2.18 0 3.51-.6 3.51-.6 1.2-.6 2.01-1 2.81-1.81s1.4-1.81 1.81-2.81a13 13 0 0 0 .8-4.01V13.9h8.63v28.15c0 2.41-.4 4.62-1.4 6.62-.8 2.01-2.21 3.61-3.61 5.02s-3.41 2.41-5.62 3.21-4.62 1.2-7.02 1.2-5.02-.4-7.02-1.2c-2.21-.8-4.01-1.81-5.62-3.21s-2.81-3.01-3.61-5.02-1.4-4.21-1.4-6.62V13.9h8.63v26.95c0 1.61.2 3.01.8 4.01.4 1.2 1.2 2.21 2.01 2.81.8.8 1.81 1.4 2.81 1.81 0 0 1.34.6 3.51.6Zm34.22-36.18v18.92l15.65-18.92h10.82l-15.03 17.32 16.03 26.83h-10.21l-11.44-20.21-5.62 6.22v13.99h-8.83V13.9"/>"""

FOOTER_LICENCE_LOGO = """<svg
            aria-hidden="true"
            focusable="false"
            class="govuk-footer__licence-logo"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 483.2 195.7"
            height="17"
            width="41"
          >
            <path
              fill="currentColor"
              d="M421.5 142.8V.1l-50.7 32.3v161.1h112.4v-50.7zm-122.3-9.6A47.12 47.12 0 0 1 221 97.8c0-26 21.1-47.1 47.1-47.1 16.7 0 31.4 8.7 39.7 21.8l42.7-27.2A97.63 97.63 0 0 0 268.1 0c-36.5 0-68.3 20.1-85.1 49.7A98 98 0 0 0 97.8 0C43.9 0 0 43.9 0 97.8s43.9 97.8 97.8 97.8c36.5 0 68.3-20.1 85.1-49.7a97.76 97.76 0 0 0 149.6 25.4l19.4 22.2h3v-87.8h-80l24.3 27.5zM97.8 145c-26 0-47.1-21.1-47.1-47.1s21.1-47.1 47.1-47.1 47.2 21 47.2 47S123.8 145 97.8 145"
            />
          </svg>"""

FOOTER_COPYRIGHT_HREF = (
    "https://www.nationalarchives.gov.uk/information-management/"
    "re-using-public-sector-information/uk-government-licensing-framework/crown-copyright/"
)

PAGINATION_ARROW_PREVIOUS = """  <svg class="govuk-pagination__icon govuk-pagination__icon--prev" xmlns="http://www.w3.org/2000/svg" height="13" width="15" aria-hidden="true" focusable="false" viewBox="0 0 15 13">
    <path d="m6.5938-0.0078125-6.7266 6.7266 6.7441 6.4062 1.377-1.449-4.1856-3.9768h12.896v-2h-12.984l4.2931-4.293-1.414-1.414z"></path>
  </svg>"""

PAGINATION_ARROW_NEXT = """  <svg class="govuk-pagination__icon govuk-pagination__icon--next" xmlns="http://www.w3.org/2000/svg" height="13" width="15" aria-hidden="true" focusable="false" viewBox="0 0 15 13">
    <path d="m8.107-0.0078125-1.4136 1.414 4.2926 4.293h-12.986v2h12.896l-4.1855 3.9766 1.377 1.4492 6.7441-6.4062-6.7246-6.7266z"></path>
  </svg>"""



def render_logo(p: Params) -> str:
    use_logotype = truthy(def_(p.get("useLogotype"), True))
    width = "32"
    view_box = "64"
    if use_logotype:
        width = "162"
        view_box = "324"
    role = "presentation"
    aria_label = p.get("ariaLabelText")
    if truthy(aria_label):
        role = "img"

    parts: list[str] = []
    parts.append(
        '\n  <svg\n    focusable="false"\n    role="'
        + role
        + '"\n'
        + '    xmlns="http://www.w3.org/2000/svg"\n'
        + '    viewBox="0 0 '
        + view_box
        + ' 60"\n    height="30"\n    width="'
        + width
        + '"\n'
        + '    fill="currentcolor"'
        + attribute_if("class", p.get("classes"))
        + attribute_if("aria-label", aria_label)
        + Attributes(p.get("attributes"))
        + "\n  >"
    )
    if truthy(aria_label):
        parts.append("<title>" + out(aria_label) + "</title>")
    parts.append("    " + indent(trim(LOGO_CROWN), 2, False) + "\n")
    if use_logotype:
        parts.append("      " + indent(trim(LOGO_LOGOTYPE), 2, False) + "\n")
    parts.append("  </svg>\n")
    return "".join(parts)


def render_generic_header(p: Params) -> str:
    namespace = out(def_(p.get("_namespace"), "govuk-generic"))
    return (
        '<div class="'
        + namespace
        + "-header"
        + classes_if(p.get("classes"))
        + '"'
        + Attributes(p.get("attributes"))
        + ">\n"
        + '  <div class="'
        + namespace
        + "-header__container "
        + out(def_truthy(p.get("containerClasses"), "govuk-width-container"))
        + '">\n'
        + '    <div class="'
        + namespace
        + '-header__logo">\n'
        + '      <a href="'
        + out(def_truthy(p.get("url"), "/"))
        + '" class="'
        + namespace
        + '-header__homepage-link">\n'
        + "        "
        + content(p, "logoHtml", "logoText")
        + "\n"
        + "      </a>\n    </div>\n  </div>\n</div>"
    )


def render_header(p: Params) -> str:
    logo = render_logo(
        new_params(
            "classes",
            "govuk-header__logotype",
            "ariaLabelText",
            "GOV.UK",
        )
    )
    logo_content = "  " + trim(logo) + "\n"
    product_name = p.get("productName")
    if truthy(product_name):
        logo_content += (
            '<span class="govuk-header__product-name">' + out(product_name) + "</span>"
        )

    return render_generic_header(
        new_params(
            "_namespace",
            "govuk",
            "logoHtml",
            Safe(indent(logo_content, 8, False)),
            "url",
            def_truthy(p.get("homepageUrl"), "//gov.uk"),
            "containerClasses",
            p.get("containerClasses"),
            "classes",
            p.get("classes"),
            "attributes",
            p.get("attributes"),
        )
    )


def render_footer(p: Params) -> str:
    parts: list[str] = []
    parts.append(
        '<div class="govuk-footer'
        + classes_if(p.get("classes"))
        + '"'
        + Attributes(p.get("attributes"))
        + ">\n"
    )
    parts.append(
        '  <div class="govuk-width-container'
        + classes_if(p.get("containerClasses"))
        + '">'
    )
    parts.append(
        render_logo(new_params("classes", "govuk-footer__crown", "useLogotype", False))
    )
    parts.append("\n")

    navigation = items(p.get("navigation"))
    if len(navigation) > 0:
        parts.append('      <div class="govuk-footer__navigation">\n')
        for nav in navigation:
            parts.append(
                '          <div class="govuk-footer__section govuk-grid-column-'
                + out(def_truthy(get(nav, "width"), "full"))
                + '">\n'
            )
            parts.append(
                '            <h2 class="govuk-footer__heading govuk-heading-m">'
                + out(get(nav, "title"))
                + "</h2>\n"
            )
            links = items(get(nav, "items"))
            if len(links) > 0:  # pragma: no branch
                list_classes = ""
                columns = get(nav, "columns")
                if truthy(columns):
                    list_classes = (
                        " govuk-footer__list--columns-" + escape(str_value(columns))
                    )
                parts.append(
                    '              <ul class="govuk-footer__list'
                    + list_classes
                    + '">\n'
                )
                for link in links:
                    if not truthy(get(link, "href")) or not truthy(get(link, "text")):
                        continue  # pragma: no cover
                    parts.append(
                        '                    <li class="govuk-footer__list-item">\n'
                    )
                    parts.append(
                        '                      <a class="govuk-footer__link" href="'
                        + out(get(link, "href"))
                        + '"'
                        + Attributes(get(link, "attributes"))
                        + ">\n"
                    )
                    parts.append(
                        "                        " + out(get(link, "text")) + "\n"
                    )
                    parts.append("                      </a>\n                    </li>\n")
                parts.append("              </ul>\n")
            parts.append("          </div>\n")
        parts.append("      </div>\n")
        parts.append('      <hr class="govuk-footer__section-break">\n')

    parts.append('    <div class="govuk-footer__meta">\n')
    parts.append(
        '      <div class="govuk-footer__meta-item govuk-footer__meta-item--grow">\n'
    )

    meta = p.get("meta")
    if truthy(meta):
        parts.append(
            '        <h2 class="govuk-visually-hidden">'
            + out(def_truthy(get(meta, "visuallyHiddenTitle"), "Support links"))
            + "</h2>\n"
        )
        links = items(get(meta, "items"))
        if len(links) > 0:
            parts.append('        <ul class="govuk-footer__inline-list">\n')
            for link in links:
                parts.append(
                    '          <li class="govuk-footer__inline-list-item">\n'
                )
                parts.append(
                    '            <a class="govuk-footer__link" href="'
                    + out(get(link, "href"))
                    + '"'
                    + Attributes(get(link, "attributes"))
                    + ">\n"
                )
                parts.append("              " + out(get(link, "text")) + "\n")
                parts.append("            </a>\n          </li>\n")
            parts.append("        </ul>\n")
        if truthy(get(meta, "text")) or truthy(get(meta, "html")):
            parts.append('        <div class="govuk-footer__meta-custom">\n')
            parts.append(
                "          " + content_indent(meta, "html", "text", 10) + "\n"
            )
            parts.append("        </div>\n")

    # contentLicence: Undefined is not None; JSON null is None.
    licence = p.get("contentLicence")
    if licence is not None:
        parts.append("          " + FOOTER_LICENCE_LOGO + "\n")
        parts.append('          <span class="govuk-footer__licence-description">\n')
        if truthy(get(licence, "html")) or truthy(get(licence, "text")):
            parts.append(
                "            " + content_indent(licence, "html", "text", 12) + "\n"
            )
        else:
            parts.append(
                "            All content is available under the\n"
                '            <a\n'
                '              class="govuk-footer__link"\n'
                '              href="https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/"\n'
                '              rel="license"\n'
                "            >Open Government Licence v3.0</a>, except where otherwise stated\n"
            )
        parts.append("          </span>\n")

    parts.append("      </div>\n")
    parts.append('      <div class="govuk-footer__meta-item">\n')
    parts.append(
        "        <a\n"
        '          class="govuk-footer__link govuk-footer__copyright-logo"\n'
        '          href="'
        + FOOTER_COPYRIGHT_HREF
        + '"\n        >\n'
    )
    copyright_ = p.get("copyright")
    if truthy(get(copyright_, "html")) or truthy(get(copyright_, "text")):
        parts.append(
            "          " + content_indent(copyright_, "html", "text", 10) + "\n"
        )
    else:
        parts.append("          \u00a9 Crown copyright\n")
    parts.append("        </a>\n      </div>\n")
    parts.append("    </div>\n  </div>\n</div>")
    return "".join(parts)


def render_breadcrumbs(p: Params) -> str:
    class_names = "govuk-breadcrumbs"
    classes = p.get("classes")
    if truthy(classes):
        class_names += " " + str_value(classes)
    if truthy(p.get("collapseOnMobile")):
        class_names += " govuk-breadcrumbs--collapse-on-mobile"

    parts: list[str] = []
    parts.append(
        '<nav class="'
        + escape(class_names)
        + '"'
        + Attributes(p.get("attributes"))
        + ' aria-label="'
        + out(def_(p.get("labelText"), "Breadcrumb"))
        + '">\n'
    )
    parts.append('  <ol class="govuk-breadcrumbs__list">\n')
    for item in items(p.get("items")):
        href = get(item, "href")
        if truthy(href):
            parts.append('    <li class="govuk-breadcrumbs__list-item">\n')
            parts.append(
                '      <a class="govuk-breadcrumbs__link" href="'
                + out(href)
                + '"'
                + Attributes(get(item, "attributes"))
                + ">"
                + content(item, "html", "text")
                + "</a>\n"
            )
            parts.append("    </li>\n")
        else:
            parts.append(
                '    <li class="govuk-breadcrumbs__list-item" aria-current="page">'
                + content(item, "html", "text")
                + "</li>\n"
            )
    parts.append("  </ol>\n</nav>")
    return "".join(parts)


def render_language_navigation(p: Params) -> str:
    parts: list[str] = []
    parts.append(
        '<nav class="govuk-language-navigation'
        + classes_if(p.get("classes"))
        + '"'
        + Attributes(p.get("attributes"))
        + ' aria-label="'
        + out(def_(p.get("ariaLabel"), "Language"))
        + '">\n'
    )
    parts.append('  <ul class="govuk-language-navigation__list">\n')

    for item in items(p.get("items")):
        href = get(item, "href")
        parts.append('    <li class="govuk-language-navigation__list-item">\n')
        if truthy(get(item, "current")) or not truthy(href):
            parts.append(
                '      <span class="govuk-language-navigation__text'
                + classes_if(get(item, "classes"))
                + '"\n        aria-current="true"'
                + attribute_if("lang", get(item, "lang"))
                + attribute_if("dir", get(item, "dir"))
                + Attributes(get(item, "attributes"))
                + ">"
                + content(item, "html", "text")
                + "</span>\n"
            )
        else:
            href_lang = get(item, "hrefLang")
            if not truthy(href_lang):  # pragma: no branch
                href_lang = get(item, "lang")
            parts.append(
                '      <a class="govuk-language-navigation__link'
                + classes_if(get(item, "classes"))
                + '" href="'
                + out(href)
                + '" rel="alternate"'
                + attribute_if("lang", get(item, "lang"))
                + attribute_if("hreflang", href_lang)
                + attribute_if("dir", get(item, "dir"))
                + Attributes(get(item, "attributes"))
                + ">"
                + content(item, "html", "text")
            )
            description = get(item, "languageDescriptionText")
            if truthy(description):
                parts.append(
                    '<span class="govuk-visually-hidden"> '
                    + out(description)
                    + "</span>"
                )
            parts.append("      </a>\n")
        parts.append("    </li>\n")

    parts.append("  </ul>\n</nav>")
    return "".join(parts)



def render_service_navigation(p: Params) -> str:
    slots = p.get("slots")
    menu_button_text = def_truthy(p.get("menuButtonText"), "Menu")
    navigation_id = out(def_truthy(p.get("navigationId"), "navigation"))

    end_slot = get(slots, "end")
    end_slot_html = get(end_slot, "html")
    if isinstance(end_slot, str):
        end_slot_html = end_slot
    end_slot_is_object = isinstance(end_slot, Params)
    end_slot_inline = end_slot_is_object and loose_eq(end_slot.get("align"), "inline")

    common_attributes = (
        'class="govuk-service-navigation'
        + classes_if(p.get("classes"))
        + '"\n'
        + 'data-module="govuk-service-navigation"'
        + Attributes(p.get("attributes"))
        + "\n"
    )

    inner: list[str] = []
    inner.append(
        '  <div class="govuk-width-container'
        + flag_if(" govuk-service-navigation__inlining-container", end_slot_inline)
        + '">\n\n    '
    )
    start = get(slots, "start")
    if truthy(start):
        inner.append(str_value(start))
    inner.append('<div class="govuk-service-navigation__container">\n      \n')

    service_name = p.get("serviceName")
    if truthy(service_name):
        inner.append('        <span class="govuk-service-navigation__service-name">\n')
        service_url = p.get("serviceUrl")
        if truthy(service_url):
            inner.append(
                '            <a href="'
                + out(service_url)
                + '" class="govuk-service-navigation__link">\n'
            )
            inner.append(
                "              " + out(service_name) + "\n            </a>\n"
            )
        else:
            inner.append(
                '            <span class="govuk-service-navigation__text">'
                + out(service_name)
                + "</span>\n"
            )
        inner.append("        </span>\n")
    inner.append("\n      \n")

    navigation_items: list[Any] = []
    for item in items(p.get("navigation")):
        if truthy(item):
            navigation_items.append(item)
    collapse = truthy(def_(p.get("collapseNavigationOnMobile"), len(navigation_items) > 1))

    navigation_start = get(slots, "navigationStart")
    navigation_end = get(slots, "navigationEnd")
    if (
        len(navigation_items) > 0
        or truthy(navigation_start)
        or truthy(navigation_end)
    ):
        inner.append(
            '        <nav aria-label="'
            + out(def_truthy(p.get("navigationLabel"), menu_button_text))
            + '" class="govuk-service-navigation__wrapper'
            + classes_if(p.get("navigationClasses"))
            + '">\n'
        )
        if collapse:
            menu_button_label = p.get("menuButtonLabel")
            aria_label = ""
            if truthy(menu_button_label) and not loose_eq(
                menu_button_label, menu_button_text
            ):
                aria_label = ' aria-label="' + out(menu_button_label) + '"'
            inner.append(
                '          <button type="button" class="govuk-service-navigation__toggle '
                "govuk-js-service-navigation-toggle\" aria-controls=\""
                + navigation_id
                + '"'
                + aria_label
                + ' hidden aria-hidden="true">\n'
            )
            inner.append(
                "            " + out(menu_button_text) + "\n          </button>\n"
            )
        inner.append(
            '\n          <ul class="govuk-service-navigation__list" id="'
            + navigation_id
            + '" >\n\n            '
        )
        if truthy(navigation_start):
            inner.append(str_value(navigation_start))
        inner.append("\n")

        for item in navigation_items:
            active = truthy(get(item, "active")) or truthy(get(item, "current"))
            if active:
                link_inner = (
                    "\n                                    \n"
                    '                  <strong class="govuk-service-navigation__active-fallback">'
                    + content(item, "html", "text")
                    + "</strong>\n"
                )
            else:
                link_inner = (
                    "\n                                    \n"
                    + content(item, "html", "text")
                )

            aria_current = ""
            if active:
                value = "true"
                if truthy(get(item, "current")):
                    value = "page"
                aria_current = ' aria-current="' + value + '"'

            inner.append("              \n")
            inner.append(
                '              <li class="govuk-service-navigation__item'
                + flag_if(" govuk-service-navigation__item--active", active)
                + '">\n'
            )
            href = get(item, "href")
            if truthy(href):
                inner.append(
                    '                  <a class="govuk-service-navigation__link" href="'
                    + out(href)
                    + '"'
                    + aria_current
                    + Attributes(get(item, "attributes"))
                    + ">"
                    + link_inner
                    + "\n                  </a>\n"
                )
            elif truthy(get(item, "html")) or truthy(get(item, "text")):  # pragma: no branch
                inner.append(
                    '                  <span class="govuk-service-navigation__text"'
                    + aria_current
                    + ">"
                    + link_inner
                    + "\n                  </span>\n"
                )
            inner.append("              </li>\n\n")

        inner.append("            ")
        if truthy(navigation_end):
            inner.append(str_value(navigation_end))
        inner.append("</ul>\n        </nav>\n")

    inner.append("    </div>\n\n    ")
    if truthy(end_slot_html):
        inner.append(str_value(end_slot_html))
    inner.append("</div>\n")

    if (
        truthy(p.get("serviceName"))
        or truthy(get(slots, "start"))
        or truthy(end_slot_html)
    ):
        return (
            '  <section aria-label="'
            + out(def_(p.get("ariaLabel"), "Service information"))
            + '" '
            + common_attributes
            + ">\n    "
            + "".join(inner)
            + "\n  </section>\n"
        )
    return "  <div " + common_attributes + ">\n    " + "".join(inner) + "\n  </div>\n"


def render_pagination(p: Params) -> str:
    previous, next_ = p.get("previous"), p.get("next")
    block_level = not truthy(p.get("items")) and (
        truthy(next_) or truthy(previous)
    )

    parts: list[str] = []
    parts.append(
        '<nav class="govuk-pagination'
        + flag_if(" govuk-pagination--block", block_level)
        + classes_if(p.get("classes"))
        + '" aria-label="'
        + out(def_truthy(p.get("landmarkLabel"), "Pagination"))
        + '"'
        + Attributes(p.get("attributes"))
        + ">\n"
    )

    if truthy(previous) and truthy(get(previous, "href")):
        parts.append(
            _pagination_arrow_link(
                previous,
                "prev",
                block_level,
                _pagination_link_label(previous, "Previous"),
            )
        )

    entries = p.get("items")
    if truthy(entries):
        parts.append('  <ul class="govuk-pagination__list">\n')
        for item in items(entries):
            if item is None or length(item) == 0:
                continue
            parts.append(
                "      " + indent(_pagination_page_item(item), 2, False) + "\n"
            )
        parts.append("  </ul>\n")

    if truthy(next_) and truthy(get(next_, "href")):
        parts.append(
            _pagination_arrow_link(
                next_, "next", block_level, _pagination_link_label(next_, "Next")
            )
        )

    parts.append("</nav>")
    return "".join(parts)


def _pagination_link_label(link: Any, fallback: str) -> str:
    html, text = get(link, "html"), get(link, "text")
    if truthy(html):
        return trim(indent(trim(str_value(html)), 8, False))  # pragma: no cover
    if truthy(text):
        return out(text)
    return fallback + '<span class="govuk-visually-hidden"> page</span>'


def _pagination_arrow_link(
    link: Any, kind: str, block_level: bool, label: str
) -> str:
    arrow = PAGINATION_ARROW_NEXT
    if kind == "prev":
        arrow = PAGINATION_ARROW_PREVIOUS

    parts: list[str] = []
    parts.append('  <div class="govuk-pagination__' + kind + '">\n')
    parts.append(
        '    <a class="govuk-link govuk-pagination__link" href="'
        + out(get(link, "href"))
        + '" rel="'
        + kind
        + '"'
        + Attributes(get(link, "attributes"))
        + ">\n"
    )
    if block_level or kind == "prev":
        parts.append(indent(arrow, 4, True) + "\n")
    label_text = get(link, "labelText")
    parts.append(
        '      <span class="govuk-pagination__link-title'
        + flag_if(
            " govuk-pagination__link-title--decorated",
            block_level and not truthy(label_text),
        )
        + '">\n        '
        + label
        + "\n      </span>\n"
    )
    if truthy(label_text) and block_level:
        parts.append('      <span class="govuk-visually-hidden">:</span>\n')
        parts.append(
            '      <span class="govuk-pagination__link-label">'
            + out(label_text)
            + "</span>\n"
        )
    if not block_level and kind == "next":
        parts.append(indent(arrow, 4, True) + "\n")
    parts.append("    </a>\n  </div>\n")
    return "".join(parts)


def _pagination_page_item(item: Any) -> str:
    parts: list[str] = []
    parts.append(
        '<li class="govuk-pagination__item'
        + flag_if(" govuk-pagination__item--current", get(item, "current"))
        + flag_if(" govuk-pagination__item--ellipsis", get(item, "ellipsis"))
        + '">\n'
    )
    if truthy(get(item, "ellipsis")):
        parts.append("    &ctdot;\n")
    else:
        parts.append(
            '    <a class="govuk-link govuk-pagination__link" href="'
            + out(get(item, "href"))
            + '" aria-label="'
            + out(
                def_(
                    get(item, "visuallyHiddenText"),
                    "Page " + str_value(get(item, "number")),
                )
            )
            + '"'
            + flag_if(' aria-current="page"', get(item, "current"))
            + Attributes(get(item, "attributes"))
            + ">\n"
        )
        parts.append("      " + out(get(item, "number")) + "\n    </a>\n")
    parts.append("  </li>")
    return "".join(parts)


def render_cookie_banner(p: Params) -> str:
    parts: list[str] = []
    parts.append(
        '<div class="govuk-cookie-banner'
        + classes_if(p.get("classes"))
        + '" data-nosnippet role="region" aria-label="'
        + out(def_truthy(p.get("ariaLabel"), "Cookie banner"))
        + '"'
        + flag_if(" hidden", p.get("hidden"))
        + Attributes(p.get("attributes"))
        + ">\n"
    )

    for message in items(p.get("messages")):
        parts.append(
            '  <div class="govuk-cookie-banner__message'
            + classes_if(get(message, "classes"))
            + ' govuk-width-container"'
            + attribute_if("role", get(message, "role"))
            + Attributes(get(message, "attributes"))
            + flag_if(" hidden", get(message, "hidden"))
            + ">\n\n"
        )
        parts.append('    <div class="govuk-grid-row">\n')
        parts.append('      <div class="govuk-grid-column-two-thirds">\n')
        if truthy(get(message, "headingHtml")) or truthy(get(message, "headingText")):
            parts.append(
                '        <h2 class="govuk-cookie-banner__heading govuk-heading-m">\n'
            )
            parts.append(
                "          "
                + content_indent(message, "headingHtml", "headingText", 10)
                + "\n"
            )
            parts.append("        </h2>\n")
        parts.append('        <div class="govuk-cookie-banner__content">\n')
        html, text = get(message, "html"), get(message, "text")
        if truthy(html):
            parts.append(
                "          " + indent(trim(str_value(html)), 10, False) + "\n"
            )
        elif truthy(text):
            parts.append(
                '          <p class="govuk-body">' + out(text) + "</p>\n"
            )
        parts.append("        </div>\n      </div>\n    </div>\n\n")

        actions = items(get(message, "actions"))
        # Only render the button group when ``actions`` was supplied as an array
        # (including empty). Missing actions must not emit an empty group.
        raw_actions = get(message, "actions")
        if isinstance(raw_actions, list):
            parts.append('    <div class="govuk-button-group">\n')
            for action in actions:
                parts.append(
                    "      "
                    + indent(trim(_cookie_banner_action(action)), 6, False)
                    + "\n"
                )
            parts.append("    </div>\n")

        parts.append("\n  </div>\n")

    parts.append("</div>")
    return "".join(parts)


def _cookie_banner_action(action: Any) -> str:
    href = get(action, "href")
    if not truthy(href) or str_value(get(action, "type")) == "button":
        return render_button(
            new_params(
                "text",
                get(action, "text"),
                "type",
                def_truthy(get(action, "type"), "button"),
                "name",
                get(action, "name"),
                "value",
                get(action, "value"),
                "classes",
                get(action, "classes"),
                "href",
                href,
                "attributes",
                get(action, "attributes"),
            )
        )
    return (
        '<a class="govuk-link'
        + classes_if(get(action, "classes"))
        + '" href="'
        + out(href)
        + '"'
        + Attributes(get(action, "attributes"))
        + ">"
        + out(get(action, "text"))
        + "</a>"
    )
