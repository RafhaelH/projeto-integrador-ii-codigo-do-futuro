from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import override_settings

from apps.accounts.models import User
from apps.core.management.commands.seed_demo import (
    DEFAULT_DEMO_PASSWORD,
    DEMO_EMAIL_SUFFIX,
)
from apps.enrollments.models import Enrollment, EnrollmentStatus, EnrollmentStatusHistory
from apps.learning.models import Attendance, Certificate, Evaluation, StudentProject
from apps.people.models import Guardian, Institution, Instructor, Participant, ParticipantGuardian
from apps.workshops.models import ClassGroup, ClassInstructor, Meeting, Workshop

pytestmark = pytest.mark.django_db


def demo_counts() -> dict[str, int]:
    demo_users = User.objects.filter(email__endswith=DEMO_EMAIL_SUFFIX)
    demo_classes = ClassGroup.objects.filter(code__startswith="DEMO-")
    demo_enrollments = Enrollment.objects.filter(class_group__in=demo_classes)
    return {
        "users": demo_users.count(),
        "participants": Participant.objects.filter(user__in=demo_users).count(),
        "instructors": Instructor.objects.filter(user__in=demo_users).count(),
        "guardians": Guardian.objects.filter(full_name__startswith="[DEMO]").count(),
        "guardian_links": ParticipantGuardian.objects.filter(
            participant__user__in=demo_users
        ).count(),
        "institutions": Institution.objects.filter(name__startswith="[DEMO]").count(),
        "workshops": Workshop.objects.filter(slug__startswith="demo-").count(),
        "classes": demo_classes.count(),
        "instructor_links": ClassInstructor.objects.filter(
            class_group__in=demo_classes
        ).count(),
        "meetings": Meeting.objects.filter(class_group__in=demo_classes).count(),
        "enrollments": demo_enrollments.count(),
        "histories": EnrollmentStatusHistory.objects.filter(
            enrollment__in=demo_enrollments
        ).count(),
        "attendances": Attendance.objects.filter(enrollment__in=demo_enrollments).count(),
        "projects": StudentProject.objects.filter(enrollment__in=demo_enrollments).count(),
        "evaluations": Evaluation.objects.filter(enrollment__in=demo_enrollments).count(),
        "certificates": Certificate.objects.filter(enrollment__in=demo_enrollments).count(),
    }


@override_settings(DEBUG=True)
def test_seed_demo_creates_complete_dataset():
    output = StringIO()

    call_command("seed_demo", stdout=output)

    assert demo_counts() == {
        "users": 9,
        "participants": 6,
        "instructors": 2,
        "guardians": 3,
        "guardian_links": 3,
        "institutions": 1,
        "workshops": 3,
        "classes": 4,
        "instructor_links": 5,
        "meetings": 10,
        "enrollments": 9,
        "histories": 20,
        "attendances": 12,
        "projects": 4,
        "evaluations": 3,
        "certificates": 1,
    }
    assert "Carga determinística concluída." in output.getvalue()


@override_settings(DEBUG=True)
def test_seed_demo_is_idempotent():
    call_command("seed_demo")
    first_counts = demo_counts()

    call_command("seed_demo")

    assert demo_counts() == first_counts


@override_settings(DEBUG=True)
def test_seed_demo_creates_working_credentials():
    call_command("seed_demo")

    admin = User.objects.get(email=f"admin{DEMO_EMAIL_SUFFIX}")
    participant = User.objects.get(email=f"ana.oliveira{DEMO_EMAIL_SUFFIX}")

    assert admin.is_staff is True
    assert admin.is_superuser is True
    assert admin.check_password(DEFAULT_DEMO_PASSWORD)
    assert participant.check_password(DEFAULT_DEMO_PASSWORD)


@override_settings(DEBUG=True)
def test_seed_demo_preserves_existing_user(admin_user):
    original_name = admin_user.full_name
    original_password = admin_user.password

    call_command("seed_demo")
    admin_user.refresh_from_db()

    assert admin_user.full_name == original_name
    assert admin_user.password == original_password


@override_settings(DEBUG=True)
def test_seed_demo_covers_relevant_enrollment_statuses():
    call_command("seed_demo")

    statuses = set(
        Enrollment.objects.filter(class_group__code__startswith="DEMO-").values_list(
            "status", flat=True
        )
    )

    assert statuses == {
        EnrollmentStatus.PENDING,
        EnrollmentStatus.CONFIRMED,
        EnrollmentStatus.WAITLISTED,
        EnrollmentStatus.CANCELLED,
        EnrollmentStatus.APPROVED,
        EnrollmentStatus.NOT_COMPLETED,
    }


@override_settings(DEBUG=False)
def test_seed_demo_is_blocked_outside_debug():
    with pytest.raises(CommandError, match="DEBUG=False"):
        call_command("seed_demo")


@override_settings(DEBUG=False)
def test_seed_demo_requires_environment_password_when_released(monkeypatch):
    monkeypatch.delenv("DEMO_PASSWORD", raising=False)

    with pytest.raises(CommandError, match="DEMO_PASSWORD"):
        call_command("seed_demo", allow_production=True)
