from datetime import datetime

import pytest
from django.urls import reverse
from django.utils import timezone

from apps.people.models import Instructor
from apps.workshops.models import ClassGroupStatus, ClassInstructor, Meeting, Workshop

pytestmark = pytest.mark.django_db


def test_workshop_list_requires_authentication(client):
    response = client.get(reverse("workshops:workshop-list"))

    assert response.status_code == 302
    assert response.url.startswith(reverse("login"))


def test_participant_cannot_manage_workshops(client, participant_user):
    client.force_login(participant_user)

    assert client.get(reverse("workshops:workshop-list")).status_code == 403
    assert client.get(reverse("workshops:class-list")).status_code == 403


def test_administrator_creates_workshop_as_draft(client, admin_user):
    client.force_login(admin_user)

    response = client.post(
        reverse("workshops:workshop-create"),
        {
            "title": "Criação de sites",
            "slug": "criacao-sites",
            "summary": "Primeiros passos na web.",
            "objective": "Publicar uma página pessoal.",
            "syllabus": "HTML, CSS e JavaScript.",
            "estimated_hours": "12.00",
        },
    )

    workshop = Workshop.objects.get(slug="criacao-sites")
    assert response.status_code == 302
    assert workshop.created_by == admin_user


def test_administrator_publishes_workshop(client, admin_user):
    workshop = Workshop.objects.create(
        title="Oficina",
        slug="oficina",
        summary="Resumo",
        objective="Objetivo",
        syllabus="Conteúdo",
        estimated_hours=8,
        created_by=admin_user,
    )
    client.force_login(admin_user)

    response = client.post(
        reverse("workshops:workshop-transition", kwargs={"pk": workshop.pk, "target": "published"})
    )
    workshop.refresh_from_db()

    assert response.status_code == 302
    assert workshop.status == "PUBLISHED"


def test_administrator_creates_class(client, admin_user, published_workshop):
    client.force_login(admin_user)

    response = client.post(
        reverse("workshops:class-create"),
        {
            "workshop": published_workshop.pk,
            "code": "CDF-WEB-01",
            "title": "Turma Web",
            "location": "Biblioteca",
            "capacity": 18,
            "waitlist_enabled": True,
            "registration_opens_at": "2026-09-15T08:00",
            "registration_closes_at": "2026-09-30T18:00",
            "start_date": "2026-10-01",
            "end_date": "2026-11-30",
        },
    )

    assert response.status_code == 302
    assert published_workshop.class_groups.filter(code="CDF-WEB-01").exists()


def test_opening_without_instructor_shows_error(client, admin_user, planned_class):
    client.force_login(admin_user)

    response = client.post(
        reverse(
            "workshops:class-transition",
            kwargs={"pk": planned_class.pk, "target": "open"},
        ),
        follow=True,
    )
    planned_class.refresh_from_db()

    assert planned_class.status == ClassGroupStatus.PLANNED
    assert "instrutor ativo" in response.content.decode()


def test_administrator_links_instructor(client, admin_user, instructor_user, planned_class):
    instructor = Instructor.objects.create(user=instructor_user)
    client.force_login(admin_user)

    response = client.post(
        reverse("workshops:class-instructor-create", kwargs={"class_pk": planned_class.pk}),
        {"instructor": instructor.pk, "is_lead": True},
    )

    assert response.status_code == 302
    assert ClassInstructor.objects.filter(class_group=planned_class, instructor=instructor).exists()


def test_administrator_creates_meeting(client, admin_user, planned_class):
    client.force_login(admin_user)

    response = client.post(
        reverse("workshops:meeting-create", kwargs={"class_pk": planned_class.pk}),
        {
            "title": "Primeiro encontro",
            "description": "Lógica",
            "starts_at": "2026-10-10T09:00",
            "ends_at": "2026-10-10T11:00",
        },
    )

    assert response.status_code == 302
    assert planned_class.meetings.filter(title="Primeiro encontro").exists()


def test_instructor_sees_only_assigned_classes(
    client, admin_user, instructor_user, planned_class, published_workshop
):
    instructor = Instructor.objects.create(user=instructor_user)
    ClassInstructor.objects.create(class_group=planned_class, instructor=instructor)
    hidden = planned_class.__class__.objects.create(
        workshop=published_workshop,
        code="CDF-OCULTA",
        title="Turma de outro instrutor",
        location="Outro local",
        capacity=10,
        registration_opens_at=timezone.make_aware(datetime(2026, 9, 15, 8)),
        registration_closes_at=timezone.make_aware(datetime(2026, 9, 30, 18)),
        start_date=planned_class.start_date,
        end_date=planned_class.end_date,
        created_by=admin_user,
    )
    client.force_login(instructor_user)

    response = client.get(reverse("workshops:class-list"))
    content = response.content.decode()

    assert response.status_code == 200
    assert planned_class.title in content
    assert hidden.title not in content
    assert (
        client.get(reverse("workshops:class-detail", kwargs={"pk": hidden.pk})).status_code == 404
    )


def test_instructor_cannot_create_class(client, instructor_user):
    client.force_login(instructor_user)

    assert client.get(reverse("workshops:class-create")).status_code == 403


def test_administrator_cancels_meeting(client, admin_user, planned_class):
    meeting = Meeting.objects.create(
        class_group=planned_class,
        title="Encontro",
        starts_at=timezone.make_aware(datetime(2026, 10, 10, 9)),
        ends_at=timezone.make_aware(datetime(2026, 10, 10, 11)),
    )
    client.force_login(admin_user)

    response = client.post(reverse("workshops:meeting-cancel", kwargs={"pk": meeting.pk}))
    meeting.refresh_from_db()

    assert response.status_code == 302
    assert meeting.status == "CANCELLED"


def test_cancelled_class_rejects_new_meeting(client, admin_user, planned_class):
    planned_class.status = ClassGroupStatus.CANCELLED
    planned_class.save()
    client.force_login(admin_user)

    response = client.get(
        reverse("workshops:meeting-create", kwargs={"class_pk": planned_class.pk})
    )

    assert response.status_code == 403


def test_open_class_rejects_new_instructor(client, admin_user, planned_class):
    planned_class.status = ClassGroupStatus.OPEN
    planned_class.save()
    client.force_login(admin_user)

    response = client.get(
        reverse("workshops:class-instructor-create", kwargs={"class_pk": planned_class.pk})
    )

    assert response.status_code == 403
