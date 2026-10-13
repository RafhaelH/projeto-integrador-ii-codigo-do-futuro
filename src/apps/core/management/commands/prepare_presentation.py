"""Prepare this project's proven demo once, retaining IDs and evaluator work thereafter."""

import hashlib
import json
import secrets
import uuid
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User, UserRole
from apps.core.presentation import guard_database, private_path, write_private
from apps.enrollments.models import Enrollment
from apps.enrollments.services import confirm_enrollment, create_enrollment
from apps.learning.models import AttendanceStatus
from apps.learning.services import (
    complete_class_group,
    issue_certificate,
    record_meeting_attendance,
    save_evaluation,
    save_student_project,
)
from apps.people.models import Instructor, Participant
from apps.workshops.models import ClassGroup, ClassGroupStatus, ClassInstructor, Meeting
from apps.workshops.services import transition_class_group

NAMESPACE = uuid.UUID("09c00c39-86c2-45cd-a880-bfb181f8c675")


def stable_id(key):
    return uuid.uuid5(NAMESPACE, key)


def moment(day, hour=12):
    return timezone.make_aware(datetime.combine(day, time(hour)))


class Presentation:
    def __init__(self, manifest, reference, credentials):
        self.manifest = manifest
        self.reference = reference
        self.credentials = credentials
        self.created = {}
        self.workspaces = {}

    def remember(self, obj):
        self.created.setdefault(obj._meta.label, []).append(str(obj.pk))
        return obj

    def create(self, model, key, **fields):
        pk = stable_id(key)
        if model.objects.filter(pk=pk).exists():
            raise CommandError("ID reservado já ocupado sem registro de preparação; nada alterado.")
        return self.remember(model.objects.create(pk=pk, **fields))

    def account(self, alias, role, name):
        password = secrets.token_urlsafe(24)
        email = f"{alias.lower()}@example.com"
        if User.objects.filter(email__iexact=email).exists():
            raise CommandError("E-mail reservado já pertence a um registro; nada alterado.")
        user = self.create(User, "user:" + alias, email=email, full_name=name, role=role)
        user.set_password(password)
        user.save(update_fields=["password", "updated_at"])
        self.credentials[alias] = {"email": email, "password": password, "user_id": str(user.pk)}
        return user

    def normalize_original(self):
        users = self.manifest["users"]
        for address, pk in users.items():
            if str(pk) == self.manifest["operational_admin"]:
                continue
            user = User.objects.get(pk=pk)
            name = user.full_name.removeprefix("[DEMO] ")
            if address == "larissa.instrutora":
                name = "Larissa Almeida"
            user.full_name = name
            user.email = address + "@example.com"
            user.full_clean()
            user.save(update_fields=["full_name", "email", "updated_at"])
        for label in [
            "people.Participant",
            "people.Guardian",
            "people.Institution",
            "workshops.Workshop",
            "workshops.ClassGroup",
        ]:
            for obj in apps.get_model(label).objects.filter(pk__in=self.manifest["records"][label]):
                fields = []
                for field in ["full_name", "name", "title", "contact_name"]:
                    if hasattr(obj, field):
                        setattr(obj, field, getattr(obj, field).removeprefix("[DEMO] "))
                        fields.append(field)
                for field in ["contact_email", "email"]:
                    if hasattr(obj, field) and getattr(obj, field):
                        setattr(obj, field, getattr(obj, field).split("@")[0] + "@example.com")
                        fields.append(field)
                for field in ["phone", "contact_phone"]:
                    if hasattr(obj, field):
                        # Guardian requires 10/11 digits. DDD 00 is deliberately non-dialable.
                        setattr(obj, field, "00000000000" if label == "people.Guardian" else "")
                        fields.append(field)
                if hasattr(obj, "code"):
                    obj.code = obj.code.removeprefix("DEMO-")
                    fields.append("code")
                if label == "people.Participant":
                    obj.contact_email = obj.user.email
                obj.full_clean()
                obj.save(update_fields=[*fields, "updated_at"])
        original_classes = apps.get_model("workshops.ClassGroup").objects.filter(
            pk__in=self.manifest["records"]["workshops.ClassGroup"]
        )
        for group in original_classes:
            if group.code.startswith("ROB-"):
                group.registration_opens_at = moment(self.reference - timedelta(days=14), 8)
                group.registration_closes_at = moment(self.reference + timedelta(days=21), 18)
                group.start_date = self.reference + timedelta(days=28)
                group.end_date = self.reference + timedelta(days=49)
                group.full_clean()
                group.save()
                for index, meeting in enumerate(group.meetings.order_by("starts_at")):
                    meeting.starts_at = moment(group.start_date + timedelta(days=21 * index), 9)
                    meeting.ends_at = meeting.starts_at + timedelta(hours=5)
                    meeting.full_clean()
                    meeting.save()
            elif group.code == "WEB-2026-01":
                # Keep completed September encounters and their attendance unchanged.
                group.end_date = self.reference + timedelta(days=18)
                group.full_clean()
                group.save()
                future = list(group.meetings.filter(status="PLANNED").order_by("starts_at"))
                for index, meeting in enumerate(future):
                    meeting.starts_at = moment(self.reference + timedelta(days=4 + 14 * index), 9)
                    meeting.ends_at = meeting.starts_at + timedelta(hours=3)
                    meeting.full_clean()
                    meeting.save()
        for project in apps.get_model("learning.StudentProject").objects.filter(
            pk__in=self.manifest["records"]["learning.StudentProject"]
        ):
            if project.repository_url:
                project.repository_url = "https://example.com/projetos/" + str(project.pk)
                project.save(update_fields=["repository_url", "updated_at"])

    def student(self, alias, name, user=None):
        user = user or self.account("aluno-" + alias, UserRole.PARTICIPANT, name)
        return self.create(
            Participant,
            "participant:" + alias,
            user=user,
            full_name=name,
            birth_date=date(2007, 2, 15),
            contact_email=user.email,
            privacy_consent_at=moment(self.reference - timedelta(days=60)),
        )

    def group(
        self,
        alias,
        workshop,
        instructor,
        actor,
        participant,
        *,
        completed=False,
        opened=False,
        delivered=True,
        attendance=True,
        evaluated=True,
    ):
        ref = self.reference
        start = ref + timedelta(days=7) if opened else ref - timedelta(days=7)
        close = ref + timedelta(days=3) if opened else ref - timedelta(days=14)
        creation_day = ref - timedelta(days=21)
        with patch("django.utils.timezone.now", return_value=moment(creation_day)):
            group = self.create(
                ClassGroup,
                "class:" + alias,
                workshop=workshop,
                institution_id=self.manifest["records"]["people.Institution"][0],
                code="PY-2026-" + alias,
                title="Prática de programação — " + alias,
                location="Laboratório do Centro Comunitário",
                capacity=2,
                registration_opens_at=moment(ref - timedelta(days=30), 8),
                registration_closes_at=moment(close, 18),
                start_date=start,
                end_date=(ref - timedelta(days=1))
                if completed or alias in {"A01", "A02"}
                else start + timedelta(days=21),
                created_by=actor,
            )
            group.full_clean()
            self.create(
                ClassInstructor,
                "assignment:" + alias,
                class_group=group,
                instructor=instructor,
                is_lead=True,
            )
            meeting = self.create(
                Meeting,
                "meeting:" + alias,
                class_group=group,
                title="Lógica e desafios",
                starts_at=moment(start, 9),
                ends_at=moment(start, 11),
                description="Encontro fictício para a sessão " + alias + ".",
            )
            meeting.full_clean()
            group = transition_class_group(group, ClassGroupStatus.OPEN)
            if not opened:
                enrollment = self.remember(
                    create_enrollment(participant=participant, class_group=group, actor=actor)
                )
                enrollment = confirm_enrollment(enrollment, actor=actor)
        self.workspaces[alias] = {
            "class_id": str(group.pk),
            "code": group.code,
            "participant_id": str(participant.pk),
            "meeting_id": str(meeting.pk),
        }
        if opened:
            return group
        with patch("django.utils.timezone.now", return_value=moment(start, 8)):
            group = transition_class_group(group, ClassGroupStatus.IN_PROGRESS)
        enrollment.class_group = group
        self.workspaces[alias]["enrollment_id"] = str(enrollment.pk)
        with patch("django.utils.timezone.now", return_value=moment(ref - timedelta(days=1), 14)):
            if attendance:
                for record in record_meeting_attendance(
                    meeting,
                    records={str(enrollment.pk): {"status": AttendanceStatus.PRESENT}},
                    actor=instructor.user,
                ):
                    self.remember(record)
            project = self.remember(
                save_student_project(
                    enrollment,
                    data={
                        "title": "Mapa de estudos",
                        "description": "Projeto fictício de lógica.",
                        "is_delivered": delivered,
                    },
                    actor=participant.user,
                )
            )
            self.workspaces[alias]["project_id"] = str(project.pk)
            if evaluated:
                self.remember(
                    save_evaluation(
                        enrollment,
                        final_score=Decimal("8.0"),
                        feedback="Aplicação correta dos fundamentos.",
                        publish=True,
                        actor=instructor.user,
                    )
                )
        if completed:
            with patch(
                "django.utils.timezone.now", return_value=moment(ref - timedelta(days=1), 16)
            ):
                complete_class_group(group, actor=actor)
                certificate = self.remember(issue_certificate(enrollment, actor=actor))
                certificate.issued_at = moment(ref - timedelta(days=1), 16)
                certificate.save(update_fields=["issued_at", "updated_at"])
                self.workspaces[alias]["certificate_id"] = str(certificate.pk)
        return group

    def run(self):
        self.normalize_original()
        admin = self.account("captura-admin", UserRole.ADMIN, "Administração da apresentação")
        # Select the proven existing Python workshop by ID, never by visible name after preparation.
        workshop = next(
            w
            for w in apps.get_model("workshops.Workshop").objects.filter(
                pk__in=self.manifest["records"]["workshops.Workshop"]
            )
            if w.slug == "demo-programacao-python"
        )
        instructor = Instructor.objects.get(user_id=self.manifest["users"]["rafael.instrutor"])
        for alias, name in [("A01", "Gabriela Nunes"), ("A02", "Hugo Ferreira")]:
            actor = self.account(alias, UserRole.ADMIN, "Acesso de avaliação " + alias)
            participant = self.student(alias, name)
            self.group(alias, workshop, instructor, actor, participant)
        for alias, name in [("A03", "Isabela Ribeiro"), ("A04", "João Teixeira")]:
            actor = self.account(alias, UserRole.INSTRUCTOR, "Acesso de avaliação " + alias)
            own_instructor = self.create(
                Instructor,
                "instructor:" + alias,
                user=actor,
                biography="Perfil fictício de acesso à avaliação.",
            )
            participant = self.student(alias, name)
            self.group(
                alias,
                workshop,
                own_instructor,
                admin,
                participant,
                attendance=False,
                evaluated=False,
            )
        actor = self.account("A05", UserRole.PARTICIPANT, "Acesso de avaliação A05")
        participant = self.student("A05", "Marina Costa", actor)
        self.group(
            "A05", workshop, instructor, admin, participant, delivered=False, evaluated=False
        )
        self.group("A05-F", workshop, instructor, admin, participant, completed=True)
        self.group("A05-I", workshop, instructor, admin, participant, opened=True)
        for alias, key in [
            ("captura-instrutor", "rafael.instrutor"),
            ("captura-participante", "ana.oliveira"),
            ("captura-projeto", "carla.mendes"),
        ]:
            user = User.objects.get(pk=self.manifest["users"][key])
            password = secrets.token_urlsafe(24)
            user.set_password(password)
            user.save(update_fields=["password", "updated_at"])
            self.credentials[alias] = {
                "email": user.email,
                "password": password,
                "user_id": str(user.pk),
            }
        # Include canonical-service-generated status history in the stable ownership ledger.
        history = apps.get_model("enrollments.EnrollmentStatusHistory")
        self.created[history._meta.label] = list(
            map(
                str,
                history.objects.filter(
                    enrollment_id__in=self.created[Enrollment._meta.label]
                ).values_list("pk", flat=True),
            )
        )


