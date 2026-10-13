import json
from io import StringIO

import pytest
from django.apps import apps
from django.contrib.sessions.backends.db import SessionStore
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import connection
from django.test import override_settings

from apps.accounts.models import User, UserRole
from apps.core.management.commands.archive_validation import ORDER
from apps.core.management.commands.prepare_presentation import stable_id
from apps.enrollments.models import Enrollment
from apps.learning.models import Certificate
from apps.learning.services import calculate_attendance_summary, complete_class_group
from apps.people.models import Participant
from apps.workshops.models import ClassGroup, Workshop

pytestmark = pytest.mark.django_db


@pytest.fixture
def fixture_manifest(tmp_path):
    tmp_path.chmod(0o700)
    with override_settings(DEBUG=True):
        call_command("seed_demo", stdout=StringIO())
    records = {label: list(apps.get_model(label).objects.all()) for label in ORDER}
    admin = User.objects.get(email="admin@demo.codigodofuturo.local")
    manifest = {
        "database": str(connection.settings_dict["NAME"]),
        "operational_admin": str(admin.pk),
        "users": {u.email.split("@")[0]: str(u.pk) for u in User.objects.all()},
        "records": {label: [str(r.pk) for r in rows] for label, rows in records.items()},
        "relations": {
            label: {
                str(r.pk): {
                    f.attname: str(getattr(r, f.attname))
                    if getattr(r, f.attname) is not None
                    else None
                    for f in r._meta.fields
                    if f.attname.endswith("_id")
                }
                for r in rows
            }
            for label, rows in records.items()
        },
    }
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest))
    return {
        "manifest": str(path),
        "confirm_database": manifest["database"],
        "credentials_file": str(tmp_path / "credentials.json"),
        "state_file": str(tmp_path / "state.json"),
        "reference_date": "2026-10-13",
    }


def prepare(options, **extra):
    output = StringIO()
    call_command("prepare_presentation", **options, **extra, stdout=output)
    return output.getvalue()


def test_presentation_dry_run_does_not_change_rows_or_write_credentials(fixture_manifest):
    before = {label: list(apps.get_model(label).objects.order_by("pk").values()) for label in ORDER}
    assert json.loads(prepare(fixture_manifest, dry_run=True))["dry_run"]
    assert before == {
        label: list(apps.get_model(label).objects.order_by("pk").values()) for label in ORDER
    }

    from pathlib import Path

    assert not Path(fixture_manifest["credentials_file"]).exists()


def test_presentation_canonical_completion_credentials_and_replay(fixture_manifest, monkeypatch):
    from pathlib import Path

    import apps.core.management.commands.prepare_presentation as command

    calls = []
    canonical = command.complete_class_group

    def observed(*args, **kwargs):
        calls.append(str(args[0].pk))
        return canonical(*args, **kwargs)

    monkeypatch.setattr(command, "complete_class_group", observed)
    admin = User.objects.get(email="admin@demo.codigodofuturo.local")
    original = (admin.password, admin.full_name, admin.is_staff, admin.is_superuser)
    output = json.loads(prepare(fixture_manifest))
    assert output["prepared"] and calls == [str(stable_id("class:A05-F"))]
    admin.refresh_from_db()
    assert original == (admin.password, admin.full_name, admin.is_staff, admin.is_superuser)
    assert Participant.objects.count() == 11
    assert Workshop.objects.count() == 3
    assert ClassGroup.objects.count() == 11
    assert Certificate.objects.count() == 2
    robotics = ClassGroup.objects.get(code="ROB-2026-01")
    for registration in robotics.enrollments.all():
        for timestamp in [registration.confirmed_at, registration.waitlisted_at]:
            if timestamp:
                assert robotics.registration_opens_at <= timestamp
                assert timestamp <= robotics.registration_closes_at
    credentials = json.loads(Path(fixture_manifest["credentials_file"]).read_text())
    assert len({v["password"] for v in credentials.values()}) == 13
    for alias in ["A01", "A02", "A03", "A04", "A05"]:
        user = User.objects.get(pk=credentials[alias]["user_id"])
        assert user.check_password(credentials[alias]["password"])
        assert not user.is_staff and not user.is_superuser
        assert (
            user.role
            == {
                "A01": UserRole.ADMIN,
                "A02": UserRole.ADMIN,
                "A03": UserRole.INSTRUCTOR,
                "A04": UserRole.INSTRUCTOR,
                "A05": UserRole.PARTICIPANT,
            }[alias]
        )
    assert Path(fixture_manifest["credentials_file"]).stat().st_mode & 0o077 == 0
    enrollment = Enrollment.objects.get(class_group_id=stable_id("class:A05-F"))
    assert enrollment.status == "APPROVED"
    assert calculate_attendance_summary(enrollment).percentage == 100
    assert enrollment.certificate.workload_hours == 2
    assert enrollment.class_group.end_date.isoformat() == "2026-10-12"
    with pytest.raises(CommandError, match="Apresentação já preparada"):
        call_command("seed_demo", allow_production=True)
    group = ClassGroup.objects.get(pk=stable_id("class:A01"))
    complete_class_group(group, actor=User.objects.get(pk=stable_id("user:A01")))
    before = {label: list(apps.get_model(label).objects.order_by("pk").values()) for label in ORDER}
    assert "nenhuma alteração" in prepare(fixture_manifest)
    assert before == {
        label: list(apps.get_model(label).objects.order_by("pk").values()) for label in ORDER
    }


