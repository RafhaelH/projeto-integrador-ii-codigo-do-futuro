import pytest
from django.urls import reverse

from apps.learning.models import Attendance, AttendanceStatus

pytestmark = pytest.mark.django_db


def formset_data(*enrollments, status=AttendanceStatus.PRESENT):
    data = {
        "form-TOTAL_FORMS": str(len(enrollments)),
        "form-INITIAL_FORMS": str(len(enrollments)),
        "form-MIN_NUM_FORMS": "1",
        "form-MAX_NUM_FORMS": "1000",
    }
    for index, enrollment in enumerate(enrollments):
        data[f"form-{index}-enrollment_id"] = str(enrollment.pk)
        data[f"form-{index}-status"] = status
        data[f"form-{index}-note"] = ""
    return data


def test_class_frequency_requires_authentication(client, learning_class):
    response = client.get(
        reverse("learning:class-attendance", kwargs={"class_pk": learning_class.pk})
    )

    assert response.status_code == 302
    assert response.url.startswith(reverse("login"))


def test_participant_cannot_access_class_call(client, participant_user, learning_class):
    client.force_login(participant_user)

    response = client.get(
        reverse("learning:class-attendance", kwargs={"class_pk": learning_class.pk})
    )

    assert response.status_code == 403


def test_assigned_instructor_sees_class_frequency(
    client, instructor_user, assigned_instructor, confirmed_enrollment, past_meeting
):
    client.force_login(instructor_user)

    response = client.get(
        reverse(
            "learning:class-attendance",
            kwargs={"class_pk": confirmed_enrollment.class_group_id},
        )
    )

    assert response.status_code == 200
    assert confirmed_enrollment.participant.full_name in response.content.decode()
    assert past_meeting.title in response.content.decode()


def test_unassigned_instructor_cannot_see_class(client, instructor_user, learning_class):
    client.force_login(instructor_user)

    response = client.get(
        reverse("learning:class-attendance", kwargs={"class_pk": learning_class.pk})
    )

    assert response.status_code == 404


def test_admin_records_call_through_form(
    client,
    confirmed_enrollment,
    second_confirmed_enrollment,
    past_meeting,
    admin_user,
):
    client.force_login(admin_user)
    url = reverse("learning:meeting-attendance", kwargs={"meeting_pk": past_meeting.pk})

    page = client.get(url)
    response = client.post(
        url,
        formset_data(confirmed_enrollment, second_confirmed_enrollment),
    )

    assert page.status_code == 200
    assert confirmed_enrollment.participant.full_name in page.content.decode()
    assert response.status_code == 302
    assert Attendance.objects.filter(meeting=past_meeting).count() == 2


def test_future_meeting_form_shows_domain_error(
    client, confirmed_enrollment, learning_class, admin_user
):
    from datetime import timedelta

    from django.utils import timezone

    from apps.workshops.models import Meeting

    starts = timezone.now() + timedelta(days=1)
    meeting = Meeting.objects.create(
        class_group=learning_class,
        title="Encontro futuro",
        starts_at=starts,
        ends_at=starts + timedelta(hours=2),
    )
    client.force_login(admin_user)

    response = client.post(
        reverse("learning:meeting-attendance", kwargs={"meeting_pk": meeting.pk}),
        formset_data(confirmed_enrollment),
    )

    assert response.status_code == 200
    assert "após o término" in response.content.decode()
    assert not Attendance.objects.filter(meeting=meeting).exists()


def test_participant_sees_only_own_frequency(
    client,
    confirmed_enrollment,
    second_confirmed_enrollment,
    past_meeting,
    admin_user,
):
    Attendance.objects.create(
        enrollment=confirmed_enrollment,
        meeting=past_meeting,
        status=AttendanceStatus.PRESENT,
        recorded_by=admin_user,
    )
    client.force_login(confirmed_enrollment.participant.user)

    response = client.get(reverse("learning:participant-frequency"))
    content = response.content.decode()

    assert response.status_code == 200
    assert confirmed_enrollment.class_group.title in content
    assert second_confirmed_enrollment.participant.full_name not in content
