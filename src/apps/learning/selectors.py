from django.db.models import QuerySet

from apps.accounts.models import User, UserRole

from .models import Certificate


def certificates_for_user(user: User) -> QuerySet[Certificate]:
    queryset = Certificate.objects.select_related(
        "enrollment__participant__user",
        "enrollment__class_group__workshop",
    )
    if user.role == UserRole.ADMIN:
        return queryset
    if user.role == UserRole.INSTRUCTOR:
        return queryset.filter(
            is_active=True,
            enrollment__class_group__instructor_links__instructor__user=user,
            enrollment__class_group__instructor_links__instructor__is_active=True,
        ).distinct()
    if user.role == UserRole.PARTICIPANT:
        return queryset.filter(
            is_active=True,
            enrollment__participant__user=user,
        )
    return queryset.none()
