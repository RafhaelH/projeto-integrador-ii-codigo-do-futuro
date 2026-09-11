from django.urls import path

from .views import (
    GuardianCreateView,
    GuardianLinkCreateView,
    GuardianListView,
    GuardianUpdateView,
    InstitutionCreateView,
    InstitutionListView,
    InstitutionUpdateView,
    InstructorCreateView,
    InstructorListView,
    InstructorUpdateView,
    ParticipantCreateView,
    ParticipantDetailView,
    ParticipantListView,
    ParticipantUpdateView,
    PeopleIndexView,
)

app_name = "people"

urlpatterns = [
    path("", PeopleIndexView.as_view(), name="index"),
    path("participantes/", ParticipantListView.as_view(), name="participant-list"),
    path("participantes/novo/", ParticipantCreateView.as_view(), name="participant-create"),
    path("participantes/<uuid:pk>/", ParticipantDetailView.as_view(), name="participant-detail"),
    path(
        "participantes/<uuid:pk>/editar/",
        ParticipantUpdateView.as_view(),
        name="participant-update",
    ),
    path(
        "participantes/<uuid:participant_pk>/responsaveis/vincular/",
        GuardianLinkCreateView.as_view(),
        name="guardian-link-create",
    ),
    path("responsaveis/", GuardianListView.as_view(), name="guardian-list"),
    path("responsaveis/novo/", GuardianCreateView.as_view(), name="guardian-create"),
    path(
        "responsaveis/<uuid:pk>/editar/",
        GuardianUpdateView.as_view(),
        name="guardian-update",
    ),
    path("instrutores/", InstructorListView.as_view(), name="instructor-list"),
    path("instrutores/novo/", InstructorCreateView.as_view(), name="instructor-create"),
    path(
        "instrutores/<uuid:pk>/editar/",
        InstructorUpdateView.as_view(),
        name="instructor-update",
    ),
    path("instituicoes/", InstitutionListView.as_view(), name="institution-list"),
    path("instituicoes/nova/", InstitutionCreateView.as_view(), name="institution-create"),
    path(
        "instituicoes/<uuid:pk>/editar/",
        InstitutionUpdateView.as_view(),
        name="institution-update",
    ),
]
