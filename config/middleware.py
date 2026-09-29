"""HTTP middleware: baseline headers and Brotli/Gzip compression."""

from __future__ import annotations

import gzip
from collections.abc import Callable

import brotli
from django.http import HttpRequest, HttpResponse

from config.baseline import build_response_headers


class BaselineHeadersMiddleware:
    """Apply baseline/policy.json headers using ``request.baseline_kind``."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        if getattr(response, "streaming", False):
            return response

        kind = str(
            getattr(request, "baseline_kind", None)
            or getattr(response, "baseline_kind", "document")
        )
        if kind == "skip":
            return response

        secure = request.is_secure() or request.META.get("HTTP_X_FORWARDED_PROTO") == "https"
        sets_cookie = bool(response.cookies)
        content_type = response.get("Content-Type")
        etag = response.get("ETag")
        filename = getattr(response, "download_filename", None)

        try:
            headers = build_response_headers(
                kind=kind,
                secure_transport=secure,
                content_type=content_type,
                etag=etag,
                sets_cookie=sets_cookie,
                filename=filename,
            )
        except ValueError:
            return response

        for name in (
            "Server",
            "X-Powered-By",
            "X-AspNet-Version",
            "X-AspNetMvc-Version",
        ):
            if name in response:
                del response[name]  # pragma: no cover

        for name, value in headers.items():
            if name == "Content-Type" and response.get("Content-Type"):
                continue
            response[name] = value
        return response


class CompressionMiddleware:
    """Compress text responses: Brotli when advertised, else Gzip."""

    _compressible_prefixes = (
        "text/",
        "application/javascript",
        "application/json",
        "application/xml",
        "image/svg+xml",
    )

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        if getattr(response, "streaming", False):
            return response  # pragma: no cover
        if response.get("Content-Encoding"):
            return response
        if response.status_code < 200 or response.status_code >= 300:
            return response

        content_type = (response.get("Content-Type") or "").split(";")[0].strip()
        if not any(
            content_type == prefix or content_type.startswith(prefix)
            for prefix in self._compressible_prefixes
        ):
            return response

        accept = request.META.get("HTTP_ACCEPT_ENCODING", "")
        body: bytes = response.content
        if len(body) < 200:
            return response

        if "br" in accept:
            response.content = brotli.compress(body)
            response["Content-Encoding"] = "br"
        elif "gzip" in accept:
            response.content = gzip.compress(body, compresslevel=6)
            response["Content-Encoding"] = "gzip"
        else:
            return response

        response["Content-Length"] = str(len(response.content))
        vary = response.get("Vary")
        if vary:
            if "Accept-Encoding" not in vary:  # pragma: no branch
                response["Vary"] = f"{vary}, Accept-Encoding"
        else:
            response["Vary"] = "Accept-Encoding"  # pragma: no cover
        return response
