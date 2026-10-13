from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import pytest
from django.contrib import admin
from django.db import IntegrityError, connections
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import User
from apps.workshops.forms import MeetingForm
from apps.workshops.models import ClassGroup, ClassGroupStatus, Meeting

pytestmark = pytest.mark.django_db


@pytest.fixture
def meeting_data():
    return {
        "title": "Encontro original",
        "description": "Descrição",
        "starts_at": "2026-10-10T09:00",
        "ends_at": "2026-10-10T11:00",
    }


@pytest.fixture
def original_meeting(planned_class):
    return Meeting.objects.create(
        class_group=planned_class,
        title="Encontro original",
        description="Descrição",
        starts_at=timezone.make_aware(datetime(2026, 10, 10, 9)),
        ends_at=timezone.make_aware(datetime(2026, 10, 10, 11)),
    )


def test_duplicate_create_returns_form_error_without_changes(
    client, admin_user, planned_class, original_meeting, meeting_data
):
    client.force_login(admin_user)
    before = list(Meeting.objects.values())
    response = client.post(
        reverse("workshops:meeting-create", args=[planned_class.pk]), meeting_data
    )
    assert response.status_code == 200
    assert "starts_at" in response.context["form"].errors
    assert "já possui um encontro" in response.content.decode()
    assert list(Meeting.objects.values()) == before


def test_unchanged_update_accepts_own_start_and_duplicate_update_preserves_records(
    client, admin_user, planned_class, original_meeting, meeting_data
):
    client.force_login(admin_user)
    path = reverse("workshops:meeting-update", args=[original_meeting.pk])
    assert client.post(path, meeting_data | {"title": "Editado"}).status_code == 302
    form = MeetingForm(
        meeting_data | {"starts_at": "2026-10-11T09:00", "ends_at": "2026-10-11T11:00"},
        class_group=planned_class,
    )
    assert form.is_valid(), form.errors
    another = form.save()
    before = list(Meeting.objects.order_by("pk").values())
    response = client.post(reverse("workshops:meeting-update", args=[another.pk]), meeting_data)
    assert response.status_code == 200
    assert "starts_at" in response.context["form"].errors
    assert list(Meeting.objects.order_by("pk").values()) == before


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("update", [False, True])
def test_duplicate_committed_between_validation_and_save_is_controlled(
    client, admin_user, planned_class, meeting_data, monkeypatch, update
):
    client.force_login(admin_user)
    if update:
        form = MeetingForm(
            meeting_data | {"starts_at": "2026-10-11T09:00", "ends_at": "2026-10-11T11:00"},
            class_group=planned_class,
        )
        assert form.is_valid()
        original = form.save()
        original_before = Meeting.objects.values().get(pk=original.pk)
        path = reverse("workshops:meeting-update", args=[original.pk])
    else:
        path = reverse("workshops:meeting-create", args=[planned_class.pk])
    save = MeetingForm.save

    def competing_commit(form, *args, **kwargs):
        def insert():
            try:
                Meeting.objects.create(
                    class_group_id=planned_class.pk,
                    title="Gravação concorrente",
                    starts_at=form.cleaned_data["starts_at"],
                    ends_at=form.cleaned_data["ends_at"],
                )
            finally:
                connections.close_all()

        with ThreadPoolExecutor(max_workers=1) as executor:
            executor.submit(insert).result(timeout=10)
        return save(form, *args, **kwargs)

    monkeypatch.setattr(MeetingForm, "save", competing_commit)
    response = client.post(path, meeting_data)
    assert response.status_code == 200
    assert "starts_at" in response.context["form"].errors
    assert Meeting.objects.filter(title="Gravação concorrente").count() == 1
    assert Meeting.objects.count() == (2 if update else 1)
    if update:
        assert Meeting.objects.values().get(pk=original.pk) == original_before
    # A query succeeds after rollback, proving the exception was caught outside its savepoint.
    assert ClassGroup.objects.filter(pk=planned_class.pk).exists()


def test_other_integrity_errors_are_not_hidden(
    client, admin_user, planned_class, meeting_data, monkeypatch
):
    client.force_login(admin_user)

    def invalid_save(form, *args, **kwargs):
        form.instance.title = None
        return form.instance.save()

    monkeypatch.setattr(MeetingForm, "save", invalid_save)
    with pytest.raises(IntegrityError):
        client.post(reverse("workshops:meeting-create", args=[planned_class.pk]), meeting_data)
    assert not Meeting.objects.exists()


def admin_payload(class_group):
    return {
        "workshop": class_group.workshop_id,
        "code": class_group.code,
        "title": class_group.title,
        "location": class_group.location,
        "capacity": class_group.capacity,
        "registration_opens_at_0": "2026-09-15",
        "registration_opens_at_1": "08:00:00",
        "registration_closes_at_0": "2026-09-30",
        "registration_closes_at_1": "18:00:00",
        "start_date": "2026-10-01",
        "end_date": "2026-11-30",
        "created_by": class_group.created_by_id,
        "instructor_links-TOTAL_FORMS": "0",
        "instructor_links-INITIAL_FORMS": "0",
        "instructor_links-MIN_NUM_FORMS": "0",
        "instructor_links-MAX_NUM_FORMS": "1000",
        "meetings-TOTAL_FORMS": "0",
        "meetings-INITIAL_FORMS": "0",
        "meetings-MIN_NUM_FORMS": "0",
        "meetings-MAX_NUM_FORMS": "1000",
        "_save": "Salvar",
    }


