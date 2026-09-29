"""Fingerprinted stylesheet / Frontend JS / init module and static asset resolution."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from django.conf import settings

_HASHED_FONT = re.compile(r"-[a-f0-9]{8,}-")
_CONTENT_TYPES: dict[str, str] = {
    ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".mjs": "text/javascript; charset=utf-8",
    ".map": "application/json; charset=utf-8",
    ".woff2": "font/woff2",
    ".woff": "font/woff",
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".ico": "image/x-icon",
    ".json": "application/json; charset=utf-8",
    ".gif": "image/gif",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
}

_ROOT_FILES = frozenset(
    {
        "govuk-frontend.min.js",
        "govuk-frontend.min.js.map",
        "manifest.json",
    }
)


def fingerprint(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()[:10]


@dataclass(frozen=True, slots=True)
class ResolvedAsset:
    path: Path | None
    body: bytes | None
    content_type: str
    kind: str  # fingerprinted-asset | static-asset


@dataclass(frozen=True, slots=True)
class PageAssets:
    stylesheet_href: str
    app_module_href: str
    script_href: str
    css_body: bytes
    script_body: bytes
    app_body: bytes


@lru_cache(maxsize=1)
def load_page_assets() -> PageAssets:
    """Read compiled CSS + Frontend JS once and compute fingerprinted URLs."""
    stylesheet = Path(settings.DIST_DIR) / "stylesheets" / "application.css"
    css = stylesheet.read_bytes()
    govuk_root = Path(settings.GOVUK_FRONTEND_ROOT) / "dist" / "govuk"
    script_path = govuk_root / "govuk-frontend.min.js"
    script = script_path.read_bytes()
    css_href = f"/assets/application.{fingerprint(css)}.css"
    script_href = f"/assets/govuk-frontend.{fingerprint(script)}.min.js"
    app = f"import {{ initAll }} from '{script_href}';\n\ninitAll();\n".encode()
    return PageAssets(
        stylesheet_href=css_href,
        app_module_href=f"/assets/app.{fingerprint(app)}.mjs",
        script_href=script_href,
        css_body=css,
        script_body=script,
        app_body=app,
    )


def resolve_asset(url_path: str) -> ResolvedAsset | None:
    """Map an ``/assets/…`` path to a file that is safe to send."""
    if not url_path.startswith("/assets/"):
        return None

    page = load_page_assets()
    if url_path == page.stylesheet_href:
        return ResolvedAsset(
            path=Path(settings.DIST_DIR) / "stylesheets" / "application.css",
            body=page.css_body,
            content_type="text/css; charset=utf-8",
            kind="fingerprinted-asset",
        )
    if url_path == page.script_href:
        govuk_root = Path(settings.GOVUK_FRONTEND_ROOT) / "dist" / "govuk"
        return ResolvedAsset(
            path=govuk_root / "govuk-frontend.min.js",
            body=page.script_body,
            content_type="text/javascript; charset=utf-8",
            kind="fingerprinted-asset",
        )
    if url_path == page.app_module_href:
        return ResolvedAsset(
            path=None,
            body=page.app_body,
            content_type="text/javascript; charset=utf-8",
            kind="fingerprinted-asset",
        )

    requested = url_path.removeprefix("/assets/")
    if not requested or "\x00" in requested or ".." in Path(requested).parts:
        return None

    govuk_root = Path(settings.GOVUK_FRONTEND_ROOT) / "dist" / "govuk"
    frontend_assets = govuk_root / "assets"
    root = (
        govuk_root
        if Path(requested).name in _ROOT_FILES and "/" not in requested
        else frontend_assets
    )
    if requested in _ROOT_FILES:
        root = govuk_root
        target = root / requested
    else:
        target = (frontend_assets / requested).resolve()
        try:
            target.relative_to(frontend_assets.resolve())
        except ValueError:  # pragma: no cover
            return None  # pragma: no cover

    if not target.is_file():
        return None
    content_type = _CONTENT_TYPES.get(target.suffix.lower())
    if content_type is None:
        return None  # pragma: no cover
    kind = (
        "fingerprinted-asset"
        if requested.startswith("fonts/") and _HASHED_FONT.search(requested)
        else "static-asset"
    )
    return ResolvedAsset(path=target, body=None, content_type=content_type, kind=kind)


def clear_asset_cache() -> None:
    """Reset cached fingerprints (tests / after rebuild)."""
    load_page_assets.cache_clear()
