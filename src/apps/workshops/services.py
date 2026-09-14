from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import ClassGroup, ClassGroupStatus, MeetingStatus, Workshop, WorkshopStatus


@transaction.atomic
def transition_workshop(workshop: Workshop, target: str) -> Workshop:
    current = Workshop.objects.select_for_update().get(pk=workshop.pk)
    allowed = {
        WorkshopStatus.DRAFT: {WorkshopStatus.PUBLISHED},
        WorkshopStatus.PUBLISHED: {WorkshopStatus.ARCHIVED},
        WorkshopStatus.ARCHIVED: set(),
    }
    if target not in allowed[current.status]:
        raise ValidationError("Transição de situação da oficina não permitida.")
    current.status = target
    current.save(update_fields=["status", "updated_at"])
    return current


@transaction.atomic
def transition_class_group(
    class_group: ClassGroup,
    target: str,
    *,
    academic_completion_validated: bool = False,
) -> ClassGroup:
    current = ClassGroup.objects.select_for_update().get(pk=class_group.pk)
    allowed = {
        ClassGroupStatus.PLANNED: {ClassGroupStatus.OPEN, ClassGroupStatus.CANCELLED},
        ClassGroupStatus.OPEN: {ClassGroupStatus.IN_PROGRESS, ClassGroupStatus.CANCELLED},
        ClassGroupStatus.IN_PROGRESS: {ClassGroupStatus.COMPLETED, ClassGroupStatus.CANCELLED},
        ClassGroupStatus.COMPLETED: set(),
        ClassGroupStatus.CANCELLED: set(),
    }
    if target not in allowed[current.status]:
        raise ValidationError("Transição de situação da turma não permitida.")
    if target == ClassGroupStatus.COMPLETED and not academic_completion_validated:
        raise ValidationError("Conclua a turma pelo processamento acadêmico.")

    active_instructors = current.instructor_links.filter(instructor__is_active=True).exists()
    if target == ClassGroupStatus.OPEN:
        current.full_clean(exclude=["status"])
        if not active_instructors:
            raise ValidationError("Vincule ao menos um instrutor ativo antes de abrir inscrições.")
    if target == ClassGroupStatus.IN_PROGRESS:
        if not active_instructors:
            raise ValidationError("A turma precisa de ao menos um instrutor ativo para iniciar.")
        if not current.meetings.filter(status=MeetingStatus.PLANNED).exists():
            raise ValidationError(
                "Cadastre ao menos um encontro planejado antes de iniciar a turma."
            )

    current.status = target
    current.save(update_fields=["status", "updated_at"])
    if target == ClassGroupStatus.CANCELLED:
        current.meetings.filter(status=MeetingStatus.PLANNED, starts_at__gte=timezone.now()).update(
            status=MeetingStatus.CANCELLED, updated_at=timezone.now()
        )
    return current


@transaction.atomic
def cancel_meeting(meeting):
    current = meeting.__class__.objects.select_for_update().get(pk=meeting.pk)
    if current.class_group.status in {
        ClassGroupStatus.COMPLETED,
        ClassGroupStatus.CANCELLED,
    }:
        raise ValidationError("A agenda de uma turma encerrada não pode ser alterada.")
    if current.status != MeetingStatus.PLANNED:
        raise ValidationError("Somente encontros planejados podem ser cancelados.")
    current.status = MeetingStatus.CANCELLED
    current.save(update_fields=["status", "updated_at"])
    return current
