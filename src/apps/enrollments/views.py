from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Count, F, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import FormView, ListView

from apps.accounts.mixins import AdminRequiredMixin, RoleRequiredMixin
from apps.accounts.models import UserRole
from apps.people.models import Participant
from apps.workshops.models import ClassGroup, ClassGroupStatus

from .forms import AdminEnrollmentCreateForm, CancellationForm, OptionalReasonForm, ReasonForm
from .models import Enrollment, EnrollmentStatus
from .services import (
    available_places,
    cancel_enrollment,
    confirm_enrollment,
    create_enrollment,
    promote_next_waitlisted,
    reject_enrollment,
)


def _error_messages(error: ValidationError) -> str:
    return "; ".join(error.messages)


class EnrollmentAccessMixin(RoleRequiredMixin):
    allowed_roles = (UserRole.ADMIN, UserRole.INSTRUCTOR, UserRole.PARTICIPANT)

    def get_queryset(self):
        queryset = Enrollment.objects.select_related(
            "participant", "participant__user", "class_group", "class_group__workshop"
        )
        user = self.request.user
        if user.role == UserRole.INSTRUCTOR:
            queryset = queryset.filter(
                class_group__instructor_links__instructor__user=user
            ).distinct()
        elif user.role == UserRole.PARTICIPANT:
            queryset = queryset.filter(participant__user=user)
        return queryset


class EnrollmentListView(EnrollmentAccessMixin, ListView):
    template_name = "enrollments/enrollment_list.html"
    context_object_name = "enrollments"
    paginate_by = 25

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get("q", "").strip()
        status = self.request.GET.get("status", "").strip()
        if query:
            queryset = queryset.filter(
                Q(participant__full_name__icontains=query)
                | Q(class_group__title__icontains=query)
                | Q(class_group__code__icontains=query)
            )
        if status in EnrollmentStatus.values:
            queryset = queryset.filter(status=status)
        return queryset

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs) | {"status_choices": EnrollmentStatus.choices}


class AvailableClassListView(RoleRequiredMixin, ListView):
    allowed_roles = (UserRole.PARTICIPANT,)
    template_name = "enrollments/available_classes.html"
    context_object_name = "class_groups"

    def get_queryset(self):
        now = timezone.now()
        participant = Participant.objects.filter(user=self.request.user, is_active=True).first()
        enrolled_ids = (
            participant.enrollments.values_list("class_group_id", flat=True) if participant else []
        )
        return (
            ClassGroup.objects.filter(
                status=ClassGroupStatus.OPEN,
                registration_opens_at__lte=now,
                registration_closes_at__gte=now,
            )
            .exclude(pk__in=enrolled_ids)
            .select_related("workshop", "institution")
            .annotate(
                occupied=Count(
                    "enrollments",
                    filter=Q(enrollments__status=EnrollmentStatus.CONFIRMED),
                ),
                vacancies=F("capacity") - F("occupied"),
            )
            .order_by("start_date", "code")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["participant_profile"] = Participant.objects.filter(
            user=self.request.user, is_active=True
        ).first()
        return context


class ParticipantEnrollmentCreateView(RoleRequiredMixin, View):
    allowed_roles = (UserRole.PARTICIPANT,)

    def post(self, request, class_pk):
        class_group = get_object_or_404(ClassGroup, pk=class_pk)
        participant = Participant.objects.filter(user=request.user).first()
        if not participant:
            messages.error(request, "Seu usuário ainda não possui cadastro de participante.")
            return redirect("enrollments:available-classes")
        try:
            enrollment = create_enrollment(
                participant=participant,
                class_group=class_group,
                actor=request.user,
            )
        except ValidationError as error:
            messages.error(request, _error_messages(error))
        else:
            messages.success(
                request,
                f"Inscrição registrada como {enrollment.get_status_display().lower()}.",
            )
        return redirect("enrollments:list")


class AdminEnrollmentCreateView(AdminRequiredMixin, FormView):
    form_class = AdminEnrollmentCreateForm
    template_name = "enrollments/entity_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.class_group = (
            get_object_or_404(ClassGroup, pk=kwargs["class_pk"]) if kwargs.get("class_pk") else None
        )
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        return super().get_form_kwargs() | {"class_group": self.class_group}

    def form_valid(self, form):
        try:
            enrollment = create_enrollment(
                participant=form.cleaned_data["participant"],
                class_group=form.cleaned_data["class_group"],
                actor=self.request.user,
            )
        except ValidationError as error:
            form.add_error(None, _error_messages(error))
            return self.form_invalid(form)
        messages.success(
            self.request,
            f"Inscrição registrada como {enrollment.get_status_display().lower()}.",
        )
        return redirect("enrollments:class-queue", class_pk=enrollment.class_group_id)

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs) | {
            "page_title": "Registrar inscrição",
            "cancel_url": (
                reverse("enrollments:class-queue", kwargs={"class_pk": self.class_group.pk})
                if self.class_group
                else reverse("enrollments:list")
            ),
        }


