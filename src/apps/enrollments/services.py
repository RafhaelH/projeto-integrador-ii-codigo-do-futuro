from datetime import date

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.accounts.models import User, UserRole
from apps.people.models import Participant
from apps.people.services import (
    LEGAL_AGE,
    calculate_age,
    participant_has_active_guardian,
    validate_participant_eligibility,
)
from apps.workshops.models import ClassGroup, ClassGroupStatus

from .models import Enrollment, EnrollmentStatus, EnrollmentStatusHistory

ACTIVE_ENROLLMENT_STATUSES = (
    EnrollmentStatus.PENDING,
    EnrollmentStatus.CONFIRMED,
    EnrollmentStatus.WAITLISTED,
)


def _record_status(
    enrollment: Enrollment,
    *,
    actor: User,
    from_status: str | None,
    reason: str = "",
) -> None:
    EnrollmentStatusHistory.objects.create(
        enrollment=enrollment,
        from_status=from_status,
        to_status=enrollment.status,
        reason=reason.strip(),
        changed_by=actor,
    )


def _validate_registration_window(class_group: ClassGroup, moment=None) -> None:
    moment = moment or timezone.now()
    if class_group.status != ClassGroupStatus.OPEN:
        raise ValidationError("A turma não está com inscrições abertas.")
    if not class_group.registration_opens_at <= moment <= class_group.registration_closes_at:
        raise ValidationError("A solicitação está fora do período de inscrições.")


def _validate_enrollment_eligibility(
    participant: Participant,
    class_group: ClassGroup,
    *,
    registration_date: date | None = None,
) -> None:
    validate_participant_eligibility(participant, class_group.start_date)
    registration_date = registration_date or timezone.localdate()
    if calculate_age(
        participant.birth_date, registration_date
    ) < LEGAL_AGE and not participant_has_active_guardian(participant):
        raise ValidationError("Participantes menores de 18 anos precisam de responsável ativo.")


def _assert_creation_permission(actor: User, participant: Participant) -> None:
    if actor.role == UserRole.ADMIN:
        return
    if actor.role != UserRole.PARTICIPANT or participant.user_id != actor.pk:
        raise PermissionDenied("Você não pode solicitar esta inscrição.")


def occupied_places(class_group: ClassGroup) -> int:
    return class_group.enrollments.filter(status=EnrollmentStatus.CONFIRMED).count()


def available_places(class_group: ClassGroup) -> int:
    return max(class_group.capacity - occupied_places(class_group), 0)


def create_enrollment(
    *, participant: Participant, class_group: ClassGroup, actor: User
) -> Enrollment:
    _assert_creation_permission(actor, participant)

    try:
        with transaction.atomic():
            locked_class = ClassGroup.objects.select_for_update().get(pk=class_group.pk)
            _validate_registration_window(locked_class)
            _validate_enrollment_eligibility(participant, locked_class)

            if Enrollment.objects.filter(
                participant=participant, class_group=locked_class
            ).exists():
                raise ValidationError("O participante já possui inscrição nesta turma.")

            is_full = occupied_places(locked_class) >= locked_class.capacity
            status = (
                EnrollmentStatus.WAITLISTED
                if is_full and locked_class.waitlist_enabled
                else EnrollmentStatus.PENDING
            )
            waitlisted_at = timezone.now() if status == EnrollmentStatus.WAITLISTED else None
            enrollment = Enrollment.objects.create(
                participant=participant,
                class_group=locked_class,
                status=status,
                waitlisted_at=waitlisted_at,
                created_by=actor,
            )
            _record_status(enrollment, actor=actor, from_status=None)
            return enrollment
    except IntegrityError as error:
        raise ValidationError("O participante já possui inscrição nesta turma.") from error


def _first_waitlisted(class_group: ClassGroup) -> Enrollment | None:
    return (
        class_group.enrollments.select_for_update()
        .filter(status=EnrollmentStatus.WAITLISTED)
        .order_by("waitlisted_at", "created_at", "pk")
        .first()
    )


def _confirm_locked(
    enrollment: Enrollment,
    *,
    actor: User,
    reason: str = "",
    enforce_waitlist_order: bool = True,
) -> Enrollment:
    if enrollment.status not in {EnrollmentStatus.PENDING, EnrollmentStatus.WAITLISTED}:
        raise ValidationError("Somente inscrições pendentes ou em espera podem ser confirmadas.")

    _validate_enrollment_eligibility(enrollment.participant, enrollment.class_group)
    if occupied_places(enrollment.class_group) >= enrollment.class_group.capacity:
        raise ValidationError("Não há vaga disponível para confirmar esta inscrição.")

    if enrollment.status == EnrollmentStatus.WAITLISTED and enforce_waitlist_order:
        first = _first_waitlisted(enrollment.class_group)
        if first and first.pk != enrollment.pk and not reason.strip():
            raise ValidationError(
                "A promoção fora da ordem da lista de espera exige justificativa."
            )

    previous = enrollment.status
    enrollment.status = EnrollmentStatus.CONFIRMED
    enrollment.confirmed_at = timezone.now()
    enrollment.status_reason = reason.strip()
    enrollment.save(update_fields=["status", "confirmed_at", "status_reason", "updated_at"])
    _record_status(enrollment, actor=actor, from_status=previous, reason=reason)
    return enrollment


