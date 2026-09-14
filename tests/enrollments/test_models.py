import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone

from apps.enrollments.models import Enrollment, EnrollmentStatus

pytestmark = pytest.mark.django_db


def test_enrollment_is_unique_per_participant_and_class(adult_participant, open_class, admin_user):
    Enrollment.objects.create(
        participant=adult_participant,
        class_group=open_class,
        created_by=admin_user,
    )

    with pytest.raises(IntegrityError):
        Enrollment.objects.create(
            participant=adult_participant,
            class_group=open_class,
            created_by=admin_user,
        )


def test_rejected_enrollment_requires_reason(adult_participant, open_class, admin_user):
    enrollment = Enrollment(
        participant=adult_participant,
        class_group=open_class,
        status=EnrollmentStatus.REJECTED,
        created_by=admin_user,
    )

    with pytest.raises(ValidationError, match="motivo"):
        enrollment.full_clean()


def test_processed_enrollment_cannot_be_deleted(adult_participant, open_class, admin_user):
    enrollment = Enrollment.objects.create(
        participant=adult_participant,
        class_group=open_class,
        status=EnrollmentStatus.CONFIRMED,
        created_by=admin_user,
    )

    with pytest.raises(ValidationError, match="não pode ser excluída"):
        enrollment.delete()


def test_waitlist_position_follows_entry_order(
    adult_participant, second_participant, open_class, admin_user
):
    first = Enrollment.objects.create(
        participant=adult_participant,
        class_group=open_class,
        status=EnrollmentStatus.WAITLISTED,
        waitlisted_at=timezone.now(),
        created_by=admin_user,
    )
    second = Enrollment.objects.create(
        participant=second_participant,
        class_group=open_class,
        status=EnrollmentStatus.WAITLISTED,
        waitlisted_at=timezone.now(),
        created_by=admin_user,
    )

    assert first.waitlist_position == 1
    assert second.waitlist_position == 2
