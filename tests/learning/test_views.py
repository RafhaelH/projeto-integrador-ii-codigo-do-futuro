import pytest
from django.urls import reverse
from django.utils import timezone

from apps.learning.models import (
    Attendance,
    AttendanceStatus,
    Evaluation,
    StudentProject,
)
from apps.learning.services import issue_certificate, revoke_certificate
from apps.workshops.models import MeetingStatus

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


def test_participant_registers_own_project(client, confirmed_enrollment):
    client.force_login(confirmed_enrollment.participant.user)
    url = reverse(
        "learning:participant-project",
        kwargs={"enrollment_pk": confirmed_enrollment.pk},
    )

    response = client.post(
        url,
        {
            "title": "Meu portfólio",
            "description": "Site com os projetos da oficina.",
            "repository_url": "https://github.com/exemplo/portfolio",
            "demonstration_url": "",
            "is_delivered": "on",
        },
    )

    assert response.status_code == 302
    assert StudentProject.objects.filter(
        enrollment=confirmed_enrollment,
        is_delivered=True,
    ).exists()


def test_participant_cannot_open_another_enrollments_project(
    client, confirmed_enrollment, second_confirmed_enrollment
):
    client.force_login(confirmed_enrollment.participant.user)

    response = client.get(
        reverse(
            "learning:participant-project",
            kwargs={"enrollment_pk": second_confirmed_enrollment.pk},
        )
    )

    assert response.status_code == 404


def test_assigned_instructor_records_evaluation(
    client, instructor_user, assigned_instructor, confirmed_enrollment
):
    client.force_login(instructor_user)

    response = client.post(
        reverse(
            "learning:evaluation",
            kwargs={"enrollment_pk": confirmed_enrollment.pk},
        ),
        {
            "final_score": "8.5",
            "feedback": "Evolução consistente.",
            "publish": "on",
        },
    )

    assert response.status_code == 302
    evaluation = Evaluation.objects.get(enrollment=confirmed_enrollment)
    assert evaluation.final_score == 8.5
    assert evaluation.published_at is not None


def test_unassigned_instructor_cannot_open_evaluation(
    client, instructor_user, confirmed_enrollment
):
    client.force_login(instructor_user)

    response = client.get(
        reverse(
            "learning:evaluation",
            kwargs={"enrollment_pk": confirmed_enrollment.pk},
        )
    )

    assert response.status_code == 403


def test_participant_does_not_see_unpublished_evaluation_feedback(
    client, confirmed_enrollment, admin_user
):
    Evaluation.objects.create(
        enrollment=confirmed_enrollment,
        final_score="9.0",
        feedback="Devolutiva ainda privada.",
        evaluated_by=admin_user,
    )
    client.force_login(confirmed_enrollment.participant.user)

    response = client.get(reverse("learning:participant-frequency"))
    content = response.content.decode()

    assert "Devolutiva ainda privada." not in content
    assert "Aguardando publicação" in content


def test_admin_completes_class_through_academic_flow(
    client, confirmed_enrollment, past_meeting, admin_user
):
    past_meeting.status = MeetingStatus.COMPLETED
    past_meeting.save()
    Attendance.objects.create(
        enrollment=confirmed_enrollment,
        meeting=past_meeting,
        status=AttendanceStatus.PRESENT,
        recorded_by=admin_user,
    )
    StudentProject.objects.create(
        enrollment=confirmed_enrollment,
        title="Projeto final",
        description="Entrega.",
        is_delivered=True,
        delivered_at=timezone.now(),
    )
    Evaluation.objects.create(
        enrollment=confirmed_enrollment,
        final_score="7.0",
        feedback="Aprovado.",
        evaluated_by=admin_user,
    )
    client.force_login(admin_user)

    response = client.post(
        reverse(
            "learning:complete-class",
            kwargs={"class_pk": confirmed_enrollment.class_group_id},
        )
    )
    confirmed_enrollment.refresh_from_db()

    assert response.status_code == 302
    assert confirmed_enrollment.status == "APPROVED"


def prepare_certificate(enrollment, meeting, admin_user):
    enrollment.status = "APPROVED"
    enrollment.save(update_fields=["status", "updated_at"])
    meeting.status = MeetingStatus.COMPLETED
    meeting.save(update_fields=["status", "updated_at"])
    return issue_certificate(enrollment, actor=admin_user)


