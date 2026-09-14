from concurrent.futures import ThreadPoolExecutor
from datetime import date

import pytest
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import close_old_connections, connection

from apps.accounts.models import User
from apps.enrollments.models import Enrollment, EnrollmentStatus
from apps.enrollments.services import (
    available_places,
    cancel_enrollment,
    confirm_enrollment,
    create_enrollment,
    occupied_places,
    promote_next_waitlisted,
    reject_enrollment,
)

pytestmark = pytest.mark.django_db


def test_eligible_request_with_vacancy_is_pending(adult_participant, open_class):
    enrollment = create_enrollment(
        participant=adult_participant,
        class_group=open_class,
        actor=adult_participant.user,
    )

    assert enrollment.status == EnrollmentStatus.PENDING
    assert enrollment.status_history.count() == 1
    assert occupied_places(open_class) == 0


def test_full_class_places_request_at_end_of_waitlist(
    adult_participant, second_participant, open_class, admin_user
):
    Enrollment.objects.create(
        participant=adult_participant,
        class_group=open_class,
        status=EnrollmentStatus.CONFIRMED,
        created_by=admin_user,
    )

    waiting = create_enrollment(
        participant=second_participant,
        class_group=open_class,
        actor=second_participant.user,
    )

    assert waiting.status == EnrollmentStatus.WAITLISTED
    assert waiting.waitlisted_at is not None
    assert waiting.waitlist_position == 1
    assert available_places(open_class) == 0


def test_full_class_without_waitlist_keeps_request_pending(
    adult_participant, second_participant, open_class, admin_user
):
    open_class.waitlist_enabled = False
    open_class.save()
    Enrollment.objects.create(
        participant=adult_participant,
        class_group=open_class,
        status=EnrollmentStatus.CONFIRMED,
        created_by=admin_user,
    )

    enrollment = create_enrollment(
        participant=second_participant,
        class_group=open_class,
        actor=second_participant.user,
    )

    assert enrollment.status == EnrollmentStatus.PENDING


def test_duplicate_request_is_rejected(adult_participant, open_class):
    create_enrollment(
        participant=adult_participant,
        class_group=open_class,
        actor=adult_participant.user,
    )

    with pytest.raises(ValidationError, match="já possui inscrição"):
        create_enrollment(
            participant=adult_participant,
            class_group=open_class,
            actor=adult_participant.user,
        )


def test_user_cannot_request_for_another_participant(
    adult_participant, second_participant, open_class
):
    with pytest.raises(PermissionDenied):
        create_enrollment(
            participant=second_participant,
            class_group=open_class,
            actor=adult_participant.user,
        )


def test_ineligible_age_is_rejected(adult_participant, open_class):
    adult_participant.birth_date = date(2015, 1, 1)
    adult_participant.save()

    with pytest.raises(ValidationError, match="entre 14 e 21"):
        create_enrollment(
            participant=adult_participant,
            class_group=open_class,
            actor=adult_participant.user,
        )


def test_minor_without_guardian_is_rejected(adult_participant, open_class):
    adult_participant.birth_date = date(2010, 1, 1)
    adult_participant.save()

    with pytest.raises(ValidationError, match="responsável ativo"):
        create_enrollment(
            participant=adult_participant,
            class_group=open_class,
            actor=adult_participant.user,
        )


def test_admin_confirms_pending_and_occupies_vacancy(adult_participant, open_class, admin_user):
    enrollment = create_enrollment(
        participant=adult_participant,
        class_group=open_class,
        actor=admin_user,
    )

    confirmed = confirm_enrollment(enrollment, actor=admin_user)

    assert confirmed.status == EnrollmentStatus.CONFIRMED
    assert confirmed.confirmed_at is not None
    assert occupied_places(open_class) == 1
    assert list(confirmed.status_history.values_list("to_status", flat=True)) == [
        EnrollmentStatus.PENDING,
        EnrollmentStatus.CONFIRMED,
    ]


def test_capacity_is_never_exceeded(adult_participant, second_participant, open_class, admin_user):
    first = create_enrollment(
        participant=adult_participant,
        class_group=open_class,
        actor=admin_user,
    )
    second = create_enrollment(
        participant=second_participant,
        class_group=open_class,
        actor=admin_user,
    )
    confirm_enrollment(first, actor=admin_user)

    with pytest.raises(ValidationError, match="Não há vaga"):
        confirm_enrollment(second, actor=admin_user)

    assert occupied_places(open_class) == open_class.capacity


def test_out_of_order_waitlist_confirmation_requires_justification(
    adult_participant, second_participant, open_class, admin_user
):
    open_class.capacity = 2
    open_class.save()
    first = Enrollment.objects.create(
        participant=adult_participant,
        class_group=open_class,
        status=EnrollmentStatus.WAITLISTED,
        waitlisted_at=open_class.registration_opens_at,
        created_by=admin_user,
    )
    second = Enrollment.objects.create(
        participant=second_participant,
        class_group=open_class,
        status=EnrollmentStatus.WAITLISTED,
        waitlisted_at=open_class.registration_closes_at,
        created_by=admin_user,
    )

    with pytest.raises(ValidationError, match="exige justificativa"):
        confirm_enrollment(second, actor=admin_user)

    confirmed = confirm_enrollment(second, actor=admin_user, reason="Prioridade documentada")
    first.refresh_from_db()
    assert confirmed.status == EnrollmentStatus.CONFIRMED
    assert confirmed.status_reason == "Prioridade documentada"
    assert first.status == EnrollmentStatus.WAITLISTED


