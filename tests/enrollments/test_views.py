import pytest
from django.urls import reverse

from apps.enrollments.models import Enrollment, EnrollmentStatus
from apps.enrollments.services import create_enrollment
from apps.people.models import Instructor
from apps.workshops.models import ClassGroup, ClassInstructor

pytestmark = pytest.mark.django_db


def test_enrollment_list_requires_authentication(client):
    response = client.get(reverse("enrollments:list"))

    assert response.status_code == 302
    assert response.url.startswith(reverse("login"))


def test_participant_sees_available_class_and_requests_enrollment(
    client, adult_participant, open_class
):
    client.force_login(adult_participant.user)

    response = client.get(reverse("enrollments:available-classes"))
    created = client.post(
        reverse("enrollments:participant-create", kwargs={"class_pk": open_class.pk})
    )

    assert response.status_code == 200
    assert open_class.title in response.content.decode()
    assert created.status_code == 302
    assert Enrollment.objects.filter(participant=adult_participant, class_group=open_class).exists()


def test_participant_only_sees_own_enrollment(
    client, adult_participant, second_participant, open_class, admin_user
):
    own = create_enrollment(
        participant=adult_participant,
        class_group=open_class,
        actor=adult_participant.user,
    )
    other = Enrollment.objects.create(
        participant=second_participant,
        class_group=open_class,
        status=EnrollmentStatus.WAITLISTED,
        created_by=admin_user,
    )
    client.force_login(adult_participant.user)

    response = client.get(reverse("enrollments:list"))
    content = response.content.decode()

    assert own.class_group.title in content
    assert adult_participant.full_name not in content
    assert other.participant.full_name not in content


def test_participant_cannot_open_administrative_queue(client, adult_participant, open_class):
    client.force_login(adult_participant.user)

    response = client.get(reverse("enrollments:class-queue", kwargs={"class_pk": open_class.pk}))

    assert response.status_code == 403


def test_administrator_registers_and_confirms_enrollment(
    client, adult_participant, open_class, admin_user
):
    client.force_login(admin_user)
    created = client.post(
        reverse("enrollments:class-create", kwargs={"class_pk": open_class.pk}),
        {"participant": adult_participant.pk, "class_group": open_class.pk},
    )
    enrollment = Enrollment.objects.get(participant=adult_participant, class_group=open_class)

    confirmed = client.post(reverse("enrollments:confirm", kwargs={"pk": enrollment.pk}))
    enrollment.refresh_from_db()

    assert created.status_code == 302
    assert confirmed.status_code == 302
    assert enrollment.status == EnrollmentStatus.CONFIRMED


def test_administrator_queue_renders_occupancy(client, adult_participant, open_class, admin_user):
    create_enrollment(
        participant=adult_participant,
        class_group=open_class,
        actor=admin_user,
    )
    client.force_login(admin_user)

    response = client.get(reverse("enrollments:class-queue", kwargs={"class_pk": open_class.pk}))

    assert response.status_code == 200
    assert adult_participant.full_name in response.content.decode()
    assert "Disponíveis" in response.content.decode()


def test_administrative_cancel_collects_justification(
    client, adult_participant, open_class, admin_user
):
    enrollment = create_enrollment(
        participant=adult_participant,
        class_group=open_class,
        actor=admin_user,
    )
    client.force_login(admin_user)

    form_response = client.get(reverse("enrollments:cancel", kwargs={"pk": enrollment.pk}))
    invalid = client.post(
        reverse("enrollments:cancel", kwargs={"pk": enrollment.pk}), {"reason": ""}
    )
    valid = client.post(
        reverse("enrollments:cancel", kwargs={"pk": enrollment.pk}),
        {"reason": "Solicitação registrada pela família."},
    )
    enrollment.refresh_from_db()

    assert form_response.status_code == 200
    assert invalid.status_code == 200
    assert valid.status_code == 302
    assert enrollment.status == EnrollmentStatus.CANCELLED
    assert enrollment.status_reason == "Solicitação registrada pela família."


def test_reject_view_requires_reason(client, adult_participant, open_class, admin_user):
    enrollment = create_enrollment(
        participant=adult_participant,
        class_group=open_class,
        actor=admin_user,
    )
    client.force_login(admin_user)

    response = client.post(
        reverse("enrollments:reject", kwargs={"pk": enrollment.pk}), {"reason": ""}
    )
    enrollment.refresh_from_db()

    assert response.status_code == 200
    assert enrollment.status == EnrollmentStatus.PENDING
    assert "obrigatório" in response.content.decode()


def test_instructor_sees_only_enrollments_from_assigned_class(
    client,
    adult_participant,
    second_participant,
    open_class,
    published_workshop,
    instructor_user,
    admin_user,
):
    instructor = Instructor.objects.create(user=instructor_user)
    ClassInstructor.objects.create(class_group=open_class, instructor=instructor)
    hidden_class = ClassGroup.objects.create(
        workshop=published_workshop,
        code="CDF-HIDDEN",
        title="Turma não vinculada",
        location="Outro local",
        capacity=10,
        registration_opens_at=open_class.registration_opens_at,
        registration_closes_at=open_class.registration_closes_at,
        start_date=open_class.start_date,
        end_date=open_class.end_date,
        created_by=admin_user,
    )
    visible = Enrollment.objects.create(
        participant=adult_participant,
        class_group=open_class,
        created_by=admin_user,
    )
    Enrollment.objects.create(
        participant=second_participant,
        class_group=hidden_class,
        created_by=admin_user,
    )
    client.force_login(instructor_user)

    response = client.get(reverse("enrollments:list"))
    content = response.content.decode()

    assert visible.participant.full_name in content
    assert second_participant.full_name not in content


def test_participant_cannot_cancel_someone_elses_enrollment(
    client, adult_participant, second_participant, open_class, admin_user
):
    enrollment = Enrollment.objects.create(
        participant=second_participant,
        class_group=open_class,
        created_by=admin_user,
    )
    client.force_login(adult_participant.user)

    response = client.post(reverse("enrollments:cancel", kwargs={"pk": enrollment.pk}))

    assert response.status_code == 403
    enrollment.refresh_from_db()
    assert enrollment.status == EnrollmentStatus.PENDING
