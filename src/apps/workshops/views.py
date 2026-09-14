from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from apps.accounts.mixins import AdminRequiredMixin, RoleRequiredMixin
from apps.accounts.models import UserRole

from .forms import ClassGroupForm, ClassInstructorForm, MeetingForm, WorkshopForm
from .models import (
    ClassGroup,
    ClassGroupStatus,
    ClassInstructor,
    Meeting,
    MeetingStatus,
    Workshop,
)
from .services import cancel_meeting, transition_class_group, transition_workshop


class WorkshopListView(AdminRequiredMixin, ListView):
    model = Workshop
    template_name = "workshops/workshop_list.html"
    context_object_name = "workshops"
    paginate_by = 25

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get("q", "").strip()
        return queryset.filter(title__icontains=query) if query else queryset


class WorkshopCreateView(AdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = Workshop
    form_class = WorkshopForm
    template_name = "workshops/entity_form.html"
    success_message = "Oficina cadastrada como rascunho."

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("workshops:workshop-detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs, page_title="Nova oficina", cancel_url=reverse("workshops:workshop-list")
        )


class WorkshopDetailView(AdminRequiredMixin, DetailView):
    model = Workshop
    template_name = "workshops/workshop_detail.html"
    context_object_name = "workshop"

    def get_queryset(self):
        return super().get_queryset().prefetch_related("class_groups")


class WorkshopUpdateView(AdminRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Workshop
    form_class = WorkshopForm
    template_name = "workshops/entity_form.html"
    success_message = "Oficina atualizada com sucesso."

    def get_success_url(self):
        return reverse("workshops:workshop-detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            page_title="Editar oficina",
            cancel_url=reverse("workshops:workshop-detail", kwargs={"pk": self.object.pk}),
        )


class WorkshopTransitionView(AdminRequiredMixin, View):
    def post(self, request, pk, target):
        workshop = get_object_or_404(Workshop, pk=pk)
        try:
            updated = transition_workshop(workshop, target.upper())
        except ValidationError as error:
            messages.error(request, "; ".join(error.messages))
        else:
            messages.success(request, f"Oficina alterada para {updated.get_status_display()}.")
        return redirect("workshops:workshop-detail", pk=pk)


class ClassAccessMixin(RoleRequiredMixin):
    allowed_roles = (UserRole.ADMIN, UserRole.INSTRUCTOR)

    def get_queryset(self):
        queryset = ClassGroup.objects.select_related("workshop", "institution")
        if self.request.user.role == UserRole.INSTRUCTOR:
            queryset = queryset.filter(instructor_links__instructor__user=self.request.user)
        return queryset.distinct()


class ClassGroupListView(ClassAccessMixin, ListView):
    template_name = "workshops/class_list.html"
    context_object_name = "class_groups"
    paginate_by = 25

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get("q", "").strip()
        return queryset.filter(title__icontains=query) if query else queryset


class ClassGroupDetailView(ClassAccessMixin, DetailView):
    template_name = "workshops/class_detail.html"
    context_object_name = "class_group"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related("instructor_links__instructor__user", "meetings")
        )


class ClassGroupCreateView(AdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = ClassGroup
    form_class = ClassGroupForm
    template_name = "workshops/entity_form.html"
    success_message = "Turma cadastrada como planejada."

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("workshops:class-detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs, page_title="Nova turma", cancel_url=reverse("workshops:class-list")
        )


class ClassGroupUpdateView(AdminRequiredMixin, SuccessMessageMixin, UpdateView):
    model = ClassGroup
    form_class = ClassGroupForm
    template_name = "workshops/entity_form.html"
    success_message = "Turma atualizada com sucesso."

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().status != ClassGroupStatus.PLANNED:
            raise PermissionDenied("Somente turmas planejadas podem ser editadas.")
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("workshops:class-detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            page_title="Editar turma",
            cancel_url=reverse("workshops:class-detail", kwargs={"pk": self.object.pk}),
        )


class ClassGroupTransitionView(AdminRequiredMixin, View):
    def post(self, request, pk, target):
        class_group = get_object_or_404(ClassGroup, pk=pk)
        try:
            updated = transition_class_group(class_group, target.upper())
        except ValidationError as error:
            messages.error(request, "; ".join(error.messages))
        else:
            messages.success(request, f"Turma alterada para {updated.get_status_display()}.")
        return redirect("workshops:class-detail", pk=pk)


class ClassInstructorCreateView(AdminRequiredMixin, CreateView):
    model = ClassInstructor
    form_class = ClassInstructorForm
    template_name = "workshops/entity_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.class_group = get_object_or_404(ClassGroup, pk=kwargs["class_pk"])
        if self.class_group.status != ClassGroupStatus.PLANNED:
            raise PermissionDenied("Instrutores só podem ser vinculados a turmas planejadas.")
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        return super().get_form_kwargs() | {"class_group": self.class_group}

    def form_valid(self, form):
        form.instance.class_group = self.class_group
        messages.success(self.request, "Instrutor vinculado com sucesso.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("workshops:class-detail", kwargs={"pk": self.class_group.pk})

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            page_title=f"Vincular instrutor a {self.class_group.code}",
            cancel_url=self.get_success_url(),
        )


class MeetingCreateView(AdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = Meeting
    form_class = MeetingForm
    template_name = "workshops/entity_form.html"
    success_message = "Encontro adicionado ao cronograma."

    def dispatch(self, request, *args, **kwargs):
        self.class_group = get_object_or_404(ClassGroup, pk=kwargs["class_pk"])
        if self.class_group.status in {
            ClassGroupStatus.COMPLETED,
            ClassGroupStatus.CANCELLED,
        }:
            raise PermissionDenied("A agenda de uma turma encerrada não pode ser ampliada.")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.class_group = self.class_group
        return super().form_valid(form)

    def get_form_kwargs(self):
        return super().get_form_kwargs() | {"class_group": self.class_group}

    def get_success_url(self):
        return reverse("workshops:class-detail", kwargs={"pk": self.class_group.pk})

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            page_title=f"Novo encontro de {self.class_group.code}",
            cancel_url=self.get_success_url(),
        )


class MeetingUpdateView(AdminRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Meeting
    form_class = MeetingForm
    template_name = "workshops/entity_form.html"
    success_message = "Encontro atualizado com sucesso."

    def dispatch(self, request, *args, **kwargs):
        meeting = self.get_object()
        if meeting.status != MeetingStatus.PLANNED or meeting.class_group.status in {
            ClassGroupStatus.COMPLETED,
            ClassGroupStatus.CANCELLED,
        }:
            raise PermissionDenied("Somente encontros planejados podem ser editados.")
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("workshops:class-detail", kwargs={"pk": self.object.class_group_id})

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs, page_title="Editar encontro", cancel_url=self.get_success_url()
        )


class MeetingCancelView(AdminRequiredMixin, View):
    def post(self, request, pk):
        meeting = get_object_or_404(Meeting, pk=pk)
        try:
            cancel_meeting(meeting)
        except ValidationError as error:
            messages.error(request, "; ".join(error.messages))
        else:
            messages.success(request, "Encontro cancelado sem apagar seu histórico.")
        return redirect("workshops:class-detail", pk=meeting.class_group_id)
