import os
from datetime import datetime
from decimal import Decimal

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User, UserRole
from apps.enrollments.models import Enrollment, EnrollmentStatus, EnrollmentStatusHistory
from apps.learning.models import (
    Attendance,
    AttendanceStatus,
    Certificate,
    Evaluation,
    StudentProject,
)
from apps.people.models import (
    Guardian,
    GuardianRelationship,
    Institution,
    Instructor,
    Participant,
    ParticipantGuardian,
)
from apps.workshops.models import (
    ClassGroup,
    ClassGroupStatus,
    ClassInstructor,
    Meeting,
    MeetingStatus,
    Workshop,
    WorkshopStatus,
)

DEFAULT_DEMO_PASSWORD = "Demo@Codigo2026"
DEMO_EMAIL_SUFFIX = "@demo.codigodofuturo.local"
DEMO_PASSWORD_ENV = "DEMO_PASSWORD"


def aware(year: int, month: int, day: int, hour: int = 0) -> datetime:
    value = datetime(year, month, day, hour)
    return timezone.make_aware(value, timezone.get_current_timezone())


class DemoSeeder:
    def __init__(self, password: str) -> None:
        self.password = password
        self.users: dict[str, User] = {}
        self.participants: dict[str, Participant] = {}
        self.instructors: dict[str, Instructor] = {}
        self.workshops: dict[str, Workshop] = {}
        self.classes: dict[str, ClassGroup] = {}
        self.meetings: dict[str, Meeting] = {}
        self.enrollments: dict[str, Enrollment] = {}

    def run(self) -> dict[str, int]:
        self._seed_users()
        self._seed_people()
        institution = self._seed_institution()
        self._seed_workshops()
        self._seed_classes(institution)
        self._seed_instructor_assignments()
        self._seed_meetings()
        self._seed_enrollments()
        self._seed_attendance()
        self._seed_projects()
        self._seed_evaluations()
        self._seed_certificate()
        return self._counts()

    def _upsert_user(
        self,
        key: str,
        email: str,
        full_name: str,
        role: str,
        *,
        is_staff: bool = False,
        is_superuser: bool = False,
    ) -> None:
        user, _ = User.objects.update_or_create(
            email=email,
            defaults={
                "full_name": full_name,
                "role": role,
                "is_active": True,
                "is_staff": is_staff,
                "is_superuser": is_superuser,
            },
        )
        if not user.check_password(self.password):
            user.set_password(self.password)
            user.save(update_fields=["password", "updated_at"])
        self.users[key] = user

    def _seed_users(self) -> None:
        self._upsert_user(
            "admin",
            f"admin{DEMO_EMAIL_SUFFIX}",
            "[DEMO] Administrador",
            UserRole.ADMIN,
            is_staff=True,
            is_superuser=True,
        )
        self._upsert_user(
            "larissa",
            f"larissa.instrutora{DEMO_EMAIL_SUFFIX}",
            "[DEMO] Larissa Souza",
            UserRole.INSTRUCTOR,
        )
        self._upsert_user(
            "rafael",
            f"rafael.instrutor{DEMO_EMAIL_SUFFIX}",
            "[DEMO] Rafael Lima",
            UserRole.INSTRUCTOR,
        )
        participant_users = [
            ("ana", "ana.oliveira", "[DEMO] Ana Oliveira"),
            ("bruno", "bruno.santos", "[DEMO] Bruno Santos"),
            ("carla", "carla.mendes", "[DEMO] Carla Mendes"),
            ("diego", "diego.rocha", "[DEMO] Diego Rocha"),
            ("elisa", "elisa.martins", "[DEMO] Elisa Martins"),
            ("felipe", "felipe.costa", "[DEMO] Felipe Costa"),
        ]
        for key, address, full_name in participant_users:
            self._upsert_user(
                key,
                f"{address}{DEMO_EMAIL_SUFFIX}",
                full_name,
                UserRole.PARTICIPANT,
            )

    def _seed_people(self) -> None:
        instructor_data = {
            "larissa": {
                "biography": "Instrutora fictícia de programação e robótica educacional.",
                "specialties": "Python, lógica de programação e robótica",
            },
            "rafael": {
                "biography": "Instrutor fictício de desenvolvimento de aplicações web.",
                "specialties": "HTML, CSS, JavaScript e Django",
            },
        }
        for key, defaults in instructor_data.items():
            instructor, _ = Instructor.objects.update_or_create(
                user=self.users[key],
                defaults={**defaults, "is_active": True},
            )
            self.instructors[key] = instructor

        participant_data = {
            "ana": (datetime(2010, 2, 10).date(), True),
            "bruno": (datetime(2005, 6, 18).date(), False),
            "carla": (datetime(2009, 9, 5).date(), True),
            "diego": (datetime(2007, 11, 22).date(), False),
            "elisa": (datetime(2011, 1, 30).date(), True),
            "felipe": (datetime(2008, 4, 14).date(), False),
        }
        for key, (birth_date, image_authorization) in participant_data.items():
            user = self.users[key]
            participant, _ = Participant.objects.update_or_create(
                user=user,
                defaults={
                    "full_name": user.full_name,
                    "birth_date": birth_date,
                    "cpf": None,
                    "contact_email": user.email,
                    "phone": "",
                    "is_active": True,
                    "privacy_consent_at": aware(2026, 1, 10, 12),
                    "image_authorization": image_authorization,
                },
            )
            self.participants[key] = participant

        guardian_data = [
            ("ana", "[DEMO] Juliana Oliveira", "11911111111", GuardianRelationship.MOTHER),
            ("carla", "[DEMO] Marcos Mendes", "11922222222", GuardianRelationship.FATHER),
            (
                "elisa",
                "[DEMO] Patrícia Martins",
                "11933333333",
                GuardianRelationship.MOTHER,
            ),
        ]
        for participant_key, full_name, phone, relationship in guardian_data:
            guardian, _ = Guardian.objects.update_or_create(
                full_name=full_name,
                defaults={
                    "phone": phone,
                    "email": f"responsavel.{participant_key}{DEMO_EMAIL_SUFFIX}",
                    "is_active": True,
                },
            )
            ParticipantGuardian.objects.update_or_create(
                participant=self.participants[participant_key],
                guardian=guardian,
                defaults={"relationship": relationship, "is_primary": True},
            )

    def _seed_institution(self) -> Institution:
        institution, _ = Institution.objects.update_or_create(
            name="[DEMO] Centro Comunitário Código Aberto",
            defaults={
                "document": None,
                "contact_name": "[DEMO] Marina Alves",
                "contact_email": f"centro.comunitario{DEMO_EMAIL_SUFFIX}",
                "contact_phone": "11944444444",
                "address": "Rua dos Exemplos, 100 - São Paulo/SP",
                "is_active": True,
            },
        )
        return institution

    def _seed_workshops(self) -> None:
        data = {
            "python": {
                "title": "[DEMO] Programação com Python",
                "slug": "demo-programacao-python",
                "summary": "Fundamentos de programação por meio de desafios práticos.",
                "objective": "Desenvolver raciocínio lógico e autonomia para criar programas.",
                "syllabus": "Variáveis, decisões, repetições, funções e projeto final.",
                "estimated_hours": Decimal("8.00"),
            },
            "web": {
                "title": "[DEMO] Desenvolvimento Web",
                "slug": "demo-desenvolvimento-web",
                "summary": "Criação de páginas acessíveis e responsivas para a web.",
                "objective": "Construir uma aplicação web simples do planejamento à publicação.",
                "syllabus": "HTML semântico, CSS, JavaScript e integração com back-end.",
                "estimated_hours": Decimal("12.00"),
            },
            "robotics": {
                "title": "[DEMO] Robótica Criativa",
                "slug": "demo-robotica-criativa",
                "summary": "Introdução à robótica com experimentação em equipe.",
                "objective": "Aplicar programação na solução de desafios com sensores e atuadores.",
                "syllabus": "Circuitos, sensores, lógica de controle e desafio final.",
                "estimated_hours": Decimal("10.00"),
            },
        }
        for key, defaults in data.items():
            workshop, _ = Workshop.objects.update_or_create(
                slug=defaults["slug"],
                defaults={
                    **defaults,
                    "status": WorkshopStatus.PUBLISHED,
                    "created_by": self.users["admin"],
                },
            )
            self.workshops[key] = workshop

    def _seed_classes(self, institution: Institution) -> None:
        data = {
            "python_completed": {
                "workshop": self.workshops["python"],
                "code": "DEMO-PY-2026-01",
                "title": "[DEMO] Python - turma concluída",
                "capacity": 12,
                "registration_opens_at": aware(2026, 3, 1, 8),
                "registration_closes_at": aware(2026, 3, 20, 18),
                "start_date": datetime(2026, 4, 4).date(),
                "end_date": datetime(2026, 4, 25).date(),
                "status": ClassGroupStatus.COMPLETED,
            },
            "web_active": {
                "workshop": self.workshops["web"],
                "code": "DEMO-WEB-2026-01",
                "title": "[DEMO] Web - turma em andamento",
                "capacity": 10,
                "registration_opens_at": aware(2026, 7, 1, 8),
                "registration_closes_at": aware(2026, 8, 20, 18),
                "start_date": datetime(2026, 9, 5).date(),
                "end_date": datetime(2026, 10, 3).date(),
                "status": ClassGroupStatus.IN_PROGRESS,
            },
            "robotics_open": {
                "workshop": self.workshops["robotics"],
                "code": "DEMO-ROB-2026-01",
                "title": "[DEMO] Robótica - inscrições abertas",
                "capacity": 2,
                "registration_opens_at": aware(2026, 8, 15, 8),
                "registration_closes_at": aware(2026, 10, 5, 18),
                "start_date": datetime(2026, 10, 10).date(),
                "end_date": datetime(2026, 10, 31).date(),
                "status": ClassGroupStatus.OPEN,
            },
            "python_planned": {
                "workshop": self.workshops["python"],
                "code": "DEMO-PY-2026-02",
                "title": "[DEMO] Python - próxima turma",
                "capacity": 15,
                "registration_opens_at": aware(2026, 10, 15, 8),
                "registration_closes_at": aware(2026, 11, 5, 18),
                "start_date": datetime(2026, 11, 14).date(),
                "end_date": datetime(2026, 12, 5).date(),
                "status": ClassGroupStatus.PLANNED,
            },
        }
        for key, defaults in data.items():
            class_group, _ = ClassGroup.objects.update_or_create(
                code=defaults["code"],
                defaults={
                    **defaults,
                    "institution": institution,
                    "location": "Laboratório de Tecnologia - Sala 2",
                    "waitlist_enabled": True,
                    "created_by": self.users["admin"],
                },
            )
            self.classes[key] = class_group

    def _seed_instructor_assignments(self) -> None:
        assignments = [
            ("python_completed", "larissa", True),
            ("web_active", "rafael", True),
            ("robotics_open", "larissa", True),
            ("robotics_open", "rafael", False),
            ("python_planned", "rafael", True),
        ]
        for class_key, instructor_key, is_lead in assignments:
            ClassInstructor.objects.update_or_create(
                class_group=self.classes[class_key],
                instructor=self.instructors[instructor_key],
                defaults={"is_lead": is_lead},
            )

    def _upsert_meeting(
        self,
        key: str,
        class_key: str,
        title: str,
        start: datetime,
        end: datetime,
        status: str,
    ) -> None:
        meeting, _ = Meeting.objects.update_or_create(
            class_group=self.classes[class_key],
            starts_at=start,
            defaults={
                "title": title,
                "description": "Encontro fictício criado pela carga determinística.",
                "ends_at": end,
                "status": status,
            },
        )
        self.meetings[key] = meeting

    def _seed_meetings(self) -> None:
        meetings = [
            (
                "py1",
                "python_completed",
                "Lógica e variáveis",
                aware(2026, 4, 4, 9),
                aware(2026, 4, 4, 11),
                MeetingStatus.COMPLETED,
            ),
            (
                "py2",
                "python_completed",
                "Condições",
                aware(2026, 4, 11, 9),
                aware(2026, 4, 11, 11),
                MeetingStatus.COMPLETED,
            ),
            (
                "py3",
                "python_completed",
                "Repetições e funções",
                aware(2026, 4, 18, 9),
                aware(2026, 4, 18, 11),
                MeetingStatus.COMPLETED,
            ),
            (
                "py4",
                "python_completed",
                "Apresentação dos projetos",
                aware(2026, 4, 25, 9),
                aware(2026, 4, 25, 11),
                MeetingStatus.COMPLETED,
            ),
            (
                "web1",
                "web_active",
                "HTML semântico",
                aware(2026, 9, 5, 9),
                aware(2026, 9, 5, 12),
                MeetingStatus.COMPLETED,
            ),
            (
                "web2",
                "web_active",
                "CSS responsivo",
                aware(2026, 9, 12, 9),
                aware(2026, 9, 12, 12),
                MeetingStatus.COMPLETED,
            ),
            (
                "web3",
                "web_active",
                "JavaScript",
                aware(2026, 9, 19, 9),
                aware(2026, 9, 19, 12),
                MeetingStatus.PLANNED,
            ),
            (
                "web4",
                "web_active",
                "Integração e apresentação",
                aware(2026, 10, 3, 9),
                aware(2026, 10, 3, 12),
                MeetingStatus.PLANNED,
            ),
            (
                "rob1",
                "robotics_open",
                "Circuitos e sensores",
                aware(2026, 10, 10, 9),
                aware(2026, 10, 10, 14),
                MeetingStatus.PLANNED,
            ),
            (
                "rob2",
                "robotics_open",
                "Desafio de automação",
                aware(2026, 10, 31, 9),
                aware(2026, 10, 31, 14),
                MeetingStatus.PLANNED,
            ),
        ]
        for meeting in meetings:
            self._upsert_meeting(*meeting)

    def _upsert_enrollment(
        self,
        key: str,
        participant_key: str,
        class_key: str,
        status: str,
        *,
        reason: str = "",
        waitlisted_at: datetime | None = None,
        confirmed_at: datetime | None = None,
        cancelled_at: datetime | None = None,
    ) -> None:
        enrollment, _ = Enrollment.objects.update_or_create(
            participant=self.participants[participant_key],
            class_group=self.classes[class_key],
            defaults={
                "status": status,
                "status_reason": reason,
                "waitlisted_at": waitlisted_at,
                "confirmed_at": confirmed_at,
                "cancelled_at": cancelled_at,
                "created_by": self.users["admin"],
            },
        )
        self.enrollments[key] = enrollment

    def _seed_enrollments(self) -> None:
        self._upsert_enrollment(
            "ana_python",
            "ana",
            "python_completed",
            EnrollmentStatus.APPROVED,
            confirmed_at=aware(2026, 3, 10, 10),
        )
        self._upsert_enrollment(
            "bruno_python",
            "bruno",
            "python_completed",
            EnrollmentStatus.NOT_COMPLETED,
            reason="Frequência de 50%, abaixo do mínimo de 75%.",
            confirmed_at=aware(2026, 3, 11, 10),
        )
        self._upsert_enrollment(
            "carla_web",
            "carla",
            "web_active",
            EnrollmentStatus.CONFIRMED,
            confirmed_at=aware(2026, 7, 15, 10),
        )
        self._upsert_enrollment(
            "diego_web",
            "diego",
            "web_active",
            EnrollmentStatus.CONFIRMED,
            confirmed_at=aware(2026, 7, 16, 10),
        )
        self._upsert_enrollment(
            "felipe_web",
            "felipe",
            "web_active",
            EnrollmentStatus.CANCELLED,
            reason="Cancelamento solicitado antes do início da turma.",
            confirmed_at=aware(2026, 7, 17, 10),
            cancelled_at=aware(2026, 8, 15, 10),
        )
        self._upsert_enrollment(
            "ana_robotics",
            "ana",
            "robotics_open",
            EnrollmentStatus.CONFIRMED,
            confirmed_at=aware(2026, 8, 20, 10),
        )
        self._upsert_enrollment(
            "bruno_robotics",
            "bruno",
            "robotics_open",
            EnrollmentStatus.CONFIRMED,
            confirmed_at=aware(2026, 8, 21, 10),
        )
        self._upsert_enrollment(
            "elisa_robotics",
            "elisa",
            "robotics_open",
            EnrollmentStatus.WAITLISTED,
            waitlisted_at=aware(2026, 8, 22, 10),
        )
        self._upsert_enrollment(
            "felipe_robotics",
            "felipe",
            "robotics_open",
            EnrollmentStatus.PENDING,
        )
        history_paths = {
            "ana_python": [
                (None, EnrollmentStatus.PENDING, ""),
                (EnrollmentStatus.PENDING, EnrollmentStatus.CONFIRMED, ""),
                (EnrollmentStatus.CONFIRMED, EnrollmentStatus.APPROVED, ""),
            ],
            "bruno_python": [
                (None, EnrollmentStatus.PENDING, ""),
                (EnrollmentStatus.PENDING, EnrollmentStatus.CONFIRMED, ""),
                (
                    EnrollmentStatus.CONFIRMED,
                    EnrollmentStatus.NOT_COMPLETED,
                    "Frequência insuficiente.",
                ),
            ],
            "carla_web": [
                (None, EnrollmentStatus.PENDING, ""),
                (EnrollmentStatus.PENDING, EnrollmentStatus.CONFIRMED, ""),
            ],
            "diego_web": [
                (None, EnrollmentStatus.PENDING, ""),
                (EnrollmentStatus.PENDING, EnrollmentStatus.CONFIRMED, ""),
            ],
            "felipe_web": [
                (None, EnrollmentStatus.PENDING, ""),
                (EnrollmentStatus.PENDING, EnrollmentStatus.CONFIRMED, ""),
                (
                    EnrollmentStatus.CONFIRMED,
                    EnrollmentStatus.CANCELLED,
                    "Cancelamento solicitado.",
                ),
            ],
            "ana_robotics": [
                (None, EnrollmentStatus.PENDING, ""),
                (EnrollmentStatus.PENDING, EnrollmentStatus.CONFIRMED, ""),
            ],
            "bruno_robotics": [
                (None, EnrollmentStatus.PENDING, ""),
                (EnrollmentStatus.PENDING, EnrollmentStatus.CONFIRMED, ""),
            ],
            "elisa_robotics": [
                (None, EnrollmentStatus.PENDING, ""),
                (EnrollmentStatus.PENDING, EnrollmentStatus.WAITLISTED, "Turma lotada."),
            ],
            "felipe_robotics": [(None, EnrollmentStatus.PENDING, "")],
        }
        for enrollment_key, changes in history_paths.items():
            for from_status, to_status, reason in changes:
                EnrollmentStatusHistory.objects.get_or_create(
                    enrollment=self.enrollments[enrollment_key],
                    from_status=from_status,
                    to_status=to_status,
                    defaults={
                        "reason": reason,
                        "changed_by": self.users["admin"],
                    },
                )

    def _seed_attendance(self) -> None:
        rows = [
            ("ana_python", "py1", AttendanceStatus.PRESENT, ""),
            ("ana_python", "py2", AttendanceStatus.PRESENT, ""),
            ("ana_python", "py3", AttendanceStatus.PRESENT, ""),
            ("ana_python", "py4", AttendanceStatus.PRESENT, ""),
            ("bruno_python", "py1", AttendanceStatus.PRESENT, ""),
            ("bruno_python", "py2", AttendanceStatus.PRESENT, ""),
            ("bruno_python", "py3", AttendanceStatus.ABSENT, ""),
            (
                "bruno_python",
                "py4",
                AttendanceStatus.JUSTIFIED,
                "Atestado fictício para demonstração.",
            ),
            ("carla_web", "web1", AttendanceStatus.PRESENT, ""),
            ("carla_web", "web2", AttendanceStatus.PRESENT, ""),
            ("diego_web", "web1", AttendanceStatus.PRESENT, ""),
            ("diego_web", "web2", AttendanceStatus.ABSENT, ""),
        ]
        for enrollment_key, meeting_key, status, note in rows:
            class_key = (
                "larissa"
                if enrollment_key in {"ana_python", "bruno_python"}
                else "rafael"
            )
            Attendance.objects.update_or_create(
                enrollment=self.enrollments[enrollment_key],
                meeting=self.meetings[meeting_key],
                defaults={
                    "status": status,
                    "note": note,
                    "recorded_by": self.users[class_key],
                },
            )

    def _seed_projects(self) -> None:
        rows = {
            "ana_python": {
                "title": "Quiz de lógica",
                "description": "Jogo de perguntas criado em Python.",
                "repository_url": "https://github.com/exemplo-demo/quiz-logica",
                "demonstration_url": "",
                "is_delivered": True,
                "delivered_at": aware(2026, 4, 23, 18),
                "review_notes": "Projeto completo e bem organizado.",
            },
            "bruno_python": {
                "title": "Calculadora de estudos",
                "description": "Calculadora de metas semanais em Python.",
                "repository_url": "https://github.com/exemplo-demo/calculadora-estudos",
                "demonstration_url": "",
                "is_delivered": True,
                "delivered_at": aware(2026, 4, 24, 18),
                "review_notes": "Entrega válida; revisar nomes das funções.",
            },
            "carla_web": {
                "title": "Portal da comunidade",
                "description": "Página responsiva para divulgar atividades comunitárias.",
                "repository_url": "https://github.com/exemplo-demo/portal-comunidade",
                "demonstration_url": "https://example.com/demo-portal-comunidade",
                "is_delivered": True,
                "delivered_at": aware(2026, 9, 13, 18),
                "review_notes": "Primeira versão entregue para revisão.",
            },
            "diego_web": {
                "title": "Guia de estudos",
                "description": "Rascunho de uma página com trilhas de aprendizado.",
                "repository_url": "",
                "demonstration_url": "",
                "is_delivered": False,
                "delivered_at": None,
                "review_notes": "",
            },
        }
        for enrollment_key, defaults in rows.items():
            StudentProject.objects.update_or_create(
                enrollment=self.enrollments[enrollment_key],
                defaults=defaults,
            )

    def _seed_evaluations(self) -> None:
        rows = {
            "ana_python": (
                Decimal("9.2"),
                "Excelente domínio dos fundamentos e boa apresentação.",
                "larissa",
                aware(2026, 4, 26, 12),
            ),
            "bruno_python": (
                Decimal("7.0"),
                "Bom projeto, mas a frequência ficou abaixo do mínimo.",
                "larissa",
                aware(2026, 4, 26, 12),
            ),
            "carla_web": (
                Decimal("8.5"),
                "Boa evolução; resultado ainda não publicado.",
                "rafael",
                None,
            ),
        }
        for enrollment_key, (score, feedback, evaluator_key, published_at) in rows.items():
            Evaluation.objects.update_or_create(
                enrollment=self.enrollments[enrollment_key],
                defaults={
                    "final_score": score,
                    "feedback": feedback,
                    "evaluated_by": self.users[evaluator_key],
                    "published_at": published_at,
                },
            )

    def _seed_certificate(self) -> None:
        Certificate.objects.update_or_create(
            enrollment=self.enrollments["ana_python"],
            defaults={
                "verification_code": "CDF-DEMO-ANA-2026",
                "issued_at": aware(2026, 4, 27, 12),
                "workload_hours": Decimal("8.00"),
                "is_active": True,
                "revoked_at": None,
                "revocation_reason": "",
            },
        )

    def _counts(self) -> dict[str, int]:
        demo_users = User.objects.filter(email__endswith=DEMO_EMAIL_SUFFIX)
        demo_classes = ClassGroup.objects.filter(code__startswith="DEMO-")
        demo_enrollments = Enrollment.objects.filter(class_group__in=demo_classes)
        return {
            "users": demo_users.count(),
            "participants": Participant.objects.filter(user__in=demo_users).count(),
            "instructors": Instructor.objects.filter(user__in=demo_users).count(),
            "guardians": Guardian.objects.filter(full_name__startswith="[DEMO]").count(),
            "institutions": Institution.objects.filter(name__startswith="[DEMO]").count(),
            "workshops": Workshop.objects.filter(slug__startswith="demo-").count(),
            "classes": demo_classes.count(),
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


class Command(BaseCommand):
    help = "Cria ou atualiza uma carga fictícia e determinística para demonstração."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--allow-production",
            action="store_true",
            help="Permite a execução com DEBUG=False quando DEMO_PASSWORD estiver definida.",
        )

    @transaction.atomic
    def handle(self, *args, **options) -> None:
        allow_production = options["allow_production"]
        configured_password = os.getenv(DEMO_PASSWORD_ENV)

        if not settings.DEBUG and not allow_production:
            raise CommandError(
                "Carga bloqueada com DEBUG=False. "
                "Use --allow-production apenas em um ambiente de demonstração isolado."
            )
        if not settings.DEBUG and not configured_password:
            raise CommandError(
                f"Defina {DEMO_PASSWORD_ENV} antes de liberar a carga com DEBUG=False."
            )

        password = configured_password or DEFAULT_DEMO_PASSWORD
        counts = DemoSeeder(password).run()

        self.stdout.write(self.style.SUCCESS("Carga determinística concluída."))
        for label, count in counts.items():
            self.stdout.write(f"- {label}: {count}")
        self.stdout.write("")
        self.stdout.write(f"Administrador: admin{DEMO_EMAIL_SUFFIX}")
        self.stdout.write(f"Participante: ana.oliveira{DEMO_EMAIL_SUFFIX}")
        if configured_password:
            self.stdout.write(f"Senha: valor definido em {DEMO_PASSWORD_ENV}")
        else:
            self.stdout.write(f"Senha local: {DEFAULT_DEMO_PASSWORD}")
