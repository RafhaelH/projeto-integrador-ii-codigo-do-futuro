from datetime import date

import pytest
from django.urls import reverse

from apps.people.models import Guardian, Institution, Instructor, Participant, ParticipantGuardian

pytestmark = pytest.mark.django_db


def test_people_index_redirects_anonymous_user(client):
    response = client.get(reverse("people:index"))

    assert response.status_code == 302
    assert response.url.startswith(reverse("login"))


def test_people_index_denies_participant(client, participant_user):
    client.force_login(participant_user)

    response = client.get(reverse("people:index"))

    assert response.status_code == 403


def test_people_index_allows_administrator(client, admin_user):
    client.force_login(admin_user)

    response = client.get(reverse("people:index"))

    assert response.status_code == 200
    assert "Pessoas e instituições" in response.content.decode()


def test_administrator_creates_participant(client, admin_user):
    client.force_login(admin_user)

    response = client.post(
        reverse("people:participant-create"),
        {
            "full_name": "Novo Participante",
            "birth_date": "2008-01-10",
            "cpf": "529.982.247-25",
            "contact_email": "novo@example.com",
            "phone": "(16) 99999-1234",
            "is_active": True,
        },
    )

    participant = Participant.objects.get(full_name="Novo Participante")
    assert response.status_code == 302
    assert response.url == reverse("people:participant-detail", kwargs={"pk": participant.pk})
    assert participant.cpf == "52998224725"


def test_participant_list_masks_cpf(client, admin_user):
    Participant.objects.create(
        full_name="Participante Protegido",
        birth_date=date(2008, 1, 10),
        cpf="52998224725",
    )
    client.force_login(admin_user)

    response = client.get(reverse("people:participant-list"))
    content = response.content.decode()

    assert response.status_code == 200
    assert "***.982.247-**" in content
    assert "529.982.247-25" not in content


def test_administrator_links_guardian_to_participant(client, admin_user):
    participant = Participant.objects.create(
        full_name="Participante Menor",
        birth_date=date(2010, 1, 1),
    )
    guardian = Guardian.objects.create(full_name="Responsável Exemplo", phone="16999991234")
    client.force_login(admin_user)

    response = client.post(
        reverse("people:guardian-link-create", kwargs={"participant_pk": participant.pk}),
        {"guardian": guardian.pk, "relationship": "MOTHER", "is_primary": True},
    )

    assert response.status_code == 302
    assert ParticipantGuardian.objects.filter(
        participant=participant,
        guardian=guardian,
        is_primary=True,
    ).exists()


def test_administrator_creates_guardian(client, admin_user):
    client.force_login(admin_user)

    response = client.post(
        reverse("people:guardian-create"),
        {
            "full_name": "Novo Responsável",
            "phone": "(16) 99999-4321",
            "email": "responsavel@example.com",
            "is_active": True,
        },
    )

    guardian = Guardian.objects.get(full_name="Novo Responsável")
    assert response.status_code == 302
    assert guardian.phone == "16999994321"


def test_administrator_creates_instructor(client, admin_user, instructor_user):
    client.force_login(admin_user)

    response = client.post(
        reverse("people:instructor-create"),
        {
            "user": instructor_user.pk,
            "biography": "Instrutor de introdução à programação.",
            "specialties": "Python, lógica",
            "is_active": True,
        },
    )

    assert response.status_code == 302
    assert Instructor.objects.filter(user=instructor_user, is_active=True).exists()


def test_administrator_creates_institution(client, admin_user):
    client.force_login(admin_user)

    response = client.post(
        reverse("people:institution-create"),
        {
            "name": "Biblioteca Municipal",
            "document": "11.222.333/0001-81",
            "contact_name": "Contato Exemplo",
            "contact_email": "contato@example.com",
            "contact_phone": "(16) 3600-1234",
            "address": "Endereço fictício",
            "is_active": True,
        },
    )

    institution = Institution.objects.get(name="Biblioteca Municipal")
    assert response.status_code == 302
    assert institution.document == "11222333000181"
    assert institution.contact_phone == "1636001234"