class Command(BaseCommand):
    help = "Organiza a demonstração comprovada; prepara A01–A05 sem repetir nem restaurar tarefas."

    def add_arguments(self, parser):
        parser.add_argument("--manifest", required=True)
        parser.add_argument("--confirm-database", required=True)
        parser.add_argument("--credentials-file", required=True)
        parser.add_argument("--state-file", required=True)
        parser.add_argument("--reference-date", required=True)
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        guard_database(options["confirm_database"])
        credentials_path = private_path(options["credentials_file"])
        state_path = private_path(options["state_file"])
        raw = Path(options["manifest"]).read_bytes()
        manifest = json.loads(raw)
        origin_hash = hashlib.sha256(raw).hexdigest()
        if manifest.get("database") != options["confirm_database"]:
            raise CommandError("Manifest não pertence ao banco confirmado.")
        reference = date.fromisoformat(options["reference_date"])
        if state_path.exists():
            state = json.loads(state_path.read_text())
            if state.get("manifest_sha256") != origin_hash or state.get("reference_date") != str(
                reference
            ):
                raise CommandError(
                    "Preparação anterior usa outro manifest ou data; preserve as sessões."
                )
            if not credentials_path.exists():
                raise CommandError(
                    "Preparação existe; restaure as credenciais restritas, sem redefinir senhas."
                )
            for label, ids in state["created"].items():
                if apps.get_model(label).objects.filter(pk__in=ids).count() != len(ids):
                    raise CommandError(
                        "Dados de sessão removidos; investigar sem recriar automaticamente."
                    )
            self.stdout.write("Preparação já registrada; nenhuma alteração ou senha redefinida.")
            return
        if credentials_path.exists():
            raise CommandError(
                "Arquivo de credenciais já existe sem estado; investigar sem sobrescrever."
            )
        with transaction.atomic():
            owned = {label: set(ids) for label, ids in manifest["records"].items()}
            for label, ids in owned.items():
                rows = list(apps.get_model(label).objects.select_for_update().filter(pk__in=ids))
                if len(rows) != len(ids):
                    raise CommandError("Um ID da demonstração comprovada está ausente.")
                for row in rows:
                    expected = manifest["relations"][label][str(row.pk)]
                    if any(
                        (str(getattr(row, field)) if getattr(row, field) is not None else None)
                        != value
                        for field, value in expected.items()
                    ):
                        raise CommandError(
                            "Relações do registro divergiram da proveniência; nada alterado."
                        )
            # Incoming external references make renaming shared fixture records ambiguous.
            from apps.core.management.commands.archive_validation import reviewed_plan

            _, ambiguous = reviewed_plan(owned)
            if ambiguous:
                raise CommandError(
                    "Demonstração possui vínculos externos; preserve e revise a origem."
                )
            if options["dry_run"]:
                self.stdout.write(
                    json.dumps(
                        {
                            "dry_run": True,
                            "reference_date": str(reference),
                            "original_records": {k: len(v) for k, v in owned.items()},
                            "managed_ids": {k: sorted(v) for k, v in owned.items()},
                            "changes": {
                                "names": "Remover [DEMO]; preservar administrador operacional.",
                                "contacts": "example.com; opcionais vazios; DDD 00 inválido.",
                                "codes": ["PY-2026-01", "PY-2026-02", "WEB-2026-01", "ROB-2026-01"],
                                "robotics_registration_end": str(reference + timedelta(days=21)),
                                "robotics_period": [
                                    str(reference + timedelta(days=28)),
                                    str(reference + timedelta(days=49)),
                                ],
                                "web_future_meetings": [
                                    str(reference + timedelta(days=4)),
                                    str(reference + timedelta(days=18)),
                                ],
                                "new_workspace_codes": [
                                    "PY-2026-" + a
                                    for a in ["A01", "A02", "A03", "A04", "A05", "A05-F", "A05-I"]
                                ],
                                "academic_states": "Preservados; sem reset de conclusão.",
                            },
                            "planned": (
                                "Nomes naturais; datas futuras Web/Robótica; "
                                "5 acessos, 7 turmas exclusivas; 4 acessos de captura."
                            ),
                            "operational_admin_preserved": True,
                        },
                        ensure_ascii=False,
                        indent=2,
                    )
                )
                return
            credentials = {}
            preparer = Presentation(manifest, reference, credentials)
            preparer.run()
            state = {
                "database": options["confirm_database"],
                "manifest_sha256": origin_hash,
                "reference_date": str(reference),
                "created": preparer.created,
                "workspaces": preparer.workspaces,
            }
            try:
                write_private(credentials_path, credentials)
                write_private(state_path, state)
            except Exception:
                # Only remove this invocation's exclusive files; DB transaction rolls back.
                if credentials_path.exists():
                    credentials_path.unlink()
                raise
            self.stdout.write(
                json.dumps(
                    {
                        "prepared": True,
                        "reference_date": str(reference),
                        "created_counts": {k: len(v) for k, v in preparer.created.items()},
                        "workspaces": preparer.workspaces,
                        "operational_admin_preserved": True,
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
