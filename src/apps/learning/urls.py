from django.urls import path

from .views import (
    CertificateDetailView,
    CertificateDownloadView,
    CertificateListView,
    ClassAttendanceView,
    CompleteClassGroupView,
    EvaluationView,
    IssueCertificateView,
    MeetingAttendanceView,
    ParticipantFrequencyView,
    ParticipantProjectView,
    ProjectReviewView,
    RevokeCertificateView,
)

app_name = "learning"

urlpatterns = [
    path("certificados/", CertificateListView.as_view(), name="certificate-list"),
    path(
        "certificados/<uuid:pk>/",
        CertificateDetailView.as_view(),
        name="certificate-detail",
    ),
    path(
        "certificados/<uuid:pk>/baixar/",
        CertificateDownloadView.as_view(),
        name="certificate-download",
    ),
    path(
        "certificados/<uuid:pk>/revogar/",
        RevokeCertificateView.as_view(),
        name="certificate-revoke",
    ),
    path(
        "inscricoes/<uuid:enrollment_pk>/certificado/emitir/",
        IssueCertificateView.as_view(),
        name="certificate-issue",
    ),
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
