"""URL routes for component previews (demos only)."""

from __future__ import annotations

from django.urls import path

from previews import views

urlpatterns = [
    path("", views.CatalogueView.as_view(), name="components"),
    path("<slug:name>/", views.ComponentDetailView.as_view(), name="component_detail"),
    path(
        "<slug:name>/fixture/",
        views.FixtureRawView.as_view(),
        name="component_fixture",
    ),
]