@pytest.mark.parametrize("target", ["OPEN", "IN_PROGRESS", "COMPLETED", "CANCELLED"])
def test_admin_direct_transition_rejects_whole_form(client, planned_class, target):
    superuser = User.objects.create_superuser(
        email="super@example.com", password="secret", full_name="Super Admin", role="ADMIN"
    )
    client.force_login(superuser)
    before = ClassGroup.objects.values().get(pk=planned_class.pk)
    payload = admin_payload(planned_class) | {"status": target, "title": "Alteração parcial"}
    response = client.post(
        reverse("admin:workshops_classgroup_change", args=[planned_class.pk]), payload
    )
    assert response.status_code == 200
    assert "não pode ser alterada diretamente" in response.content.decode()
    assert ClassGroup.objects.values().get(pk=planned_class.pk) == before
    assert not planned_class.meetings.exists()
    assert not planned_class.instructor_links.exists()


def test_admin_preserves_legitimate_other_field_edits(client, planned_class):
    superuser = User.objects.create_superuser(
        email="super@example.com", password="secret", full_name="Super Admin", role="ADMIN"
    )
    client.force_login(superuser)
    path = reverse("admin:workshops_classgroup_change", args=[planned_class.pk])
    response = client.get(path)
    assert "status" not in response.context["adminform"].form.fields
    assert "processar a conclusão na aplicação" in response.content.decode()
    response = client.post(path, admin_payload(planned_class) | {"title": "Título permitido"})
    planned_class.refresh_from_db()
    assert response.status_code == 302
    assert planned_class.title == "Título permitido"
    assert planned_class.status == ClassGroupStatus.PLANNED


def test_admin_has_no_state_actions_or_academic_write_paths(client, admin_user):
    from apps.enrollments.models import Enrollment
    from apps.learning.models import Certificate, Evaluation, StudentProject

    request = client.get("/").wsgi_request
    request.user = admin_user
    class_admin = admin.site._registry[ClassGroup]
    assert "status" not in class_admin.list_editable
    assert class_admin.get_actions(request) == {}
    for model in [Enrollment, Evaluation, StudentProject, Certificate]:
        model_admin = admin.site._registry[model]
        assert not model_admin.has_add_permission(request)
        assert not model_admin.has_change_permission(request)
        assert not model_admin.has_delete_permission(request)


def test_admin_inline_status_forgery_rejects_parent_and_meeting_edits(
    client, planned_class, original_meeting
):
    superuser = User.objects.create_superuser(
        email="super@example.com", password="secret", full_name="Super Admin", role="ADMIN"
    )
    client.force_login(superuser)
    class_before = ClassGroup.objects.values().get(pk=planned_class.pk)
    meeting_before = Meeting.objects.values().get(pk=original_meeting.pk)
    payload = admin_payload(planned_class) | {
        "title": "Alteração parcial",
        "meetings-TOTAL_FORMS": "1",
        "meetings-INITIAL_FORMS": "1",
        "meetings-0-id": str(original_meeting.pk),
        "meetings-0-class_group": str(planned_class.pk),
        "meetings-0-title": "Alteração parcial",
        "meetings-0-description": original_meeting.description,
        "meetings-0-starts_at_0": "2026-10-10",
        "meetings-0-starts_at_1": "09:00:00",
        "meetings-0-ends_at_0": "2026-10-10",
        "meetings-0-ends_at_1": "11:00:00",
        "meetings-0-status": "COMPLETED",
    }
    response = client.post(
        reverse("admin:workshops_classgroup_change", args=[planned_class.pk]), payload
    )
    assert response.status_code == 200
    assert "não pode ser alterada diretamente" in response.content.decode()
    assert ClassGroup.objects.values().get(pk=planned_class.pk) == class_before
    assert Meeting.objects.values().get(pk=original_meeting.pk) == meeting_before


def test_admin_add_cannot_create_completed_class(client, planned_class):
    superuser = User.objects.create_superuser(
        email="super@example.com", password="secret", full_name="Super Admin", role="ADMIN"
    )
    client.force_login(superuser)
    payload = admin_payload(planned_class) | {"code": "FORGED", "status": "COMPLETED"}
    response = client.post(reverse("admin:workshops_classgroup_add"), payload)
    assert response.status_code == 200
    assert "não pode ser alterada diretamente" in response.content.decode()
    assert not ClassGroup.objects.filter(code="FORGED").exists()


@pytest.mark.parametrize("processed", [False, True])
def test_admin_cannot_modify_processed_meeting_or_extend_closed_class(
    client, planned_class, original_meeting, processed
):
    superuser = User.objects.create_superuser(
        email="super@example.com", password="secret", full_name="Super Admin", role="ADMIN"
    )
    client.force_login(superuser)
    if processed:
        original_meeting.status = "COMPLETED"
        original_meeting.save()
    else:
        planned_class.status = "COMPLETED"
        planned_class.save()
    before = list(Meeting.objects.values())
    payload = {
        "class_group": str(planned_class.pk),
        "title": "Alteração parcial",
        "description": "",
        "starts_at_0": "2026-10-12",
        "starts_at_1": "09:00:00",
        "ends_at_0": "2026-10-12",
        "ends_at_1": "11:00:00",
        "_save": "Salvar",
    }
    path = reverse("admin:workshops_meeting_change", args=[original_meeting.pk])
    assert client.post(path, payload).status_code == 200
    assert list(Meeting.objects.values()) == before
    if not processed:
        assert client.post(reverse("admin:workshops_meeting_add"), payload).status_code == 200
        assert list(Meeting.objects.values()) == before
