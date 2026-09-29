"""Load and apply baseline/policy.json response headers."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, cast

from django.conf import settings

CacheKind = str

VALID_KINDS = frozenset(
    {
        "document",
        "sensitive-document",
        "fingerprinted-asset",
        "static-asset",
        "download",
        "sensitive-download",
    }
)


@lru_cache(maxsize=1)
def load_policy() -> dict[str, Any]:
    path: Path = settings.BASELINE_POLICY_PATH
    with path.open(encoding="utf-8") as handle:
        return cast(dict[str, Any], json.load(handle))


def js_enabled_snippet() -> str:
    return str(load_policy()["jsEnabledSnippet"])


def js_enabled_script_hash() -> str:
    return str(load_policy()["jsEnabledScriptHash"])


def build_response_headers(
    *,
    kind: CacheKind,
    secure_transport: bool,
    content_type: str | None = None,
    etag: str | None = None,
    sets_cookie: bool = False,
    filename: str | None = None,
) -> dict[str, str]:
    """Build OWASP/performance headers for one response kind.

    Mirrors ``baseline/index.mjs`` ``buildResponseHeaders`` for the kinds this
    service uses. Pass ``secure_transport=True`` behind HTTPS / Render.
    """
    if kind not in VALID_KINDS:
        raise ValueError(f"unknown cache kind: {kind!r}")

    policy = load_policy()
    headers: dict[str, str] = dict(policy["headers"]["all"])

    if kind in {"document", "sensitive-document"}:
        headers.update(policy["headers"]["document"])

    cache = policy["cacheControl"][kind]
    if sets_cookie and kind == "document":
        cache = "private, no-cache"
    headers["Cache-Control"] = cache

    if content_type:
        headers["Content-Type"] = content_type
    elif kind in policy["contentTypes"]:  # pragma: no branch
        headers["Content-Type"] = policy["contentTypes"][kind]

    # CSP
    if kind in {"document", "sensitive-document"}:
        csp = _build_csp(policy, secure_transport=secure_transport)
        headers["Content-Security-Policy"] = csp
        headers["Permissions-Policy"] = ",".join(
            f"{feature}=()" for feature in policy["permissionsPolicy"]
        )
        headers["X-Robots-Tag"] = "noindex, nofollow"

    if etag:
        headers["ETag"] = etag

    if secure_transport:
        hsts = policy["hsts"]
        headers["Strict-Transport-Security"] = (
            f"max-age={hsts['maxAge']}; includeSubDomains"
        )

    if kind in {"download", "sensitive-download"}:
        if not filename:
            raise ValueError("filename is required for download kinds")
        if "/" in filename or "\\" in filename or "\n" in filename or "\r" in filename:
            raise ValueError("filename must be a single path segment")
        headers["Content-Disposition"] = f'attachment; filename="{filename}"'

    return headers


def _build_csp(policy: dict[str, Any], *, secure_transport: bool) -> str:
    directives: dict[str, list[str]] = {
        key: list(values) for key, values in policy["csp"]["directives"].items()
    }
    script_src = directives.setdefault("script-src", ["'self'"])
    # CSP hash sources must be single-quoted (see baseline/headers.mjs).
    script_hash = js_enabled_script_hash()
    quoted_hash = script_hash if script_hash.startswith("'") else f"'{script_hash}'"
    if quoted_hash not in script_src:  # pragma: no branch
        script_src.append(quoted_hash)

    parts: list[str] = []
    for name, values in directives.items():
        if name == "upgrade-insecure-requests":
            if secure_transport:
                parts.append("upgrade-insecure-requests")
            continue
        if values:
            parts.append(f"{name} {' '.join(values)}")
        else:
            parts.append(name)  # pragma: no cover
    return "; ".join(parts)
