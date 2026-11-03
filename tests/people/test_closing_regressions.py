from datetime import date, datetime

import pytest
from django.db import IntegrityError
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import User, UserRole
from apps.people.forms import InstructorForm, ParticipantForm
from apps.people.models import Instructor, Participant

pytestmark = pytest.mark.django_db


@pytest.fixture
def saved_participant():
    return Participant.objects.create(
        full_name="Pessoa fictícia para regressão",
        birth_date=date(2007, 2, 15),
        cpf="52998224725",
        phone="16999991234",
        contact_email="pessoa.ficticia@example.com",
        privacy_consent_at=timezone.make_aware(datetime(2026, 10, 1, 9, 32, 17, 123456)),
    )


def participant_data(participant):
    form = ParticipantForm(instance=participant)
    return {
        name: form[name].value() if form[name].value() is not None else "" for name in form.fields
    }


def test_saved_values_render_and_editing_other_field_preserves_them(
    client, admin_user, saved_participant
):
    admin_user.is_staff = False
    admin_user.save()
    client.force_login(admin_user)
    url = reverse("people:participant-update", kwargs={"pk": saved_participant.pk})
    response = client.get(url)
    body = response.content.decode()
    assert 'value="2007-02-15"' in body
    assert 'value="529.982.247-25"' in body
    assert 'value="(16) 99999-1234"' in body
    original_consent = saved_participant.privacy_consent_at
    data = participant_data(saved_participant)
    data["full_name"] = "Nome fictício atualizado"
    data["privacy_consent_at"] = "2026-10-01T09:32:17.123456"
    assert client.post(url, data).status_code == 302
    saved_participant.refresh_from_db()
    assert saved_participant.full_name == data["full_name"]
    assert saved_participant.birth_date == date(2007, 2, 15)
    assert saved_participant.cpf == "52998224725"
    assert saved_participant.phone == "16999991234"
    assert saved_participant.privacy_consent_at == original_consent


@pytest.mark.parametrize(
    ("field", "invalid"), [("full_name", ""), ("cpf", "111.111.111-11"), ("phone", "123")]
)
def test_invalid_submission_preserves_entered_values_and_database(
    client, admin_user, saved_participant, field, invalid
):
    client.force_login(admin_user)
    data = participant_data(saved_participant)
    data["birth_date"] = "2007-02-15"
    data["privacy_consent_at"] = "2026-10-01T09:32:17.123456"
    data[field] = invalid
    response = client.post(
        reverse("people:participant-update", kwargs={"pk": saved_participant.pk}), data
    )
    assert response.status_code == 200
    assert field in response.context["form"].errors
    for name in ["cpf", "phone", "birth_date"]:
        assert response.context["form"][name].value() == data[name]
    saved_participant.refresh_from_db()
    assert saved_participant.cpf == "52998224725" and saved_participant.phone == "16999991234"


def test_optional_consent_is_not_collected_automatically():
    form = ParticipantForm(
        data={
            "full_name": "Sem consentimento fictício",
            "birth_date": "2007-02-15",
            "is_active": True,
        }
    )
    assert form.is_valid(), form.errors
    person = form.save()
    assert person.privacy_consent_at is None and person.image_authorization is False


def test_minor_registration_is_allowed_and_explains_enrollment_guardian_rule(client, admin_user):
    client.force_login(admin_user)
    person = Participant.objects.create(
        full_name="Menor fictício", birth_date=date(timezone.localdate().year - 16, 1, 1)
    )
    response = client.get(reverse("people:participant-detail", kwargs={"pk": person.pk}))
    assert response.status_code == 200
    assert "A inscrição será bloqueada" in response.content.decode()


def test_empty_instructor_selector_has_safe_provisioning_path(client, admin_user, instructor_user):
    admin_user.is_staff = False
    admin_user.save()
    Instructor.objects.create(user=instructor_user)
    assert not InstructorForm().fields["user"].queryset.exists()
    client.force_login(admin_user)
    response = client.get(reverse("people:instructor-create"))
    assert reverse("people:instructor-access-create") in response.content.decode()


def test_instructor_selector_only_exposes_eligible_users(
    admin_user, instructor_user, participant_user
):
    eligible = User.objects.create_user(
        email="elegivel@example.com", full_name="Instrutor elegível", role=UserRole.INSTRUCTOR
    )
    User.objects.create_user(
        email="inativo@example.com",
        full_name="Instrutor inativo",
        role=UserRole.INSTRUCTOR,
        is_active=False,
    )
    Instructor.objects.create(user=instructor_user)
    form = InstructorForm()
    assert set(form.fields["user"].queryset.values_list("pk", flat=True)) == {eligible.pk}
    forged = InstructorForm(data={"user": admin_user.pk, "is_active": True})
    assert not forged.is_valid() and "user" in forged.errors


def provisioning_data():
    return {
        "email": "novo.instrutor@example.com",
        "full_name": "Instrutor fictício novo",
        "password1": "Senha-isolada!2026#Forte",
        "password2": "Senha-isolada!2026#Forte",
        "biography": "Fictícia",
        "specialties": "Python",
        "role": "ADMIN",
        "is_staff": "1",
        "is_superuser": "1",
        "groups": "1",
        "user_permissions": "1",
    }


def test_functional_admin_provisions_only_instructor_without_extra_privileges(client, admin_user):
    admin_user.is_staff = False
    admin_user.save()
    client.force_login(admin_user)
    data = provisioning_data()
    response = client.post(reverse("people:instructor-access-create"), data)
    assert response.status_code == 302
    user = User.objects.get(email=data["email"])
    assert user.role == UserRole.INSTRUCTOR and user.is_active
    assert not user.is_staff and not user.is_superuser
    assert not user.groups.exists() and not user.user_permissions.exists()
    assert user.check_password(data["password1"]) and user.password != data["password1"]
    assert Instructor.objects.get(user=user).specialties == "Python"
    admin_user.refresh_from_db()
    assert not admin_user.is_staff


@pytest.mark.parametrize("user_fixture", ["instructor_user", "participant_user"])
def test_non_admin_cannot_provision(client, request, user_fixture):
    client.force_login(request.getfixturevalue(user_fixture))
    url = reverse("people:instructor-access-create")
    assert client.get(url).status_code == 403
    assert client.post(url, provisioning_data()).status_code == 403
    assert not User.objects.filter(email="novo.instrutor@example.com").exists()


def test_provisioning_requires_csrf_and_rejects_weak_and_duplicate_passwords(client, admin_user):
    secure = Client(enforce_csrf_checks=True)
    secure.force_login(admin_user)
    url = reverse("people:instructor-access-create")
    assert secure.post(url, provisioning_data()).status_code == 403
    client.force_login(admin_user)
    data = provisioning_data()
    data["password1"] = data["password2"] = "123"
    assert client.post(url, data).status_code == 200
    assert not User.objects.filter(email=data["email"]).exists()
    data = provisioning_data()
    data["email"] = admin_user.email.upper()
    assert client.post(url, data).status_code == 200
    assert User.objects.filter(email__iexact=admin_user.email).count() == 1


def test_provisioning_failure_rolls_back_new_user(client, admin_user, monkeypatch):
    client.force_login(admin_user)

    def fail(**kwargs):
        raise IntegrityError("simulated profile failure")

    monkeypatch.setattr(Instructor.objects, "create", fail)
    assert (
        client.post(reverse("people:instructor-access-create"), provisioning_data()).status_code
        == 200
    )
    assert not User.objects.filter(email="novo.instrutor@example.com").exists()
