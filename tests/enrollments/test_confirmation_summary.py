from datetime import date

import pytest
from django.urls import reverse
from django.utils import timezone

from apps.enrollments.models import EnrollmentStatus
from apps.enrollments.services import confirm_enrollment, create_enrollment
from apps.people.models import Participant
from apps.reporting.selectors import class_summary_rows, dashboard_snapshot
from apps.workshops.models import ClassGroup

pytestmark = pytest.mark.django_db


def test_capacity_is_displayed_and_stale_page_cannot_overbook(
    client, admin_user, open_class, adult_participant, second_participant
):
    pending = create_enrollment(
        participant=adult_participant, class_group=open_class, actor=admin_user
    )
    client.force_login(admin_user)
    url = reverse("enrollments:confirm", kwargs={"pk": pending.pk})
    response = client.get(url)
    assert response.status_code == 200
    assert response.context["capacity_summary"]["capacity"] == 1
    assert response.context["capacity_summary"]["available"] == 1
    other = create_enrollment(
        participant=second_participant, class_group=open_class, actor=admin_user
    )
    confirm_enrollment(other, actor=admin_user)
    response = client.post(url, {"reason": ""})
    assert response.status_code == 200
    assert response.context["capacity_summary"]["available"] == 0
    pending.refresh_from_db()
    assert pending.status == EnrollmentStatus.PENDING
    assert open_class.enrollments.filter(status=EnrollmentStatus.CONFIRMED).count() == 1


def test_pending_and_waitlist_are_separate_in_metrics(
    client, admin_user, open_class, adult_participant, second_participant
):
    create_enrollment(participant=adult_participant, class_group=open_class, actor=admin_user)
    other = create_enrollment(
        participant=second_participant, class_group=open_class, actor=admin_user
    )
    other.status = EnrollmentStatus.WAITLISTED
    other.save()
    snapshot = dashboard_snapshot(ClassGroup.objects.filter(pk=open_class.pk))
    assert snapshot.pending == 1 and snapshot.waitlisted == 1 and snapshot.occupied == 0
    row = class_summary_rows(ClassGroup.objects.filter(pk=open_class.pk)).get()
    assert row.pending_count == 1 and row.waitlisted_count == 1
    client.force_login(admin_user)
    content = client.get(
        reverse("enrollments:class-queue", kwargs={"class_pk": open_class.pk})
    ).content.decode()
    assert "Inscrições pendentes" in content and "Lista de espera" in content
    assert "Pendentes / espera" not in content


def test_minor_without_guardian_is_blocked_at_enrollment_not_registration(
    client, admin_user, open_class
):
    now = timezone.localdate()
    person = Participant.objects.create(
        full_name="Menor fictício sem responsável", birth_date=date(now.year - 16, 1, 1)
    )
    client.force_login(admin_user)
    response = client.post(
        reverse("enrollments:class-create", kwargs={"class_pk": open_class.pk}),
        {"participant": person.pk, "class_group": open_class.pk},
    )
    assert response.status_code == 200
    assert "responsável ativo" in response.content.decode()
    assert not person.enrollments.exists()
