from django.urls import path

from .views import (
    AdminEnrollmentCreateView,
    AvailableClassListView,
    ClassEnrollmentQueueView,
    EnrollmentCancelView,
    EnrollmentConfirmView,
    EnrollmentListView,
    EnrollmentRejectView,
    ParticipantEnrollmentCreateView,
    PromoteWaitlistView,
)

app_name = "enrollments"

urlpatterns = [
    path("", EnrollmentListView.as_view(), name="list"),
    path("turmas-disponiveis/", AvailableClassListView.as_view(), name="available-classes"),
    path("nova/", AdminEnrollmentCreateView.as_view(), name="admin-create"),
    path(
        "turmas/<uuid:class_pk>/nova/",
        AdminEnrollmentCreateView.as_view(),
        name="class-create",
    ),
    path(
        "turmas/<uuid:class_pk>/solicitar/",
        ParticipantEnrollmentCreateView.as_view(),
        name="participant-create",
    ),
    path(
        "turmas/<uuid:class_pk>/fila/",
        ClassEnrollmentQueueView.as_view(),
        name="class-queue",
    ),
    path(
        "turmas/<uuid:class_pk>/promover/",
        PromoteWaitlistView.as_view(),
        name="promote-waitlist",
    ),
    path("<uuid:pk>/confirmar/", EnrollmentConfirmView.as_view(), name="confirm"),
    path("<uuid:pk>/rejeitar/", EnrollmentRejectView.as_view(), name="reject"),
    path("<uuid:pk>/cancelar/", EnrollmentCancelView.as_view(), name="cancel"),
]
