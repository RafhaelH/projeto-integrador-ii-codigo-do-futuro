from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, TemplateView, UpdateView

from apps.accounts.mixins import AdminRequiredMixin

from .forms import (
    GuardianForm,
    InstitutionForm,
    InstructorForm,
    ParticipantForm,
    ParticipantGuardianForm,
)
from .models import Guardian, Institution, Instructor, Participant, ParticipantGuardian


class PeopleIndexView(AdminRequiredMixin, TemplateView):
    template_name = "people/index.html"


class ParticipantListView(AdminRequiredMixin, ListView):
    model = Participant
    template_name = "people/participant_list.html"
    context_object_name = "participants"
    paginate_by = 25

    def get_queryset(self):
        queryset = super().get_queryset().select_related("user")
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(full_name__icontains=query)
        return queryset


class ParticipantDetailView(AdminRequiredMixin, DetailView):
    model = Participant
    template_name = "people/participant_detail.html"
    context_object_name = "participant"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("user")
            .prefetch_related("guardian_links__guardian")
        )


class ParticipantCreateView(AdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = Participant
    form_class = ParticipantForm
    template_name = "people/entity_form.html"
    success_message = "Participante cadastrado com sucesso."

    def get_success_url(self):
        return reverse("people:participant-detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            page_title="Novo participante",
            cancel_url=reverse("people:participant-list"),
        )


class ParticipantUpdateView(AdminRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Participant
    form_class = ParticipantForm
    template_name = "people/entity_form.html"
    success_message = "Participante atualizado com sucesso."

    def get_success_url(self):
        return reverse("people:participant-detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            page_title="Editar participante",
            cancel_url=reverse("people:participant-detail", kwargs={"pk": self.object.pk}),
        )


class GuardianLinkCreateView(AdminRequiredMixin, CreateView):
    model = ParticipantGuardian
    form_class = ParticipantGuardianForm
    template_name = "people/entity_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.participant = get_object_or_404(Participant, pk=kwargs["participant_pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        return super().get_form_kwargs() | {"participant": self.participant}

    def form_valid(self, form):
        form.instance.participant = self.participant
        messages.success(self.request, "Responsável vinculado com sucesso.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("people:participant-detail", kwargs={"pk": self.participant.pk})

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            page_title=f"Vincular responsável a {self.participant.full_name}",
            cancel_url=reverse("people:participant-detail", kwargs={"pk": self.participant.pk}),
        )


class GuardianListView(AdminRequiredMixin, ListView):
    model = Guardian
    template_name = "people/guardian_list.html"
    context_object_name = "guardians"
    paginate_by = 25

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get("q", "").strip()
        return queryset.filter(full_name__icontains=query) if query else queryset


class GuardianCreateView(AdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = Guardian
    form_class = GuardianForm
    template_name = "people/entity_form.html"
    success_url = reverse_lazy("people:guardian-list")
    success_message = "Responsável cadastrado com sucesso."

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            page_title="Novo responsável",
            cancel_url=reverse("people:guardian-list"),
        )


class GuardianUpdateView(AdminRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Guardian
    form_class = GuardianForm
    template_name = "people/entity_form.html"
    success_url = reverse_lazy("people:guardian-list")
    success_message = "Responsável atualizado com sucesso."

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            page_title="Editar responsável",
            cancel_url=reverse("people:guardian-list"),
        )


class InstructorListView(AdminRequiredMixin, ListView):
    model = Instructor
    template_name = "people/instructor_list.html"
    context_object_name = "instructors"
    paginate_by = 25

    def get_queryset(self):
        queryset = super().get_queryset().select_related("user")
        query = self.request.GET.get("q", "").strip()
        return queryset.filter(user__full_name__icontains=query) if query else queryset


class InstructorCreateView(AdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = Instructor
    form_class = InstructorForm
    template_name = "people/entity_form.html"
    success_url = reverse_lazy("people:instructor-list")
    success_message = "Instrutor cadastrado com sucesso."

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            page_title="Novo instrutor",
            cancel_url=reverse("people:instructor-list"),
        )


class InstructorUpdateView(AdminRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Instructor
    form_class = InstructorForm
    template_name = "people/entity_form.html"
    success_url = reverse_lazy("people:instructor-list")
    success_message = "Instrutor atualizado com sucesso."

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            page_title="Editar instrutor",
            cancel_url=reverse("people:instructor-list"),
        )


class InstitutionListView(AdminRequiredMixin, ListView):
    model = Institution
    template_name = "people/institution_list.html"
    context_object_name = "institutions"
    paginate_by = 25

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get("q", "").strip()
        return queryset.filter(name__icontains=query) if query else queryset


class InstitutionCreateView(AdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = Institution
    form_class = InstitutionForm
    template_name = "people/entity_form.html"
    success_url = reverse_lazy("people:institution-list")
    success_message = "Instituição cadastrada com sucesso."

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            page_title="Nova instituição",
            cancel_url=reverse("people:institution-list"),
        )


class InstitutionUpdateView(AdminRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Institution
    form_class = InstitutionForm
    template_name = "people/entity_form.html"
    success_url = reverse_lazy("people:institution-list")
    success_message = "Instituição atualizada com sucesso."

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            page_title="Editar instituição",
            cancel_url=reverse("people:institution-list"),
        )
