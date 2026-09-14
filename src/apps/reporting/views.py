from django.http import Http404, HttpResponseBadRequest
from django.views import View
from django.views.generic import TemplateView

from apps.accounts.mixins import AdminRequiredMixin, RoleRequiredMixin
from apps.accounts.models import UserRole
from apps.workshops.models import ClassGroup

from .csv_exports import REPORT_BUILDERS, export_report
from .forms import ReportingFilterForm
from .selectors import (
    class_groups_for_user,
    class_summary_rows,
    dashboard_snapshot,
    filter_class_groups,
)


def _filtered_classes(request) -> tuple[ReportingFilterForm, object, dict]:
    form = ReportingFilterForm(request.GET or None, user=request.user)
    if request.GET:
        if not form.is_valid():
            return form, ClassGroup.objects.none(), {"invalid": True}
        filters = form.cleaned_data
    else:
        filters = {}
    queryset = filter_class_groups(
        class_groups_for_user(request.user),
        filters=filters,
    )
    return form, queryset, filters


def _period_description(filters: dict) -> str:
    if filters.get("invalid"):
        return "um período inválido"
    period_start = filters.get("period_start")
    period_end = filters.get("period_end")
    if period_start and period_end:
        return f"{period_start:%d/%m/%Y} a {period_end:%d/%m/%Y}"
    if period_start:
        return f"a partir de {period_start:%d/%m/%Y}"
    if period_end:
        return f"até {period_end:%d/%m/%Y}"
    return "todo o período"


class DashboardView(RoleRequiredMixin, TemplateView):
    allowed_roles = (UserRole.ADMIN, UserRole.INSTRUCTOR)
    template_name = "reporting/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form, class_groups, filters = _filtered_classes(self.request)
        context.update(
            {
                "filter_form": form,
                "snapshot": dashboard_snapshot(class_groups),
                "class_rows": class_summary_rows(class_groups),
                "period_description": _period_description(filters),
                "filter_query": self.request.GET.urlencode(),
            }
        )
        return context


class ExportReportView(AdminRequiredMixin, View):
    def get(self, request, report_kind):
        if report_kind not in REPORT_BUILDERS:
            raise Http404
        form, class_groups, filters = _filtered_classes(request)
        if request.GET and not form.is_valid():
            return HttpResponseBadRequest("Filtros inválidos.")
        return export_report(
            report_kind,
            class_groups=class_groups,
            filters=filters,
        )
