from django.urls import path

from .views import (
    ClassAttendanceView,
    CompleteClassGroupView,
    EvaluationView,
    MeetingAttendanceView,
    ParticipantFrequencyView,
    ParticipantProjectView,
    ProjectReviewView,
)

app_name = "learning"

urlpatterns = [
    path("frequencia/", ParticipantFrequencyView.as_view(), name="participant-frequency"),
    path(
        "turmas/<uuid:class_pk>/frequencia/",
        ClassAttendanceView.as_view(),
        name="class-attendance",
    ),
    path(
        "encontros/<uuid:meeting_pk>/chamada/",
        MeetingAttendanceView.as_view(),
        name="meeting-attendance",
    ),
    path(
        "inscricoes/<uuid:enrollment_pk>/projeto/",
        ParticipantProjectView.as_view(),
        name="participant-project",
    ),
    path("projetos/<uuid:pk>/revisao/", ProjectReviewView.as_view(), name="project-review"),
    path(
        "inscricoes/<uuid:enrollment_pk>/avaliacao/",
        EvaluationView.as_view(),
        name="evaluation",
    ),
    path(
        "turmas/<uuid:class_pk>/conclusao/",
        CompleteClassGroupView.as_view(),
        name="complete-class",
    ),
]
