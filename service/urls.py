"""URL routes for the licence journey and supporting pages."""

from __future__ import annotations

from django.urls import path, re_path

from service import views

urlpatterns = [
    path("health", views.HealthView.as_view(), name="health"),
    path("robots.txt", views.RobotsView.as_view(), name="robots"),
    re_path(r"^assets/(?P<asset_path>.*)$", views.AssetView.as_view(), name="assets"),
    path("", views.StartView.as_view(), {"lang": "en"}, name="start"),
    path("cy", views.StartView.as_view(), {"lang": "cy"}, name="start_cy"),
    path("new-application", views.NewApplicationView.as_view(), name="new_application"),
    path("task-list", views.TaskListView.as_view(), name="task_list"),
    path("name", views.NameView.as_view(), name="name"),
    path("date-of-birth", views.DateOfBirthView.as_view(), name="date_of_birth"),
    path("email", views.EmailView.as_view(), name="email"),
    path(
        "contact-preference",
        views.ContactPreferenceView.as_view(),
        name="contact_preference",
    ),
    path(
        "where-you-will-fish",
        views.WhereYouWillFishView.as_view(),
        name="where_you_will_fish",
    ),
    path("licence-length", views.LicenceLengthView.as_view(), name="licence_length"),
    path("start-month", views.StartMonthView.as_view(), name="start_month"),
    path("address", views.AddressView.as_view(), name="address"),
    path("evidence", views.EvidenceView.as_view(), name="evidence"),
    path(
        "additional-details",
        views.AdditionalDetailsView.as_view(),
        name="additional_details",
    ),
    path("create-a-password", views.CreatePasswordView.as_view(), name="create_a_password"),
    path("check-answers", views.CheckAnswersView.as_view(), name="check_answers"),
    path("confirmation", views.ConfirmationView.as_view(), name="confirmation"),
    path("fees", views.FeesView.as_view(), name="fees"),
    path("help", views.HelpView.as_view(), name="help"),
    path("guidance", views.GuidanceView.as_view(), name="guidance"),
    path("updates", views.UpdatesView.as_view(), name="updates"),
    path("cookies", views.CookiesView.as_view(), name="cookies"),
    path("cookie-choices", views.CookieChoicesView.as_view(), name="cookie_choices"),
    path("accessibility", views.AccessibilityView.as_view(), name="accessibility"),
    path("about", views.AboutView.as_view(), name="about"),
    path("examples", views.ExamplesView.as_view(), name="examples"),
    path(
        "examples/exit-this-page",
        views.ExitThisPageView.as_view(),
        name="exit_this_page",
    ),
    path(
        "examples/service-unavailable",
        views.UnavailableView.as_view(),
        name="unavailable",
    ),
    path(
        "examples/problem-with-the-service",
        views.ProblemView.as_view(),
        name="problem",
    ),
]