def test_certificate_list_requires_authentication(client):
    response = client.get(reverse("learning:certificate-list"))

    assert response.status_code == 302
    assert response.url.startswith(reverse("login"))


def test_admin_issues_certificate_through_view(
    client,
    confirmed_enrollment,
    past_meeting,
    admin_user,
):
    confirmed_enrollment.status = "APPROVED"
    confirmed_enrollment.save(update_fields=["status", "updated_at"])
    past_meeting.status = MeetingStatus.COMPLETED
    past_meeting.save(update_fields=["status", "updated_at"])
    client.force_login(admin_user)

    response = client.post(
        reverse(
            "learning:certificate-issue",
            kwargs={"enrollment_pk": confirmed_enrollment.pk},
        )
    )

    certificate = confirmed_enrollment.certificate
    assert response.status_code == 302
    assert response.url == reverse(
        "learning:certificate-detail",
        kwargs={"pk": certificate.pk},
    )


def test_participant_downloads_own_certificate(
    client,
    confirmed_enrollment,
    past_meeting,
    admin_user,
):
    certificate = prepare_certificate(confirmed_enrollment, past_meeting, admin_user)
    client.force_login(confirmed_enrollment.participant.user)

    response = client.get(
        reverse(
            "learning:certificate-download",
            kwargs={"pk": certificate.pk},
        )
    )

    assert response.status_code == 200
    assert response["Content-Type"] == "application/pdf"
    assert response.content.startswith(b"%PDF-1.4")
    assert certificate.verification_code in response["Content-Disposition"]


def test_participant_cannot_access_another_certificate(
    client,
    second_confirmed_enrollment,
    past_meeting,
    admin_user,
    participant_user,
):
    certificate = prepare_certificate(
        second_confirmed_enrollment,
        past_meeting,
        admin_user,
    )
    client.force_login(participant_user)

    response = client.get(
        reverse(
            "learning:certificate-detail",
            kwargs={"pk": certificate.pk},
        )
    )

    assert response.status_code == 404


def test_assigned_instructor_views_certificate(
    client,
    confirmed_enrollment,
    past_meeting,
    admin_user,
    assigned_instructor,
):
    certificate = prepare_certificate(confirmed_enrollment, past_meeting, admin_user)
    client.force_login(assigned_instructor.user)

    response = client.get(
        reverse(
            "learning:certificate-detail",
            kwargs={"pk": certificate.pk},
        )
    )

    assert response.status_code == 200
    assert certificate.verification_code in response.content.decode()


def test_unassigned_instructor_cannot_access_certificate(
    client,
    confirmed_enrollment,
    past_meeting,
    admin_user,
    instructor_user,
):
    certificate = prepare_certificate(confirmed_enrollment, past_meeting, admin_user)
    client.force_login(instructor_user)

    response = client.get(
        reverse(
            "learning:certificate-detail",
            kwargs={"pk": certificate.pk},
        )
    )

    assert response.status_code == 404


def test_revoked_certificate_cannot_be_downloaded(
    client,
    confirmed_enrollment,
    past_meeting,
    admin_user,
):
    certificate = prepare_certificate(confirmed_enrollment, past_meeting, admin_user)
    revoke_certificate(
        certificate,
        reason="Documento substituído.",
        actor=admin_user,
    )
    client.force_login(admin_user)

    response = client.get(
        reverse(
            "learning:certificate-download",
            kwargs={"pk": certificate.pk},
        )
    )

    assert response.status_code == 403


def test_admin_revokes_certificate_through_view(
    client,
    confirmed_enrollment,
    past_meeting,
    admin_user,
):
    certificate = prepare_certificate(confirmed_enrollment, past_meeting, admin_user)
    client.force_login(admin_user)

    response = client.post(
        reverse(
            "learning:certificate-revoke",
            kwargs={"pk": certificate.pk},
        ),
        {"reason": "Dados incorretos."},
    )

    certificate.refresh_from_db()
    assert response.status_code == 302
    assert not certificate.is_active
    assert certificate.revocation_reason == "Dados incorretos."
