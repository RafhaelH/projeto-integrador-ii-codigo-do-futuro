from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import FormView, TemplateView

from apps.accounts.mixins import RoleRequiredMixin
from apps.accounts.models import UserRole
from apps.enrollments.models import Enrollment, EnrollmentStatus
from apps.workshops.models import ClassGroup, ClassGroupStatus, Meeting, MeetingStatus

from .forms import (
    AttendanceFormSet,
    CertificateRevocationForm,
    EvaluationForm,
    ProjectReviewForm,
    StudentProjectForm,
)
from .models import Attendance, Certificate, Evaluation, StudentProject
from .pdf import render_certificate_pdf
from .selectors import certificates_for_user
from .services import (
    ACADEMIC_ENROLLMENT_STATUSES,
    calculate_attendance_summary,
    complete_class_group,
    issue_certificate,
    record_meeting_attendance,
    review_student_project,
    revoke_certificate,
    save_evaluation,
    save_student_project,
)


class ClassAttendanceAccessMixin(RoleRequiredMixin):
    allowed_roles = (UserRole.ADMIN, UserRole.INSTRUCTOR)

    def get_class_queryset(self):
        queryset = ClassGroup.objects.select_related("workshop")
        if self.request.user.role == UserRole.INSTRUCTOR:
            queryset = queryset.filter(
                instructor_links__instructor__user=self.request.user,
                instructor_links__instructor__is_active=True,
            )
        return queryset.distinct()


class ClassAttendanceView(ClassAttendanceAccessMixin, TemplateView):
    template_name = "learning/class_attendance.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        self.class_group = get_object_or_404(self.get_class_queryset(), pk=kwargs["class_pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        enrollments = self.class_group.enrollments.filter(
            status__in=ACADEMIC_ENROLLMENT_STATUSES
        ).select_related("participant", "student_project", "evaluation", "certificate")
        context.update(
            {
                "class_group": self.class_group,
                "meetings": self.class_group.meetings.prefetch_related("attendances"),
                "frequency_rows": [
                    (enrollment, calculate_attendance_summary(enrollment))
                    for enrollment in enrollments
                ],
            }
        )
        return context


class MeetingAttendanceView(ClassAttendanceAccessMixin, FormView):
    form_class = AttendanceFormSet
    template_name = "learning/attendance_form.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        self.meeting = get_object_or_404(
            Meeting.objects.select_related("class_group", "class_group__workshop"),
            pk=kwargs["meeting_pk"],
        )
        if not self.get_class_queryset().filter(pk=self.meeting.class_group_id).exists():
            raise PermissionDenied
        if self.meeting.status == MeetingStatus.CANCELLED:
            raise PermissionDenied("Encontros cancelados não aceitam chamada.")
        return super().dispatch(request, *args, **kwargs)

    def get_enrollments(self):
        return list(
            Enrollment.objects.filter(
                class_group=self.meeting.class_group,
                status__in=ACADEMIC_ENROLLMENT_STATUSES,
            )
            .select_related("participant")
            .order_by("participant__full_name")
        )

    def get_initial(self):
        existing = {
            attendance.enrollment_id: attendance
            for attendance in Attendance.objects.filter(meeting=self.meeting)
        }
        return [
            {
                "enrollment_id": enrollment.pk,
                "participant_name": enrollment.participant.full_name,
                "status": (
                    existing[enrollment.pk].status if enrollment.pk in existing else "PRESENT"
                ),
                "note": (existing[enrollment.pk].note if enrollment.pk in existing else ""),
            }
            for enrollment in self.get_enrollments()
        ]

    def form_valid(self, form):
        records = {
            str(entry.cleaned_data["enrollment_id"]): {
                "status": entry.cleaned_data["status"],
                "note": entry.cleaned_data["note"],
            }
            for entry in form.forms
        }
        try:
            record_meeting_attendance(self.meeting, records=records, actor=self.request.user)
        except ValidationError as error:
            messages.error(self.request, "; ".join(error.messages))
            return self.form_invalid(form)
        messages.success(self.request, "Chamada registrada e percentuais atualizados.")
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse(
            "learning:class-attendance",
            kwargs={"class_pk": self.meeting.class_group_id},
        )

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs) | {
            "meeting": self.meeting,
            "class_group": self.meeting.class_group,
            "cancel_url": self.get_success_url(),
        }


