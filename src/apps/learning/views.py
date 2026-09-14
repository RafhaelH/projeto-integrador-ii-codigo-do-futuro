from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import FormView, TemplateView

from apps.accounts.mixins import RoleRequiredMixin
from apps.accounts.models import UserRole
from apps.enrollments.models import Enrollment
from apps.workshops.models import ClassGroup, Meeting, MeetingStatus

from .forms import AttendanceFormSet
from .models import Attendance
from .services import (
    ACADEMIC_ENROLLMENT_STATUSES,
    calculate_attendance_summary,
    record_meeting_attendance,
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
        ).select_related("participant")
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
        ).select_related("participant", "class_group", "class_group__workshop")
        context["frequency_rows"] = [
            (enrollment, calculate_attendance_summary(enrollment)) for enrollment in enrollments
        ]
        return context
