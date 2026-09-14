from django.urls import path

from .views import (
    ClassGroupCreateView,
    ClassGroupDetailView,
    ClassGroupListView,
    ClassGroupTransitionView,
    ClassGroupUpdateView,
    ClassInstructorCreateView,
    MeetingCancelView,
    MeetingCreateView,
    MeetingUpdateView,
    WorkshopCreateView,
    WorkshopDetailView,
    WorkshopListView,
    WorkshopTransitionView,
    WorkshopUpdateView,
)

app_name = "workshops"

urlpatterns = [
    path("", WorkshopListView.as_view(), name="workshop-list"),
    path("nova/", WorkshopCreateView.as_view(), name="workshop-create"),
    path("<uuid:pk>/", WorkshopDetailView.as_view(), name="workshop-detail"),
    path("<uuid:pk>/editar/", WorkshopUpdateView.as_view(), name="workshop-update"),
    path(
        "<uuid:pk>/situacao/<str:target>/",
        WorkshopTransitionView.as_view(),
        name="workshop-transition",
    ),
    path("turmas/", ClassGroupListView.as_view(), name="class-list"),
    path("turmas/nova/", ClassGroupCreateView.as_view(), name="class-create"),
    path("turmas/<uuid:pk>/", ClassGroupDetailView.as_view(), name="class-detail"),
    path("turmas/<uuid:pk>/editar/", ClassGroupUpdateView.as_view(), name="class-update"),
    path(
        "turmas/<uuid:pk>/situacao/<str:target>/",
        ClassGroupTransitionView.as_view(),
        name="class-transition",
    ),
    path(
        "turmas/<uuid:class_pk>/instrutores/vincular/",
        ClassInstructorCreateView.as_view(),
        name="class-instructor-create",
    ),
    path(
        "turmas/<uuid:class_pk>/encontros/novo/",
        MeetingCreateView.as_view(),
        name="meeting-create",
    ),
    path("encontros/<uuid:pk>/editar/", MeetingUpdateView.as_view(), name="meeting-update"),
    path("encontros/<uuid:pk>/cancelar/", MeetingCancelView.as_view(), name="meeting-cancel"),
]
