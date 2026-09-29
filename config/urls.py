"""Root URL configuration."""

from __future__ import annotations

from django.conf import settings
from django.urls import include, path

urlpatterns = [
    path("", include("service.urls")),
]

if settings.DEMOS_ENABLED:
    urlpatterns.append(path("components/", include("previews.urls")))
else:  # pragma: no cover — demos off: catalogue routes omitted
    pass

handler404 = "service.views.not_found"
