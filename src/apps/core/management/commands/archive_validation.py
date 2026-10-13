"""Archive and remove only explicit, reviewed IDs from fictitious validation manifests."""

import hashlib
import json

from django.apps import apps
from django.contrib.sessions.models import Session
from django.core import serializers
from django.core.management.base import BaseCommand, CommandError
from django.db import models, transaction
from django.db.models.deletion import Collector

from apps.core.presentation import guard_database, private_path, write_private

ORDER = (
    "learning.Certificate",
    "learning.Attendance",
    "learning.Evaluation",
    "learning.StudentProject",
    "enrollments.EnrollmentStatusHistory",
    "enrollments.Enrollment",
    "workshops.Meeting",
    "workshops.ClassInstructor",
    "people.ParticipantGuardian",
    "workshops.ClassGroup",
    "workshops.Workshop",
    "people.Participant",
    "people.Guardian",
    "people.Instructor",
    "people.Institution",
    "admin.LogEntry",
    "accounts.User",
)


def reviewed_plan(requested):
    """Keep targets of any incoming relation whose source is not owned; repeat to stability."""
    planned = {
        label: set(
            map(str, apps.get_model(label).objects.filter(pk__in=ids).values_list("pk", flat=True))
        )
        for label, ids in requested.items()
    }
    preserved = []
    changed = True
    while changed:
        changed = False
        for source in apps.get_models(include_auto_created=True):
            for field in source._meta.fields:
                if not isinstance(field, models.ForeignKey):
                    continue
                target = field.remote_field.model._meta.label
                if target not in planned or not planned[target]:
                    continue
                foreign = source.objects.filter(**{field.attname + "__in": planned[target]})
                foreign = foreign.exclude(pk__in=planned.get(source._meta.label, set()))
                blocked = set(map(str, foreign.values_list(field.attname, flat=True)))
                if blocked:
                    planned[target] -= blocked
                    preserved.append(
                        {
                            "model": target,
                            "ids": sorted(blocked),
                            "relation": field.name,
                            "external_model": source._meta.label,
                        }
                    )
                    changed = True
    return planned, preserved


class Command(BaseCommand):
    help = "Arquiva IDs comprovados e revisa cascatas; simulação é o padrão."

    def add_arguments(self, parser):
        parser.add_argument("--manifest", action="append", required=True)
        parser.add_argument("--confirm-database", required=True)
        parser.add_argument("--archive", required=True)
        parser.add_argument("--apply", action="store_true")

    def handle(self, *args, **options):
        guard_database(options["confirm_database"])
        archive = private_path(options["archive"])
        if archive.exists():
            raise CommandError("Escolha um arquivo novo para preservar arquivos anteriores.")
        requested = {label: set() for label in ORDER}
        manifests = []
        for filename in options["manifest"]:
            from pathlib import Path

            raw = Path(filename).read_bytes()
            manifest = json.loads(raw)
            if set(manifest) - set(ORDER):
                raise CommandError("Manifest contém modelos fora do domínio autorizado.")
            for label, ids in manifest.items():
                requested[label].update(map(str, ids))
            manifests.append({"path": filename, "sha256": hashlib.sha256(raw).hexdigest()})
        with transaction.atomic():
            for label, ids in requested.items():
                list(apps.get_model(label).objects.select_for_update().filter(pk__in=ids))
            planned, preserved = reviewed_plan(requested)
            sessions = [
                s
                for s in Session.objects.select_for_update().all()
                if s.get_decoded().get("_auth_user_id") in planned["accounts.User"]
            ]
            counts = {k: len(v) for k, v in planned.items()}
            report = {
                "database": options["confirm_database"],
                "manifests": manifests,
                "counts": counts,
                "technical_sessions": len(sessions),
                "preserved_ambiguous": preserved,
                "apply_requested": options["apply"],
                "applied": False,
            }
            if options["apply"]:
                objects = [
                    obj
                    for label in ORDER
                    for obj in apps.get_model(label).objects.filter(pk__in=planned[label])
                ] + sessions
                # Restrict raw records (including password hashes/session keys) to mode 600.
                write_private(
                    archive,
                    {
                        "review": report,
                        "objects": json.loads(serializers.serialize("json", objects)),
                    },
                )
                archive_hash = hashlib.sha256(archive.read_bytes()).hexdigest()
                write_private(
                    archive.with_suffix(archive.suffix + ".sha256.json"), {"sha256": archive_hash}
                )
                deleted = {}
                for label in ORDER:
                    model = apps.get_model(label)
                    query = model.objects.filter(pk__in=planned[label])
                    collector = Collector(using="default")
                    collector.collect(query)
                    for collected_model, rows in collector.data.items():
                        if {str(r.pk) for r in rows} - planned.get(
                            collected_model._meta.label, set()
                        ):
                            raise CommandError(
                                "Cascata alcançaria registros externos; transação revertida."
                            )
                    for fast_query in collector.fast_deletes:
                        if set(map(str, fast_query.values_list("pk", flat=True))) - planned.get(
                            fast_query.model._meta.label, set()
                        ):
                            raise CommandError("Cascata rápida externa; transação revertida.")
                    number, _ = collector.delete()
                    deleted[label] = number
                Session.objects.filter(pk__in=[s.pk for s in sessions]).delete()
                report["deleted"] = deleted
                report["archive_sha256"] = archive_hash
                report["applied"] = True
        self.stdout.write(json.dumps(report, ensure_ascii=False, indent=2))