@transaction.atomic
def confirm_enrollment(enrollment: Enrollment, *, actor: User, reason: str = "") -> Enrollment:
    if actor.role != UserRole.ADMIN:
        raise PermissionDenied("Somente administradores podem confirmar inscrições.")
    locked_class = ClassGroup.objects.select_for_update().get(pk=enrollment.class_group_id)
    locked_enrollment = (
        Enrollment.objects.select_for_update()
        .select_related("participant", "class_group")
        .get(pk=enrollment.pk)
    )
    locked_enrollment.class_group = locked_class
    return _confirm_locked(locked_enrollment, actor=actor, reason=reason)


@transaction.atomic
def reject_enrollment(enrollment: Enrollment, *, actor: User, reason: str) -> Enrollment:
    if actor.role != UserRole.ADMIN:
        raise PermissionDenied("Somente administradores podem rejeitar inscrições.")
    reason = reason.strip()
    if not reason:
        raise ValidationError("Informe o motivo da rejeição.")

    locked = Enrollment.objects.select_for_update().get(pk=enrollment.pk)
    if locked.status != EnrollmentStatus.PENDING:
        raise ValidationError("Somente inscrições pendentes podem ser rejeitadas.")
    previous = locked.status
    locked.status = EnrollmentStatus.REJECTED
    locked.status_reason = reason
    locked.save(update_fields=["status", "status_reason", "updated_at"])
    _record_status(locked, actor=actor, from_status=previous, reason=reason)
    return locked


def _promote_next_locked(class_group: ClassGroup, *, actor: User) -> Enrollment | None:
    if (
        class_group.status != ClassGroupStatus.OPEN
        or timezone.localdate() >= class_group.start_date
    ):
        return None
    if occupied_places(class_group) >= class_group.capacity:
        return None

    candidates = list(
        class_group.enrollments.select_for_update()
        .filter(status=EnrollmentStatus.WAITLISTED)
        .select_related("participant")
        .order_by("waitlisted_at", "created_at", "pk")
    )
    for candidate in candidates:
        try:
            _validate_enrollment_eligibility(candidate.participant, class_group)
        except ValidationError:
            continue
        candidate.class_group = class_group
        return _confirm_locked(
            candidate,
            actor=actor,
            reason="Promoção automática da lista de espera.",
            enforce_waitlist_order=False,
        )
    return None


@transaction.atomic
def promote_next_waitlisted(class_group: ClassGroup, *, actor: User) -> Enrollment | None:
    if actor.role != UserRole.ADMIN:
        raise PermissionDenied("Somente administradores podem promover a lista de espera.")
    locked_class = ClassGroup.objects.select_for_update().get(pk=class_group.pk)
    if (
        locked_class.status != ClassGroupStatus.OPEN
        or timezone.localdate() >= locked_class.start_date
    ):
        raise ValidationError("A lista de espera só pode ser promovida antes do início da turma.")
    return _promote_next_locked(locked_class, actor=actor)


@transaction.atomic
def cancel_enrollment(
    enrollment: Enrollment,
    *,
    actor: User,
    reason: str = "",
) -> tuple[Enrollment, Enrollment | None]:
    locked_class = ClassGroup.objects.select_for_update().get(pk=enrollment.class_group_id)
    locked = (
        Enrollment.objects.select_for_update().select_related("participant").get(pk=enrollment.pk)
    )
    locked.class_group = locked_class

    is_admin = actor.role == UserRole.ADMIN
    is_owner = actor.role == UserRole.PARTICIPANT and locked.participant.user_id == actor.pk
    if not is_admin and not is_owner:
        raise PermissionDenied("Você não pode cancelar esta inscrição.")
    if locked.status not in ACTIVE_ENROLLMENT_STATUSES:
        raise ValidationError("Esta inscrição não pode mais ser cancelada.")
    if is_owner and timezone.localdate() >= locked_class.start_date:
        raise ValidationError("Após o início da turma, o cancelamento exige um administrador.")
    if is_admin and not reason.strip():
        raise ValidationError("Informe o motivo do cancelamento administrativo.")

    was_confirmed = locked.status == EnrollmentStatus.CONFIRMED
    previous = locked.status
    locked.status = EnrollmentStatus.CANCELLED
    locked.cancelled_at = timezone.now()
    locked.status_reason = reason.strip()
    locked.save(update_fields=["status", "cancelled_at", "status_reason", "updated_at"])
    _record_status(locked, actor=actor, from_status=previous, reason=reason)

    promoted = _promote_next_locked(locked_class, actor=actor) if was_confirmed else None
    return locked, promoted
