from django.urls import path

from .views import ClassAttendanceView, MeetingAttendanceView, ParticipantFrequencyView

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
]
