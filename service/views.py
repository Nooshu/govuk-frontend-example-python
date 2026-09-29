"""HTTP views for the rod fishing licence example service."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, ClassVar, cast

from django import forms
from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import FormView, TemplateView

from service import govuk_options
from service.answers import summary_rows, task_sections
from service.application import (
    STEP_ADDITIONAL_DETAILS,
    STEP_ADDRESS,
    STEP_CONTACT_PREFERENCE,
    STEP_CREATE_A_PASSWORD,
    STEP_DATE_OF_BIRTH,
    STEP_EMAIL,
    STEP_EVIDENCE,
    STEP_LICENCE_LENGTH,
    STEP_NAME,
    STEP_START_MONTH,
    STEP_WHERE_YOU_WILL_FISH,
    Application,
    Step,
    first_incomplete_step,
    next_step,
    previous_step,
    reference_for,
    step_by_id,
)
from service.assets import resolve_asset
from service.chrome import crumbs, layout_context, safe_return_path
from service.forms import (
    AdditionalDetailsForm,
    AddressForm,
    ContactPreferenceForm,
    CookieSettingsForm,
    DateOfBirthForm,
    EmailForm,
    EvidenceForm,
    LicenceLengthForm,
    NameForm,
    PasswordForm,
    StartMonthForm,
    WhereYouWillFishForm,
)
from service.save import (
    AddressValues,
    save_address,
    save_contact,
    save_date,
    save_details,
    save_email,
    save_evidence,
    save_licence,
    save_month,
    save_name,
    save_password,
    save_regions,
)
from service.session import (
    CHOICE_ACCEPT,
    CHOICE_REJECT,
    clear_application,
    clear_errors,
    get_application,
    get_cookie_choice,
    pop_errors_for,
    pop_notice_for,
    save_application,
    set_cookie_banner,
    set_cookie_choice,
    set_errors,
    set_notice,
)
from service.validate import FieldError, safe_filename

if TYPE_CHECKING:
    _JourneyFormView = FormView[forms.Form]
    _CookieFormView = FormView[CookieSettingsForm]
else:
    _JourneyFormView = FormView
    _CookieFormView = FormView


def _now() -> datetime:
    return datetime.now(UTC)


def _set_baseline(request: HttpRequest, kind: str) -> None:
    request.baseline_kind = kind  # type: ignore[attr-defined]


def _layout(
    request: HttpRequest,
    *,
    heading: str,
    lang: str = "en",
    has_errors: bool = False,
    back_link: dict[str, Any] | None = None,
    breadcrumbs: dict[str, Any] | None = None,
    main_classes: str = "",
    show_feedback: bool = False,
    personal: bool = False,
    exit_this_page: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if personal:
        _set_baseline(request, "sensitive-document")
    else:
        _set_baseline(request, "document")
    return layout_context(
        request,
        heading=heading,
        lang=lang,
        has_errors=has_errors,
        back_link=back_link,
        breadcrumbs=breadcrumbs,
        main_classes=main_classes,
        show_feedback=show_feedback,
        personal=personal,
        exit_this_page=exit_this_page,
    )


def _errors_from_dicts(items: list[dict[str, str]]) -> list[FieldError]:
    return [
        FieldError(
            field=item.get("field", ""),
            href=item.get("href", ""),
            text=item.get("text", ""),
        )
        for item in items
    ]


class HealthView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        _set_baseline(request, "document")
        return HttpResponse("ok", content_type="text/plain; charset=utf-8")


class RobotsView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        _set_baseline(request, "document")
        return HttpResponse(
            "User-agent: *\nDisallow: /\n",
            content_type="text/plain; charset=utf-8",
        )


class AssetView(View):
    def get(self, request: HttpRequest, asset_path: str = "") -> HttpResponse:
        url_path = request.path
        resolved = resolve_asset(url_path)
        if resolved is None:
            return HttpResponse("Not found", status=404, content_type="text/plain; charset=utf-8")
        body = resolved.body
        if body is None and resolved.path is not None:
            body = resolved.path.read_bytes()
        if body is None:
            return HttpResponse(
                "Not found",
                status=404,
                content_type="text/plain; charset=utf-8",
            )  # pragma: no cover
        response = HttpResponse(body, content_type=resolved.content_type)
        response["ETag"] = '"' + hashlib.sha256(body).hexdigest() + '"'
        request.baseline_kind = resolved.kind  # type: ignore[attr-defined]
        response.baseline_kind = resolved.kind  # type: ignore[attr-defined]
        return response


class StartView(TemplateView):
    template_name = "service/start.html"

    def get(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
        lang = str(kwargs.get("lang") or "en")
        welsh = lang == "cy"

        def pick(english: str, cymraeg: str) -> str:
            return cymraeg if welsh else english

        heading = pick("Apply for a rod fishing licence", "Gwneud cais am drwydded bysgota")
        context = _layout(request, heading=heading, lang=lang, show_feedback=True)
        context.update(
            {
                "lede": pick(
                    "Use this service to apply for a licence to fish with a rod.",
                    "Defnyddiwch y gwasanaeth hwn i wneud cais am drwydded i bysgota gyda gwialen.",
                ),
                "timing": pick("Applying takes about 10 minutes.", "Mae’n cymryd tua 10 munud."),
                "start_button": {
                    "text": pick("Start now", "Dechrau nawr"),
                    "href": "/task-list",
                    "isStartButton": True,
                },
                "notification": {
                    "titleText": pick("Important", "Pwysig"),
                    "text": pick(
                        "The 2026 to 2027 rod licence is now available.",
                        "Mae trwydded gwialen 2026 i 2027 ar gael nawr.",
                    ),
                },
                "warning": {
                    "text": pick(
                        "You must have a valid rod licence before you fish.",
                        "Rhaid i chi gael trwydded gwialen ddilys cyn i chi bysgota.",
                    ),
                    "iconFallbackText": pick("Warning", "Rhybudd"),
                },
                "inset": {
                    "text": pick(
                        "You need to be 13 or over. This example does not take payment.",
                        "Mae gweddill yr enghraifft hon yn Saesneg.",
                    )
                },
                "details": {
                    "summaryText": pick("What you will need", "Beth fydd ei angen arnoch"),
                    "html": pick(
                        '<ul class="govuk-list govuk-list--bullet">'
                        "<li>Your name</li><li>Your date of birth</li><li>Your address</li></ul>",
                        '<ul class="govuk-list govuk-list--bullet">'
                        "<li>Eich enw</li><li>Eich dyddiad geni</li><li>Eich cyfeiriad</li></ul>",
                    ),
                },
            }
        )
        # Mark details html as Safe via govuk_options pattern in template using mark — use Safe
        from govuk_components.rendering.params import Safe

        context["details"]["html"] = Safe(context["details"]["html"])
        return render(request, self.template_name, context)


class NewApplicationView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        clear_application(request)
        clear_errors(request)
        return redirect("/")


class TaskListView(TemplateView):
    template_name = "service/task_list.html"

    def get(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
        application = get_application(request)
        context = _layout(
            request,
            heading="Your application",
            back_link={"text": "Back", "href": "/"},
            personal=True,
        )
        sections = task_sections(application)
        context["sections"] = [
            {
                "heading": section.heading,
                "id_prefix": section.id_prefix,
                "items": section.items,
                "task_list": {"idPrefix": section.id_prefix, "items": section.items},
            }
            for section in sections
        ]
        return render(request, self.template_name, context)


class StepFormView(_JourneyFormView):
    """Base for each licence journey question page."""

    step_id: ClassVar[str] = ""
    step: Step
    template_name = "service/step.html"
    http_method_names = ["get", "post", "head", "options"]

    def dispatch(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
        step = step_by_id(self.step_id)
        if step is None:
            return HttpResponse("Not found", status=404)  # pragma: no cover
        self.step = step
        return cast(HttpResponse, super().dispatch(request, *args, **kwargs))

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        if self.request.method == "POST":
            kwargs["data"] = self._bind_post(self.request)
        if self.form_class in {DateOfBirthForm, StartMonthForm}:
            kwargs["now"] = _now()
        return kwargs

    def _bind_post(self, request: HttpRequest) -> dict[str, Any]:
        post = request.POST
        mapping: dict[str, Any] = {
            STEP_NAME: {
                "first_name": post.get("first-name", ""),
                "last_name": post.get("last-name", ""),
            },
            STEP_DATE_OF_BIRTH: {
                "day": post.get("date-of-birth-day", ""),
                "month": post.get("date-of-birth-month", ""),
                "year": post.get("date-of-birth-year", ""),
            },
            STEP_EMAIL: {"email": post.get("email", "")},
            STEP_CONTACT_PREFERENCE: {
                "contact_by": post.get("contact-by", ""),
                "telephone": post.get("telephone", ""),
            },
            STEP_WHERE_YOU_WILL_FISH: {"regions": post.getlist("regions")},
            STEP_LICENCE_LENGTH: {"licence_length": post.get("licence-length", "")},
            STEP_START_MONTH: {"start_month": post.get("start-month", "")},
            STEP_ADDRESS: {
                "address_line_1": post.get("address-line-1", ""),
                "address_line_2": post.get("address-line-2", ""),
                "town": post.get("town", ""),
                "postcode": post.get("postcode", ""),
            },
            STEP_EVIDENCE: {"evidence": self._evidence_name(request)},
            STEP_ADDITIONAL_DETAILS: {
                "additional_details": post.get("additional-details", "")
            },
            STEP_CREATE_A_PASSWORD: {
                "password": post.get("password", ""),
                "password_confirm": post.get("password-confirm", ""),
            },
        }
        return cast(dict[str, Any], mapping.get(self.step_id, {}))

    def _evidence_name(self, request: HttpRequest) -> str:
        upload = request.FILES.get("evidence")
        if upload is None:
            return ""
        name = safe_filename(getattr(upload, "name", "") or "")
        return name or ""

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        application = get_application(self.request)
        errors = _errors_from_dicts(pop_errors_for(self.request, self.step.path))
        return_to = ""
        if self.request.GET.get("return") == "check-answers":
            return_to = "check-answers"
        back = "/task-list"
        if return_to:
            back = "/check-answers"
        else:
            previous = previous_step(self.step_id)
            if previous is not None:
                back = previous.path
        layout = _layout(
            self.request,
            heading=self.step.heading,
            has_errors=bool(errors),
            back_link={"text": "Back", "href": back},
            main_classes="govuk-main-wrapper--l",
            personal=True,
        )
        context.update(layout)
        field_context = self._field_context(application, errors)
        context.update(field_context)
        summary = govuk_options.error_summary(errors)
        if summary is not None:
            context["error_summary"] = summary
        if return_to:
            context["return_to"] = return_to
        context["step"] = self.step
        context["continue_button"] = {"text": "Continue"}
        return context

    def _field_context(
        self, application: Application, errors: list[FieldError]
    ) -> dict[str, Any]:
        builders: dict[str, Any] = {
            STEP_NAME: lambda: govuk_options.name_fields(application, errors),
            STEP_DATE_OF_BIRTH: lambda: govuk_options.date_field(application, errors),
            STEP_EMAIL: lambda: govuk_options.email_field(application, errors),
            STEP_CONTACT_PREFERENCE: lambda: govuk_options.contact_fields(
                application, errors
            ),
            STEP_WHERE_YOU_WILL_FISH: lambda: govuk_options.region_fields(
                application, errors
            ),
            STEP_LICENCE_LENGTH: lambda: govuk_options.licence_fields(application, errors),
            STEP_START_MONTH: lambda: govuk_options.month_field(
                application, errors, _now()
            ),
            STEP_ADDRESS: lambda: govuk_options.address_fields(application, errors),
            STEP_EVIDENCE: lambda: {
                **govuk_options.evidence_field(application, errors),
                "enctype": "multipart/form-data",
            },
            STEP_ADDITIONAL_DETAILS: lambda: govuk_options.details_field(
                application, errors
            ),
            STEP_CREATE_A_PASSWORD: lambda: govuk_options.password_fields(errors),
        }
        builder = builders.get(self.step_id)
        return builder() if builder else {}

    def form_valid(self, form: Any) -> HttpResponse:
        application = get_application(self.request)
        application = self._apply(application, form, valid=True)
        save_application(self.request, application)
        clear_errors(self.request)
        if self.request.POST.get("returnTo") == "check-answers":
            return redirect("/check-answers")
        nxt = next_step(self.step_id)
        if nxt is not None:
            return redirect(nxt.path)
        return redirect("/check-answers")

    def form_invalid(self, form: Any) -> HttpResponse:
        application = get_application(self.request)
        application = self._apply(application, form, valid=False)
        save_application(self.request, application)
        errors = self._errors_from_invalid(form)
        set_errors(self.request, self.step.path, [err.as_dict() for err in errors])
        target = self.step.path
        if self.request.POST.get("returnTo") == "check-answers":
            target = f"{self.step.path}?return=check-answers"
        return redirect(target)

    def _errors_from_invalid(self, form: Any) -> list[FieldError]:
        # Re-run validate helpers from cleaned/raw data for accurate field ids.
        data = form.data if hasattr(form, "data") else {}
        return self._validate_data(data)

    def _validate_data(self, data: dict[str, Any]) -> list[FieldError]:
        from service.validate import (
            validate_additional_details,
            validate_address,
            validate_contact_preference,
            validate_date_of_birth,
            validate_email,
            validate_evidence,
            validate_licence_length,
            validate_name,
            validate_password,
            validate_regions,
            validate_start_month,
        )

        sid = self.step_id
        if sid == STEP_NAME:
            return validate_name(
                str(data.get("first_name") or ""), str(data.get("last_name") or "")
            )
        if sid == STEP_DATE_OF_BIRTH:
            return validate_date_of_birth(
                str(data.get("day") or ""),
                str(data.get("month") or ""),
                str(data.get("year") or ""),
                _now(),
            )
        if sid == STEP_EMAIL:
            return validate_email(str(data.get("email") or ""))
        if sid == STEP_CONTACT_PREFERENCE:
            return validate_contact_preference(
                str(data.get("contact_by") or ""),
                str(data.get("telephone") or ""),
            )
        if sid == STEP_WHERE_YOU_WILL_FISH:
            regions = data.get("regions") or []
            if not isinstance(regions, list):  # pragma: no cover
                regions = list(regions)
            return validate_regions([str(r) for r in regions])
        if sid == STEP_LICENCE_LENGTH:
            return validate_licence_length(str(data.get("licence_length") or ""))
        if sid == STEP_START_MONTH:
            return validate_start_month(str(data.get("start_month") or ""), _now())
        if sid == STEP_ADDRESS:
            return validate_address(
                str(data.get("address_line_1") or ""),
                str(data.get("town") or ""),
                str(data.get("postcode") or ""),
            )
        if sid == STEP_EVIDENCE:
            return validate_evidence(str(data.get("evidence") or ""))
        if sid == STEP_ADDITIONAL_DETAILS:
            return validate_additional_details(str(data.get("additional_details") or ""))
        return validate_password(
            str(data.get("password") or ""),
            str(data.get("password_confirm") or ""),
        )

    def _apply(self, application: Application, form: Any, *, valid: bool) -> Application:
        data = form.data if hasattr(form, "data") else {}
        cleaned = getattr(form, "cleaned_data", None) or data
        sid = self.step_id
        if sid == STEP_NAME:
            return save_name(
                application,
                str(cleaned.get("first_name") or data.get("first_name") or ""),
                str(cleaned.get("last_name") or data.get("last_name") or ""),
                valid=valid,
            )
        if sid == STEP_DATE_OF_BIRTH:
            return save_date(
                application,
                str(data.get("day") or ""),
                str(data.get("month") or ""),
                str(data.get("year") or ""),
                valid=valid,
            )
        if sid == STEP_EMAIL:
            return save_email(application, str(data.get("email") or ""), valid=valid)
        if sid == STEP_CONTACT_PREFERENCE:
            return save_contact(
                application,
                str(data.get("contact_by") or ""),
                str(data.get("telephone") or ""),
                valid=valid,
            )
        if sid == STEP_WHERE_YOU_WILL_FISH:
            regions = data.get("regions") or []
            if not isinstance(regions, list):  # pragma: no cover
                regions = list(regions)
            return save_regions(application, [str(r) for r in regions], valid=valid)
        if sid == STEP_LICENCE_LENGTH:
            return save_licence(
                application, str(data.get("licence_length") or ""), valid=valid
            )
        if sid == STEP_START_MONTH:
            return save_month(
                application, str(data.get("start_month") or ""), valid=valid
            )
        if sid == STEP_ADDRESS:
            return save_address(
                application,
                AddressValues(
                    line1=str(data.get("address_line_1") or ""),
                    line2=str(data.get("address_line_2") or ""),
                    town=str(data.get("town") or ""),
                    postcode=str(data.get("postcode") or ""),
                ),
                valid=valid,
            )
        if sid == STEP_EVIDENCE:
            filename = str(data.get("evidence") or "")
            has_file = bool(filename)
            return save_evidence(
                application, filename, has_file=has_file, valid=valid
            )
        if sid == STEP_ADDITIONAL_DETAILS:
            return save_details(
                application, str(data.get("additional_details") or ""), valid=valid
            )
        return save_password(application, valid=valid)


class NameView(StepFormView):
    step_id = STEP_NAME
    form_class = NameForm
    template_name = "service/name.html"


class DateOfBirthView(StepFormView):
    step_id = STEP_DATE_OF_BIRTH
    form_class = DateOfBirthForm
    template_name = "service/date_of_birth.html"


class EmailView(StepFormView):
    step_id = STEP_EMAIL
    form_class = EmailForm
    template_name = "service/email.html"


class ContactPreferenceView(StepFormView):
    step_id = STEP_CONTACT_PREFERENCE
    form_class = ContactPreferenceForm
    template_name = "service/contact_preference.html"


class WhereYouWillFishView(StepFormView):
    step_id = STEP_WHERE_YOU_WILL_FISH
    form_class = WhereYouWillFishForm
    template_name = "service/where_you_will_fish.html"


class LicenceLengthView(StepFormView):
    step_id = STEP_LICENCE_LENGTH
    form_class = LicenceLengthForm
    template_name = "service/licence_length.html"


class StartMonthView(StepFormView):
    step_id = STEP_START_MONTH
    form_class = StartMonthForm
    template_name = "service/start_month.html"


class AddressView(StepFormView):
    step_id = STEP_ADDRESS
    form_class = AddressForm
    template_name = "service/address.html"


class EvidenceView(StepFormView):
    step_id = STEP_EVIDENCE
    form_class = EvidenceForm
    template_name = "service/evidence.html"


class AdditionalDetailsView(StepFormView):
    step_id = STEP_ADDITIONAL_DETAILS
    form_class = AdditionalDetailsForm
    template_name = "service/additional_details.html"


class CreatePasswordView(StepFormView):
    step_id = STEP_CREATE_A_PASSWORD
    form_class = PasswordForm
    template_name = "service/create_a_password.html"


class CheckAnswersView(View):
    template_name = "service/check_answers.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        application = get_application(request)
        if application.submitted:
            return redirect("/confirmation")
        incomplete = first_incomplete_step(application)
        if incomplete is not None:
            return redirect(incomplete.path)
        context = _layout(
            request,
            heading="Check your answers",
            back_link={"text": "Back", "href": "/create-a-password"},
            main_classes="govuk-main-wrapper--l",
            personal=True,
        )
        rows = summary_rows(application, _now())
        context["summary_list"] = {"rows": rows}
        context["submit_button"] = {"text": "Submit application"}
        return render(request, self.template_name, context)

    def post(self, request: HttpRequest) -> HttpResponse:
        application = get_application(request)
        if application.submitted:
            return redirect("/confirmation")
        incomplete = first_incomplete_step(application)
        if incomplete is not None:
            return redirect(incomplete.path)
        if not request.session.session_key:  # pragma: no cover — session exists after journey
            request.session.create()
        application.submitted = True
        application.reference = reference_for(request.session.session_key or "session")
        save_application(request, application)
        return redirect("/confirmation")


class ConfirmationView(TemplateView):
    template_name = "service/confirmation.html"

    def get(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
        application = get_application(request)
        if not application.submitted:
            return redirect("/task-list")
        context = _layout(
            request,
            heading="Application complete",
            show_feedback=True,
            personal=True,
        )
        context["panel"] = govuk_options.confirmation_panel(application.reference)
        return render(request, self.template_name, context)


class FeesView(TemplateView):
    template_name = "service/fees.html"

    def get(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
        context = _layout(
            request, heading="Licence fees", breadcrumbs=crumbs("Licence fees")
        )
        context["table"] = govuk_options.fees_table()
        return render(request, self.template_name, context)


class HelpView(TemplateView):
    template_name = "service/help.html"

    def get(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
        context = _layout(
            request,
            heading="Help",
            show_feedback=True,
            breadcrumbs=crumbs("Help"),
        )
        context["accordion"] = govuk_options.help_accordion()
        return render(request, self.template_name, context)


class GuidanceView(TemplateView):
    template_name = "service/guidance.html"

    def get(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
        context = _layout(
            request, heading="Guidance", breadcrumbs=crumbs("Guidance")
        )
        context["tabs"] = govuk_options.guidance_tabs()
        return render(request, self.template_name, context)


class UpdatesView(View):
    template_name = "service/updates.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        requested = request.GET.get("page", "")
        if requested not in {"", "1", "2"}:
            return redirect("/updates")
        page = 2 if requested == "2" else 1
        pagination: dict[str, Any] = {
            "items": [
                {"number": 1, "href": "/updates", "current": page == 1},
                {"number": 2, "href": "/updates?page=2", "current": page == 2},
            ]
        }
        if page > 1:
            pagination["previous"] = {"href": "/updates"}
        if page < 2:
            pagination["next"] = {"href": "/updates?page=2"}
        body = (
            "There are no further fee changes planned in this example."
            if page == 2
            else "Example fees for the 2026 to 2027 season are on the fees page."
        )
        context = _layout(
            request,
            heading="Service updates",
            breadcrumbs=crumbs("Service updates"),
        )
        context["body"] = body
        context["pagination"] = pagination
        return render(request, self.template_name, context)


class CookiesView(_CookieFormView):
    template_name = "service/cookies.html"
    form_class = CookieSettingsForm
    success_url = "/cookies"

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        if self.request.method == "POST":
            kwargs["data"] = {"analytics": self.request.POST.get("analytics", "")}
        return kwargs

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        errors = _errors_from_dicts(pop_errors_for(self.request, "/cookies"))
        notice = pop_notice_for(self.request, "/cookies")
        layout = _layout(
            self.request,
            heading="Cookies",
            has_errors=bool(errors),
            personal=True,
            breadcrumbs=crumbs("Cookies"),
        )
        context.update(layout)
        fields = govuk_options.cookie_fields(get_cookie_choice(self.request), errors)
        context.update(fields)
        summary = govuk_options.error_summary(errors)
        if summary is not None:
            context["error_summary"] = summary
        if notice:
            context["notice"] = {
                "type": "success",
                "titleText": "Success",
                "text": notice,
            }
        context["save_button"] = {"text": "Save cookie settings"}
        return context

    def form_valid(self, form: CookieSettingsForm) -> HttpResponse:
        choice = CHOICE_ACCEPT if form.cleaned_data.get("analytics") == "yes" else CHOICE_REJECT
        set_cookie_choice(self.request, choice)
        set_cookie_banner(self.request, "")
        clear_errors(self.request)
        set_notice(self.request, "/cookies", "Your cookie settings were saved")
        return redirect("/cookies")

    def form_invalid(self, form: CookieSettingsForm) -> HttpResponse:
        from service.validate import validate_cookie_choice

        errors = validate_cookie_choice(str(form.data.get("analytics") or ""))
        set_errors(self.request, "/cookies", [err.as_dict() for err in errors])
        return redirect("/cookies")


class AccessibilityView(TemplateView):
    template_name = "service/accessibility.html"

    def get(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
        context = _layout(
            request,
            heading="Accessibility statement",
            show_feedback=True,
            breadcrumbs=crumbs("Accessibility statement"),
        )
        return render(request, self.template_name, context)


class AboutView(TemplateView):
    template_name = "service/about.html"

    def get(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
        context = _layout(
            request,
            heading="About this example",
            show_feedback=True,
            breadcrumbs=crumbs("About this example"),
        )
        return render(request, self.template_name, context)


class CookieChoicesView(View):
    def post(self, request: HttpRequest) -> HttpResponse:
        choice = request.POST.get("cookies", "")
        if choice in {CHOICE_ACCEPT, CHOICE_REJECT}:
            set_cookie_choice(request, choice)
            set_cookie_banner(request, choice)
        elif choice == "hide":  # pragma: no branch
            set_cookie_banner(request, "")
        return redirect(safe_return_path(request.POST.get("returnPath", "/")))

    def get(self, request: HttpRequest) -> HttpResponse:
        return HttpResponseNotAllowed(["POST"])


class ExamplesView(TemplateView):
    template_name = "service/examples.html"

    def get(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
        if not settings.DEMOS_ENABLED:
            return _demos_not_found(request)
        context = _layout(
            request, heading="Example pages", breadcrumbs=crumbs("Example pages")
        )
        return render(request, self.template_name, context)


class ExitThisPageView(TemplateView):
    template_name = "service/exit_this_page.html"

    def get(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
        if not settings.DEMOS_ENABLED:
            return _demos_not_found(request)
        context = _layout(
            request,
            heading="Exit this page",
            back_link={"text": "Back", "href": "/examples"},
            exit_this_page={"redirectUrl": "https://www.bbc.co.uk/weather"},
        )
        context["warning"] = {
            "text": "Use this component only on services where someone may be in danger.",
            "iconFallbackText": "Warning",
        }
        context["inset"] = {
            "text": (
                "This page is an example of the component. It is not part of the rod licence "
                "application. Choosing the button leaves this example and opens the BBC weather "
                "forecast."
            )
        }
        return render(request, self.template_name, context)


class UnavailableView(TemplateView):
    template_name = "service/unavailable.html"

    def get(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
        if not settings.DEMOS_ENABLED:
            return _demos_not_found(request)
        context = _layout(
            request,
            heading="Sorry, the service is unavailable",
            back_link={"text": "Back", "href": "/examples"},
        )
        return render(request, self.template_name, context)


class ProblemView(TemplateView):
    template_name = "service/problem.html"

    def get(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
        if not settings.DEMOS_ENABLED:
            return _demos_not_found(request)
        context = _layout(
            request, heading="Sorry, there is a problem with the service"
        )
        return render(request, self.template_name, context)


def _not_found_context(request: HttpRequest) -> dict[str, Any]:
    return _layout(request, heading="Page not found")


def _demos_not_found(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "service/not_found.html",
        _not_found_context(request),
        status=404,
    )


def not_found(request: HttpRequest, exception: Exception | None = None) -> HttpResponse:
    return render(request, "service/not_found.html", _not_found_context(request), status=404)