def test_presentation_rejects_wrong_database(fixture_manifest):
    options = dict(fixture_manifest, confirm_database="other_project")
    with pytest.raises(CommandError, match="Banco"):
        prepare(options)


def test_presentation_refuses_external_dependencies(fixture_manifest):
    instructor = User.objects.get(email="rafael.instrutor@demo.codigodofuturo.local")
    Workshop.objects.create(
        title="Existing operational workshop",
        slug="external",
        created_by=instructor,
        estimated_hours=1,
    )
    with pytest.raises(CommandError, match="vínculos externos"):
        prepare(fixture_manifest)
    assert User.objects.count() == 9


def test_presentation_rolls_back_reserved_id_collision(fixture_manifest):
    User.objects.create_user(
        id=stable_id("user:A02"),
        email="external@example.com",
        full_name="External record",
        role=UserRole.PARTICIPANT,
    )
    ana = User.objects.get(email="ana.oliveira@demo.codigodofuturo.local")
    with pytest.raises(CommandError, match="ID reservado"):
        prepare(fixture_manifest)
    ana.refresh_from_db()
    assert ana.full_name == "[DEMO] Ana Oliveira"
    assert ClassGroup.objects.count() == 4


def test_presentation_refuses_changed_relations(fixture_manifest):
    Participant.objects.filter(full_name="[DEMO] Ana Oliveira").update(user=None)
    with pytest.raises(CommandError, match="Relações"):
        prepare(fixture_manifest)


def test_presentation_replay_refuses_different_reference_date(fixture_manifest):
    prepare(fixture_manifest)
    with pytest.raises(CommandError, match="outro manifest ou data"):
        prepare(dict(fixture_manifest, reference_date="2026-11-01"))


def test_archive_removes_only_explicit_ids_and_sessions(tmp_path, admin_user):
    tmp_path.chmod(0o700)
    technical = User.objects.create_user(
        email="technical@example.com", full_name="Fictitious", role=UserRole.ADMIN
    )
    unknown = User.objects.create_user(
        email="unknown@example.com", full_name="Fictitious", role=UserRole.ADMIN
    )
    for user in [technical, unknown]:
        session = SessionStore()
        session["_auth_user_id"] = str(user.pk)
        session.save()
    manifest = tmp_path / "ids.json"
    manifest.write_text(json.dumps({"accounts.User": [str(technical.pk)]}))
    options = {
        "manifest": [str(manifest)],
        "confirm_database": str(connection.settings_dict["NAME"]),
        "archive": str(tmp_path / "archive.json"),
    }
    output = StringIO()
    call_command("archive_validation", **options, stdout=output)
    assert not json.loads(output.getvalue())["applied"]
    assert not (tmp_path / "archive.json").exists()
    output = StringIO()
    call_command("archive_validation", **options, apply=True, stdout=output)
    report = json.loads(output.getvalue())
    assert report["deleted"]["accounts.User"] == 1
    assert report["technical_sessions"] == 1
    assert not User.objects.filter(pk=technical.pk).exists()
    assert (
        User.objects.filter(pk=unknown.pk).exists()
        and User.objects.filter(pk=admin_user.pk).exists()
    )
    archive = json.loads((tmp_path / "archive.json").read_text())
    assert {r["model"] for r in archive["objects"]} == {"accounts.user", "sessions.session"}
    assert (tmp_path / "archive.json").stat().st_mode & 0o077 == 0


def test_archive_preserves_incoming_unknown_relation(tmp_path, admin_user):
    tmp_path.chmod(0o700)
    Workshop.objects.create(
        title="External", slug="external", created_by=admin_user, estimated_hours=1
    )
    manifest = tmp_path / "ids.json"
    manifest.write_text(json.dumps({"accounts.User": [str(admin_user.pk)]}))
    output = StringIO()
    call_command(
        "archive_validation",
        manifest=[str(manifest)],
        confirm_database=str(connection.settings_dict["NAME"]),
        archive=str(tmp_path / "archive.json"),
        apply=True,
        stdout=output,
    )
    report = json.loads(output.getvalue())
    assert report["preserved_ambiguous"]
    assert report["deleted"]["accounts.User"] == 0
    assert User.objects.filter(pk=admin_user.pk).exists()


def test_archive_rejects_out_of_domain_manifest(tmp_path):
    tmp_path.chmod(0o700)
    manifest = tmp_path / "ids.json"
    manifest.write_text(json.dumps({"auth.Permission": [1]}))
    with pytest.raises(CommandError, match="fora do domínio"):
        call_command(
            "archive_validation",
            manifest=[str(manifest)],
            confirm_database=str(connection.settings_dict["NAME"]),
            archive=str(tmp_path / "archive.json"),
            apply=True,
        )
