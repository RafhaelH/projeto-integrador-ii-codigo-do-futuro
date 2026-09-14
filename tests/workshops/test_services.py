from datetime import datetime, timedelta

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.people.models import Instructor
from apps.workshops.models import (
    ClassGroupStatus,
    ClassInstructor,
    Meeting,
    MeetingStatus,
    WorkshopStatus,
)
from apps.workshops.services import cancel_meeting, transition_class_group, transition_workshop

pytestmark = pytest.mark.django_db


def test_publishes_then_archives_workshop(published_workshop):
    published_workshop.status = WorkshopStatus.DRAFT
    published_workshop.save()

    published = transition_workshop(published_workshop, WorkshopStatus.PUBLISHED)
    archived = transition_workshop(published, WorkshopStatus.ARCHIVED)

    assert archived.status == WorkshopStatus.ARCHIVED


def test_archived_workshop_cannot_transition(published_workshop):
    published_workshop.status = WorkshopStatus.ARCHIVED
    published_workshop.save()

    with pytest.raises(ValidationError, match="não permitida"):
        transition_workshop(published_workshop, WorkshopStatus.PUBLISHED)


def test_opening_class_requires_active_instructor(planned_class):
    with pytest.raises(ValidationError, match="instrutor ativo"):
        transition_class_group(planned_class, ClassGroupStatus.OPEN)


def test_class_follows_complete_lifecycle(planned_class, instructor_user):
    instructor = Instructor.objects.create(user=instructor_user)
    ClassInstructor.objects.create(class_group=planned_class, instructor=instructor, is_lead=True)
    Meeting.objects.create(
        class_group=planned_class,
        title="Lógica",
        starts_at=timezone.make_aware(datetime(2026, 10, 10, 9)),
        ends_at=timezone.make_aware(datetime(2026, 10, 10, 11)),
    )

    opened = transition_class_group(planned_class, ClassGroupStatus.OPEN)
    started = transition_class_group(opened, ClassGroupStatus.IN_PROGRESS)
    completed = transition_class_group(
        started,
        ClassGroupStatus.COMPLETED,
        academic_completion_validated=True,
    )

    assert completed.status == ClassGroupStatus.COMPLETED


def test_class_cannot_bypass_academic_completion(planned_class, instructor_user):
    instructor = Instructor.objects.create(user=instructor_user)
    ClassInstructor.objects.create(class_group=planned_class, instructor=instructor)
    planned_class.status = ClassGroupStatus.IN_PROGRESS
    planned_class.save()

    with pytest.raises(ValidationError, match="processamento acadêmico"):
        transition_class_group(planned_class, ClassGroupStatus.COMPLETED)


def test_starting_class_requires_meeting(planned_class, instructor_user):
    instructor = Instructor.objects.create(user=instructor_user)
    ClassInstructor.objects.create(class_group=planned_class, instructor=instructor)
    planned_class.status = ClassGroupStatus.OPEN
    planned_class.save()

    with pytest.raises(ValidationError, match="encontro planejado"):
        transition_class_group(planned_class, ClassGroupStatus.IN_PROGRESS)


def test_cancelling_class_cancels_only_future_meetings(planned_class):
    future = Meeting.objects.create(
        class_group=planned_class,
        title="Futuro",
        starts_at=timezone.now() + timedelta(days=30),
        ends_at=timezone.now() + timedelta(days=30, hours=2),
    )
    past = Meeting.objects.create(
        class_group=planned_class,
        title="Passado",
        starts_at=timezone.now() - timedelta(days=1),
        ends_at=timezone.now() - timedelta(days=1) + timedelta(hours=2),
    )

    transition_class_group(planned_class, ClassGroupStatus.CANCELLED)
    future.refresh_from_db()
    past.refresh_from_db()

    assert future.status == MeetingStatus.CANCELLED
    assert past.status == MeetingStatus.PLANNED


def test_cancel_meeting_preserves_record(planned_class):
    meeting = Meeting.objects.create(
        class_group=planned_class,
        title="Encontro",
        starts_at=timezone.make_aware(datetime(2026, 10, 12, 9)),
        ends_at=timezone.make_aware(datetime(2026, 10, 12, 11)),
    )

    cancel_meeting(meeting)
    meeting.refresh_from_db()

    assert meeting.status == MeetingStatus.CANCELLED
    assert Meeting.objects.filter(pk=meeting.pk).exists()