class ParticipantFrequencyView(RoleRequiredMixin, TemplateView):
    allowed_roles = (UserRole.PARTICIPANT,)
    template_name = "learning/participant_frequency.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        enrollments = Enrollment.objects.filter(
            participant__user=self.request.user,
            status__in=ACADEMIC_ENROLLMENT_STATUSES,
        ).select_related(
            "participant",
            "class_group",
            "class_group__workshop",
            "student_project",
            "evaluation",
            "certificate",
        )
        context["frequency_rows"] = [
            (enrollment, calculate_attendance_summary(enrollment)) for enrollment in enrollments
        ]
        return context


class ParticipantProjectView(RoleRequiredMixin, FormView):
    allowed_roles = (UserRole.PARTICIPANT,)
    form_class = StudentProjectForm
    template_name = "learning/entity_form.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        self.enrollment = get_object_or_404(
            Enrollment.objects.select_related("participant", "class_group"),
            pk=kwargs["enrollment_pk"],
            participant__user=request.user,
        )
        if (
            self.enrollment.status != EnrollmentStatus.CONFIRMED
            or self.enrollment.class_group.status != ClassGroupStatus.IN_PROGRESS
        ):
            raise PermissionDenied("O projeto só pode ser alterado durante a turma.")
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = StudentProject.objects.filter(enrollment=self.enrollment).first()
        return kwargs

    def form_valid(self, form):
        try:
            save_student_project(
                self.enrollment,
                data=form.cleaned_data,
                actor=self.request.user,
            )
        except (PermissionDenied, ValidationError) as error:
            message = "; ".join(error.messages) if hasattr(error, "messages") else str(error)
            form.add_error(None, message)
            return self.form_invalid(form)
        messages.success(self.request, "Projeto atualizado com sucesso.")
        return redirect("learning:participant-frequency")

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs) | {
            "page_title": "Meu projeto",
            "page_description": self.enrollment.class_group.title,
            "cancel_url": reverse("learning:participant-frequency"),
        }


class ProjectReviewView(ClassAttendanceAccessMixin, FormView):
    form_class = ProjectReviewForm
    template_name = "learning/entity_form.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        self.project = get_object_or_404(
            StudentProject.objects.select_related(
                "enrollment__class_group",
                "enrollment__participant",
            ),
            pk=kwargs["pk"],
        )
        if not self.get_class_queryset().filter(pk=self.project.enrollment.class_group_id).exists():
            raise PermissionDenied
        if (
            self.project.enrollment.status != EnrollmentStatus.CONFIRMED
            or self.project.enrollment.class_group.status != ClassGroupStatus.IN_PROGRESS
        ):
            raise PermissionDenied("A revisão só pode ser alterada durante a turma.")
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        return super().get_form_kwargs() | {"instance": self.project}

    def form_valid(self, form):
        try:
            review_student_project(
                self.project,
                review_notes=form.cleaned_data["review_notes"],
                actor=self.request.user,
            )
        except ValidationError as error:
            form.add_error(None, "; ".join(error.messages))
            return self.form_invalid(form)
        messages.success(self.request, "Devolutiva do projeto registrada.")
        return redirect(
            "learning:class-attendance",
            class_pk=self.project.enrollment.class_group_id,
        )

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs) | {
            "page_title": f"Revisar projeto de {self.project.enrollment.participant}",
            "page_description": self.project.title,
            "cancel_url": reverse(
                "learning:class-attendance",
                kwargs={"class_pk": self.project.enrollment.class_group_id},
            ),
        }


class EvaluationView(ClassAttendanceAccessMixin, FormView):
    form_class = EvaluationForm
    template_name = "learning/entity_form.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        self.enrollment = get_object_or_404(
            Enrollment.objects.select_related("participant", "class_group"),
            pk=kwargs["enrollment_pk"],
        )
        if not self.get_class_queryset().filter(pk=self.enrollment.class_group_id).exists():
            raise PermissionDenied
        if (
            self.enrollment.status != EnrollmentStatus.CONFIRMED
            or self.enrollment.class_group.status != ClassGroupStatus.IN_PROGRESS
        ):
            raise PermissionDenied("A avaliação só pode ser alterada durante a turma.")
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        return super().get_form_kwargs() | {
            "instance": Evaluation.objects.filter(enrollment=self.enrollment).first()
        }

    def form_valid(self, form):
        try:
            save_evaluation(
                self.enrollment,
                final_score=form.cleaned_data["final_score"],
                feedback=form.cleaned_data["feedback"],
                publish=form.cleaned_data["publish"],
                actor=self.request.user,
            )
        except ValidationError as error:
            form.add_error(None, "; ".join(error.messages))
            return self.form_invalid(form)
        messages.success(self.request, "Avaliação final registrada.")
        return redirect("learning:class-attendance", class_pk=self.enrollment.class_group_id)

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs) | {
            "page_title": f"Avaliar {self.enrollment.participant}",
            "page_description": self.enrollment.class_group.title,
            "cancel_url": reverse(
                "learning:class-attendance",
                kwargs={"class_pk": self.enrollment.class_group_id},
            ),
        }