def test_rejection_requires_reason(adult_participant, open_class, admin_user):
    enrollment = create_enrollment(
        participant=adult_participant,
        class_group=open_class,
        actor=admin_user,
    )

    with pytest.raises(ValidationError, match="motivo"):
        reject_enrollment(enrollment, actor=admin_user, reason="")

    rejected = reject_enrollment(enrollment, actor=admin_user, reason="Dados inconsistentes")
    assert rejected.status == EnrollmentStatus.REJECTED


def test_participant_cancellation_promotes_oldest_waitlisted(
    adult_participant, second_participant, open_class, admin_user
):
    confirmed = create_enrollment(
        participant=adult_participant,
        class_group=open_class,
        actor=adult_participant.user,
    )
    confirm_enrollment(confirmed, actor=admin_user)
    waiting = create_enrollment(
        participant=second_participant,
        class_group=open_class,
        actor=second_participant.user,
    )

    cancelled, promoted = cancel_enrollment(confirmed, actor=adult_participant.user)

    assert cancelled.status == EnrollmentStatus.CANCELLED
    assert promoted.pk == waiting.pk
    assert promoted.status == EnrollmentStatus.CONFIRMED
    assert occupied_places(open_class) == 1


def test_administrative_cancellation_requires_reason(adult_participant, open_class, admin_user):
    enrollment = create_enrollment(
        participant=adult_participant,
        class_group=open_class,
        actor=admin_user,
    )

    with pytest.raises(ValidationError, match="motivo"):
        cancel_enrollment(enrollment, actor=admin_user)


def test_participant_cannot_cancel_after_class_starts(adult_participant, open_class, admin_user):
    enrollment = create_enrollment(
        participant=adult_participant,
        class_group=open_class,
        actor=adult_participant.user,
    )
    confirm_enrollment(enrollment, actor=admin_user)
    open_class.start_date = open_class.registration_opens_at.date()
    open_class.save()

    with pytest.raises(ValidationError, match="exige um administrador"):
        cancel_enrollment(enrollment, actor=adult_participant.user)


def test_manual_promotion_uses_oldest_eligible(
    adult_participant, second_participant, open_class, admin_user
):
    open_class.capacity = 1
    open_class.save()
    first = Enrollment.objects.create(
        participant=adult_participant,
        class_group=open_class,
        status=EnrollmentStatus.WAITLISTED,
        waitlisted_at=open_class.registration_opens_at,
        created_by=admin_user,
    )
    Enrollment.objects.create(
        participant=second_participant,
        class_group=open_class,
        status=EnrollmentStatus.WAITLISTED,
        waitlisted_at=open_class.registration_closes_at,
        created_by=admin_user,
    )

    promoted = promote_next_waitlisted(open_class, actor=admin_user)

    assert promoted.pk == first.pk
    assert promoted.status == EnrollmentStatus.CONFIRMED


def test_waitlist_cannot_be_promoted_after_class_starts(adult_participant, open_class, admin_user):
    Enrollment.objects.create(
        participant=adult_participant,
        class_group=open_class,
        status=EnrollmentStatus.WAITLISTED,
        waitlisted_at=open_class.registration_opens_at,
        created_by=admin_user,
    )
    open_class.start_date = open_class.registration_opens_at.date()
    open_class.save()

    with pytest.raises(ValidationError, match="antes do início"):
        promote_next_waitlisted(open_class, actor=admin_user)


@pytest.mark.skipif(connection.vendor != "postgresql", reason="Exige bloqueio real do PostgreSQL")
@pytest.mark.django_db(transaction=True)
def test_concurrent_confirmations_do_not_exceed_capacity(
    adult_participant, second_participant, open_class, admin_user
):
    enrollments = [
        Enrollment.objects.create(
            participant=participant,
            class_group=open_class,
            created_by=admin_user,
        )
        for participant in (adult_participant, second_participant)
    ]
    enrollment_ids = [item.pk for item in enrollments]
    actor_id = admin_user.pk

    def attempt(enrollment_id):
        close_old_connections()
        try:
            enrollment = Enrollment.objects.get(pk=enrollment_id)
            actor = User.objects.get(pk=actor_id)
            confirm_enrollment(enrollment, actor=actor)
            return "confirmed"
        except ValidationError:
            return "blocked"
        finally:
            close_old_connections()

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(attempt, enrollment_ids))

    assert sorted(results) == ["blocked", "confirmed"]
    assert Enrollment.objects.filter(status=EnrollmentStatus.CONFIRMED).count() == 1
