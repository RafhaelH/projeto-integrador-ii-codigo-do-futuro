from django.urls import path

from .views import DashboardView, ExportReportView

app_name = "reporting"

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path(
        "relatorios/<str:report_kind>.csv",
        ExportReportView.as_view(),
        name="export",
    ),
]
