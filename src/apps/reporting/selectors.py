from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from django.db.models import Count, Q, QuerySet, Sum

from apps.accounts.models import User, UserRole
from apps.enrollments.models import Enrollment, EnrollmentStatus
from apps.learning.models import AttendanceStatus
from apps.workshops.models import ClassGroup, ClassGroupStatus, MeetingStatus

OCCUPIED_STATUSES = (
    EnrollmentStatus.CONFIRMED,
    EnrollmentStatus.APPROVED,
    EnrollmentStatus.NOT_COMPLETED,
)
ACADEMIC_STATUSES = OCCUPIED_STATUSES
FINAL_STATUSES = (
    EnrollmentStatus.APPROVED,
    EnrollmentStatus.NOT_COMPLETED,
)


@dataclass(frozen=True)
class StatusCount:
    value: str
    label: str
    total: int


@dataclass(frozen=True)
class DashboardSnapshot:
    classes: int
    participants: int
    enrollments: int
    capacity: int
    occupied: int
    occupancy_percentage: Decimal
    average_attendance: Decimal
    delivered_projects: int
    approved: int
    not_completed: int
    completion_percentage: Decimal
    class_statuses: tuple[StatusCount, ...]
    enrollment_statuses: tuple[StatusCount, ...]


def _percentage(numerator: int | Decimal, denominator: int | Decimal) -> Decimal:
    if not denominator:
        return Decimal("0.00")
    return (Decimal(numerator) / Decimal(denominator) * Decimal("100")).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )


def class_groups_for_user(user: User) -> QuerySet[ClassGroup]:
    queryset = ClassGroup.objects.select_related("workshop", "institution")
    if user.role == UserRole.ADMIN:
        return queryset
    if user.role == UserRole.INSTRUCTOR:
        return queryset.filter(
            instructor_links__instructor__user=user,
            instructor_links__instructor__is_active=True,
        ).distinct()
    return queryset.none()


def filter_class_groups(
    queryset: QuerySet[ClassGroup],
    *,
    filters: dict,
) -> QuerySet[ClassGroup]:
    if filters.get("period_start"):
        queryset = queryset.filter(start_date__gte=filters["period_start"])
    if filters.get("period_end"):
        queryset = queryset.filter(start_date__lte=filters["period_end"])
    if filters.get("workshop"):
        queryset = queryset.filter(workshop=filters["workshop"])
    if filters.get("class_status"):
        queryset = queryset.filter(status=filters["class_status"])
    return queryset


def class_summary_rows(queryset: QuerySet[ClassGroup]) -> QuerySet[ClassGroup]:
    return queryset.annotate(
        occupied_count=Count(
            "enrollments",
            filter=Q(enrollments__status__in=OCCUPIED_STATUSES),
            distinct=True,
        ),
        waitlisted_count=Count(
            "enrollments",
            filter=Q(enrollments__status=EnrollmentStatus.WAITLISTED),
            distinct=True,
        ),
        approved_count=Count(
            "enrollments",
            filter=Q(enrollments__status=EnrollmentStatus.APPROVED),
            distinct=True,
        ),
        not_completed_count=Count(
            "enrollments",
            filter=Q(enrollments__status=EnrollmentStatus.NOT_COMPLETED),
            distinct=True,
        ),
    ).order_by("-start_date", "code")


def dashboard_snapshot(queryset: QuerySet[ClassGroup]) -> DashboardSnapshot:
    enrollments = Enrollment.objects.filter(class_group__in=queryset)
    academic_enrollments = enrollments.filter(status__in=ACADEMIC_STATUSES)
    final_enrollments = enrollments.filter(status__in=FINAL_STATUSES)

    capacity = queryset.aggregate(total=Sum("capacity"))["total"] or 0
    occupied = academic_enrollments.count()
    approved = final_enrollments.filter(status=EnrollmentStatus.APPROVED).count()
    not_completed = final_enrollments.filter(
        status=EnrollmentStatus.NOT_COMPLETED
    ).count()

    attendance_rows = academic_enrollments.annotate(
        completed_meetings=Count(
            "class_group__meetings",
            filter=Q(class_group__meetings__status=MeetingStatus.COMPLETED),
            distinct=True,
        ),
        presents=Count(
            "attendances",
            filter=Q(
                attendances__status=AttendanceStatus.PRESENT,
                attendances__meeting__status=MeetingStatus.COMPLETED,
            ),
            distinct=True,
        ),
    ).values_list("completed_meetings", "presents")
    attendance_percentages = [
        _percentage(presents, completed_meetings)
        for completed_meetings, presents in attendance_rows
        if completed_meetings
    ]
    average_attendance = (
        (sum(attendance_percentages, start=Decimal("0.00")) / len(attendance_percentages)).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )
        if attendance_percentages
        else Decimal("0.00")
    )

    class_labels = dict(ClassGroupStatus.choices)
    class_statuses = tuple(
        StatusCount(row["status"], class_labels[row["status"]], row["total"])
        for row in queryset.values("status")
        .annotate(total=Count("pk", distinct=True))
        .order_by("status")
    )
    enrollment_labels = dict(EnrollmentStatus.choices)
    enrollment_statuses = tuple(
        StatusCount(row["status"], enrollment_labels[row["status"]], row["total"])
        for row in enrollments.values("status").annotate(total=Count("pk")).order_by("status")
    )

    return DashboardSnapshot(
        classes=queryset.count(),
        participants=enrollments.values("participant_id").distinct().count(),
        enrollments=enrollments.count(),
        capacity=capacity,
        occupied=occupied,
        occupancy_percentage=_percentage(occupied, capacity),
        average_attendance=average_attendance,
        delivered_projects=enrollments.filter(student_project__is_delivered=True)
        .distinct()
        .count(),
        approved=approved,
        not_completed=not_completed,
        completion_percentage=_percentage(approved, approved + not_completed),
        class_statuses=class_statuses,
        enrollment_statuses=enrollment_statuses,
    )
