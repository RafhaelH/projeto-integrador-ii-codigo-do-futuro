import csv
from collections.abc import Callable
from decimal import Decimal

from django.http import HttpResponse
from django.utils import timezone

from apps.enrollments.models import Enrollment, EnrollmentStatus
from apps.learning.services import ACADEMIC_ENROLLMENT_STATUSES, calculate_attendance_summary


def _format_date(value) -> str:
    if not value:
        return ""
    if hasattr(value, "hour"):
        value = timezone.localtime(value)
        return value.strftime("%d/%m/%Y %H:%M")
    return value.strftime("%d/%m/%Y")


def _format_decimal(value: Decimal | None) -> str:
    if value is None:
        return ""
    return str(value).replace(".", ",")


def _period_description(filters: dict) -> str:
    period_start = filters.get("period_start")
    period_end = filters.get("period_end")
    if period_start and period_end:
        return f"{_format_date(period_start)} a {_format_date(period_end)}"
    if period_start:
        return f"a partir de {_format_date(period_start)}"
    if period_end:
        return f"até {_format_date(period_end)}"
    return "todo o período"


def _base_response(filename: str) -> HttpResponse:
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response.write("\ufeff")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


def _write_metadata(
    writer,
    *,
    title: str,
    class_groups,
    filters: dict,
) -> None:
    writer.writerow(["Relatório", title])
    writer.writerow(["Período das turmas", _period_description(filters)])
    writer.writerow(["Universo", f"{class_groups.count()} turma(s)"])
    writer.writerow([])


def _enrollment_report(class_groups, *, filters: dict) -> HttpResponse:
    response = _base_response("relatorio-inscricoes.csv")
    writer = csv.writer(response, delimiter=";")
    _write_metadata(
        writer,
        title="Inscrições",
        class_groups=class_groups,
        filters=filters,
    )
    writer.writerow(
        [
            "Participante",
            "Oficina",
            "Turma",
            "Situação",
            "Data da inscrição",
            "Motivo da situação",
        ]
    )
    enrollments = (
        Enrollment.objects.filter(class_group__in=class_groups)
        .select_related("participant", "class_group__workshop")
        .order_by("class_group__code", "participant__full_name")
    )
    for enrollment in enrollments:
        writer.writerow(
            [
                enrollment.participant.full_name,
                enrollment.class_group.workshop.title,
                enrollment.class_group.code,
                enrollment.get_status_display(),
                _format_date(enrollment.created_at),
                enrollment.status_reason,
            ]
        )
    return response


def _attendance_report(class_groups, *, filters: dict) -> HttpResponse:
    response = _base_response("relatorio-frequencia.csv")
    writer = csv.writer(response, delimiter=";")
    _write_metadata(
        writer,
        title="Frequência",
        class_groups=class_groups,
        filters=filters,
    )
    writer.writerow(
        [
            "Participante",
            "Oficina",
            "Turma",
            "Encontros realizados",
            "Presenças",
            "Ausências",
            "Faltas justificadas",
            "Frequência",
        ]
    )
    enrollments = (
        Enrollment.objects.filter(
            class_group__in=class_groups,
            status__in=ACADEMIC_ENROLLMENT_STATUSES,
        )
        .select_related("participant", "class_group__workshop")
        .order_by("class_group__code", "participant__full_name")
    )
    for enrollment in enrollments:
        summary = calculate_attendance_summary(enrollment)
        writer.writerow(
            [
                enrollment.participant.full_name,
                enrollment.class_group.workshop.title,
                enrollment.class_group.code,
                summary.completed_meetings,
                summary.presents,
                summary.absences,
                summary.justified_absences,
                f"{_format_decimal(summary.percentage)}%",
            ]
        )
    return response


def _completion_report(class_groups, *, filters: dict) -> HttpResponse:
    response = _base_response("relatorio-conclusao.csv")
    writer = csv.writer(response, delimiter=";")
    _write_metadata(
        writer,
        title="Conclusão",
        class_groups=class_groups,
        filters=filters,
    )
    writer.writerow(
        [
            "Participante",
            "Oficina",
            "Turma",
            "Período",
            "Resultado",
            "Nota final",
            "Projeto entregue",
            "Certificado ativo",
            "Motivo",
        ]
    )
    enrollments = (
        Enrollment.objects.filter(
            class_group__in=class_groups,
            status__in=(
                EnrollmentStatus.APPROVED,
                EnrollmentStatus.NOT_COMPLETED,
            ),
        )
        .select_related(
            "participant",
            "class_group__workshop",
            "evaluation",
            "student_project",
            "certificate",
        )
        .order_by("class_group__code", "participant__full_name")
    )
    for enrollment in enrollments:
        evaluation = getattr(enrollment, "evaluation", None)
        project = getattr(enrollment, "student_project", None)
        certificate = getattr(enrollment, "certificate", None)
        class_group = enrollment.class_group
        writer.writerow(
            [
                enrollment.participant.full_name,
                class_group.workshop.title,
                class_group.code,
                f"{_format_date(class_group.start_date)} a {_format_date(class_group.end_date)}",
                enrollment.get_status_display(),
                _format_decimal(evaluation.final_score if evaluation else None),
                "Sim" if project and project.is_delivered else "Não",
                "Sim" if certificate and certificate.is_active else "Não",
                enrollment.status_reason,
            ]
        )
    return response


REPORT_BUILDERS: dict[str, Callable] = {
    "inscricoes": _enrollment_report,
    "frequencia": _attendance_report,
    "conclusao": _completion_report,
}


def export_report(
    report_kind: str,
    *,
    class_groups,
    filters: dict,
) -> HttpResponse:
    return REPORT_BUILDERS[report_kind](class_groups, filters=filters)
