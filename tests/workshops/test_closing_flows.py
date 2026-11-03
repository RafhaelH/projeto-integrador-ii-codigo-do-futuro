import pytest
from django.test import Client
from django.urls import reverse

from apps.accounts.models import User
from apps.people.models import Instructor
from apps.workshops.models import ClassGroupStatus, ClassInstructor

pytestmark = pytest.mark.django_db


def test_provisioned_instructor_can_be_linked_to_class_by_nonstaff_admin(
    client, admin_user, planned_class
):
    admin_user.is_staff = False
    admin_user.save()
    client.force_login(admin_user)
    response = client.post(
        reverse("people:instructor-access-create"),
        {
            "email": "vinculo.instrutor@example.com",
            "full_name": "Instrutor fictício",
            "password1": "Acesso-ficticio!2026#Teste",
            "password2": "Acesso-ficticio!2026#Teste",
        },
    )
    assert response.status_code == 302
    user = User.objects.get(email="vinculo.instrutor@example.com")
    instructor = Instructor.objects.get(user=user)
    url = reverse("workshops:class-instructor-create", kwargs={"class_pk": planned_class.pk})
    assert client.post(url, {"instructor": instructor.pk, "is_lead": True}).status_code == 302
    assert ClassInstructor.objects.filter(class_group=planned_class, instructor=instructor).exists()


def test_cancellation_requires_readonly_confirmation_and_explicit_post(
    client, admin_user, planned_class
):
    admin_user.is_staff = False
    admin_user.save()
    client.force_login(admin_user)
    url = reverse(
        "workshops:class-transition", kwargs={"pk": planned_class.pk, "target": "cancelled"}
    )
    assert client.get(url).status_code == 200
    planned_class.refresh_from_db()
    assert planned_class.status == ClassGroupStatus.PLANNED
    assert client.post(url, {}).status_code == 200
    planned_class.refresh_from_db()
    assert planned_class.status == ClassGroupStatus.PLANNED
    assert client.post(url, {"confirmed": True}).status_code == 302
    planned_class.refresh_from_db()
    assert planned_class.status == ClassGroupStatus.CANCELLED


def test_cancellation_keeps_csrf_role_and_http_guards(admin_user, planned_class, instructor_user):
    url = reverse(
        "workshops:class-transition", kwargs={"pk": planned_class.pk, "target": "cancelled"}
    )
    c = Client(enforce_csrf_checks=True)
    c.force_login(admin_user)
    assert c.post(url, {"confirmed": True}).status_code == 403
    c.force_login(instructor_user)
    assert c.get(url).status_code == 403
    other = Client()
    other.force_login(admin_user)
    assert (
        other.get(
            reverse("workshops:class-transition", kwargs={"pk": planned_class.pk, "target": "open"})
        ).status_code
        == 405
    )
    planned_class.refresh_from_db()
    assert planned_class.status == ClassGroupStatus.PLANNED