class ClassEnrollmentQueueView(RoleRequiredMixin, ListView):
    allowed_roles = (UserRole.ADMIN, UserRole.INSTRUCTOR)
    template_name = "enrollments/class_queue.html"
    context_object_name = "enrollments"

    def dispatch(self, request, *args, **kwargs):
        classes = ClassGroup.objects.select_related("workshop")
        if request.user.role == UserRole.INSTRUCTOR:
            classes = classes.filter(instructor_links__instructor__user=request.user)
        self.class_group = get_object_or_404(classes.distinct(), pk=kwargs["class_pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.class_group.enrollments.select_related("participant", "created_by").order_by(
            "status", "waitlisted_at", "created_at"
        )

    def get_context_data(self, **kwargs):
        queryset = self.class_group.enrollments
        return super().get_context_data(**kwargs) | {
            "class_group": self.class_group,
            "occupied": queryset.filter(status=EnrollmentStatus.CONFIRMED).count(),
            "available": available_places(self.class_group),
            "pending_count": queryset.filter(status=EnrollmentStatus.PENDING).count(),
            "waitlisted_count": queryset.filter(status=EnrollmentStatus.WAITLISTED).count(),
        }


class EnrollmentConfirmView(AdminRequiredMixin, FormView):
    form_class = OptionalReasonForm
    template_name = "enrollments/entity_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.enrollment = get_object_or_404(Enrollment, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        try:
            confirm_enrollment(
                self.enrollment,
                actor=self.request.user,
                reason=form.cleaned_data["reason"],
            )
        except ValidationError as error:
            form.add_error(None, _error_messages(error))
            return self.form_invalid(form)
        messages.success(self.request, "Inscrição confirmada e vaga ocupada.")
        return redirect("enrollments:class-queue", class_pk=self.enrollment.class_group_id)

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs) | {
            "page_title": f"Confirmar inscrição de {self.enrollment.participant}",
            "cancel_url": reverse(
                "enrollments:class-queue",
                kwargs={"class_pk": self.enrollment.class_group_id},
            ),
        }


class EnrollmentRejectView(AdminRequiredMixin, FormView):
    form_class = ReasonForm
    template_name = "enrollments/entity_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.enrollment = get_object_or_404(Enrollment, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        try:
            reject_enrollment(
                self.enrollment,
                actor=self.request.user,
                reason=form.cleaned_data["reason"],
            )
        except ValidationError as error:
            form.add_error(None, _error_messages(error))
            return self.form_invalid(form)
        messages.success(self.request, "Inscrição rejeitada sem apagar o histórico.")
        return redirect("enrollments:class-queue", class_pk=self.enrollment.class_group_id)

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs) | {
            "page_title": f"Rejeitar inscrição de {self.enrollment.participant}",
            "cancel_url": reverse(
                "enrollments:class-queue",
                kwargs={"class_pk": self.enrollment.class_group_id},
            ),
        }


class EnrollmentCancelView(RoleRequiredMixin, FormView):
    allowed_roles = (UserRole.ADMIN, UserRole.PARTICIPANT)
    form_class = CancellationForm
    template_name = "enrollments/entity_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.enrollment = get_object_or_404(Enrollment, pk=kwargs["pk"])
        if (
            request.user.role == UserRole.PARTICIPANT
            and self.enrollment.participant.user_id != request.user.pk
        ):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        return super().get_form_kwargs() | {
            "require_reason": self.request.user.role == UserRole.ADMIN
        }

    def form_valid(self, form):
        try:
            _, promoted = cancel_enrollment(
                self.enrollment,
                actor=self.request.user,
                reason=form.cleaned_data["reason"],
            )
        except ValidationError as error:
            form.add_error(None, _error_messages(error))
            return self.form_invalid(form)
        message = "Inscrição cancelada sem apagar o histórico."
        if promoted:
            message += f" {promoted.participant} foi promovido da lista de espera."
        messages.success(self.request, message)
        if self.request.user.role == UserRole.ADMIN:
            return redirect("enrollments:class-queue", class_pk=self.enrollment.class_group_id)
        return redirect("enrollments:list")

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs) | {
            "page_title": f"Cancelar inscrição de {self.enrollment.participant}",
            "cancel_url": (
                reverse(
                    "enrollments:class-queue",
                    kwargs={"class_pk": self.enrollment.class_group_id},
                )
                if self.request.user.role == UserRole.ADMIN
                else reverse("enrollments:list")
            ),
        }


class PromoteWaitlistView(AdminRequiredMixin, View):
    def post(self, request, class_pk):
        class_group = get_object_or_404(ClassGroup, pk=class_pk)
        try:
            promoted = promote_next_waitlisted(class_group, actor=request.user)
        except ValidationError as error:
            messages.error(request, _error_messages(error))
        else:
            if promoted:
                messages.success(request, f"{promoted.participant} foi promovido e confirmado.")
            else:
                messages.info(request, "Nenhuma inscrição elegível pôde ser promovida.")
        return redirect("enrollments:class-queue", class_pk=class_pk)