class CompleteClassGroupView(RoleRequiredMixin, View):
    allowed_roles = (UserRole.ADMIN,)

    def post(self, request, class_pk):
        class_group = get_object_or_404(ClassGroup, pk=class_pk)
        try:
            summary = complete_class_group(class_group, actor=request.user)
        except ValidationError as error:
            messages.error(request, "; ".join(error.messages))
        else:
            messages.success(
                request,
                f"Turma concluída: {summary.approved} aprovado(s) e "
                f"{summary.not_completed} não concluinte(s).",
            )
        return redirect("learning:class-attendance", class_pk=class_pk)



class CertificateListView(RoleRequiredMixin, TemplateView):
    allowed_roles = (UserRole.ADMIN, UserRole.INSTRUCTOR, UserRole.PARTICIPANT)
    template_name = "learning/certificate_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["certificates"] = certificates_for_user(self.request.user)
        if self.request.user.role == UserRole.ADMIN:
            context["eligible_enrollments"] = (
                Enrollment.objects.filter(
                    status=EnrollmentStatus.APPROVED,
                    certificate__isnull=True,
                )
                .select_related("participant", "class_group__workshop")
                .order_by("participant__full_name")
            )
        return context


class CertificateDetailView(RoleRequiredMixin, TemplateView):
    allowed_roles = (UserRole.ADMIN, UserRole.INSTRUCTOR, UserRole.PARTICIPANT)
    template_name = "learning/certificate_detail.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        self.certificate = get_object_or_404(
            certificates_for_user(request.user),
            pk=kwargs["pk"],
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs) | {
            "certificate": self.certificate,
            "revocation_form": CertificateRevocationForm(),
        }


class CertificateDownloadView(RoleRequiredMixin, View):
    allowed_roles = (UserRole.ADMIN, UserRole.INSTRUCTOR, UserRole.PARTICIPANT)

    def get(self, request, pk):
        certificate = get_object_or_404(certificates_for_user(request.user), pk=pk)
        if not certificate.is_active:
            raise PermissionDenied("Certificados revogados não podem ser baixados.")
        response = HttpResponse(
            render_certificate_pdf(certificate),
            content_type="application/pdf",
        )
        response["Content-Disposition"] = (
            f'attachment; filename="certificado-{certificate.verification_code}.pdf"'
        )
        return response


class IssueCertificateView(RoleRequiredMixin, View):
    allowed_roles = (UserRole.ADMIN,)

    def post(self, request, enrollment_pk):
        enrollment = get_object_or_404(Enrollment, pk=enrollment_pk)
        try:
            certificate = issue_certificate(enrollment, actor=request.user)
        except ValidationError as error:
            messages.error(request, "; ".join(error.messages))
            return redirect("learning:certificate-list")
        messages.success(request, "Certificado emitido com sucesso.")
        return redirect("learning:certificate-detail", pk=certificate.pk)


class RevokeCertificateView(RoleRequiredMixin, View):
    allowed_roles = (UserRole.ADMIN,)

    def post(self, request, pk):
        certificate = get_object_or_404(Certificate, pk=pk)
        form = CertificateRevocationForm(request.POST)
        if not form.is_valid():
            messages.error(request, "Informe o motivo da revogação.")
            return redirect("learning:certificate-detail", pk=pk)
        try:
            revoke_certificate(
                certificate,
                reason=form.cleaned_data["reason"],
                actor=request.user,
            )
        except ValidationError as error:
            messages.error(request, "; ".join(error.messages))
        else:
            messages.success(request, "Certificado revogado e bloqueado para download.")
        return redirect("learning:certificate-detail", pk=pk)
