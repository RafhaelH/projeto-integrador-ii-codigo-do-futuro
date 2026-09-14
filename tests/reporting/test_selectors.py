from decimal import Decimal

import pytest

from apps.reporting.selectors import (
    class_groups_for_user,
    dashboard_snapshot,
    filter_class_groups,
)

pytestmark = pytest.mark.django_db


def test_admin_snapshot_reconciles_indicators(
    admin_user,
    reporting_class,
    reporting_academic_data,
):
    snapshot = dashboard_snapshot(class_groups_for_user(admin_user))

    assert snapshot.classes == 1
    assert snapshot.participants == 1
    assert snapshot.enrollments == 1
    assert snapshot.capacity == 10
    assert snapshot.occupied == 1
    assert snapshot.occupancy_percentage == Decimal("10.00")
    assert snapshot.average_attendance == Decimal("100.00")
    assert snapshot.delivered_projects == 1
    assert snapshot.approved == 1
    assert snapshot.not_completed == 0
    assert snapshot.completion_percentage == Decimal("100.00")


def test_instructor_scope_contains_only_assigned_classes(
    instructor_user,
    reporting_instructor,
    reporting_class,
    unrelated_class,
):
    queryset = class_groups_for_user(instructor_user)

    assert list(queryset) == [reporting_class]
    assert unrelated_class not in queryset


def test_period_filter_uses_class_start_date(
    admin_user,
    reporting_class,
    unrelated_class,
):
    queryset = filter_class_groups(
        class_groups_for_user(admin_user),
        filters={"period_end": reporting_class.start_date},
    )

    assert list(queryset) == [reporting_class]
    assert unrelated_class not in queryset
