from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone

from apps.core.models import UUIDTimestampedModel
from apps.people.models import Institution, Instructor


class WorkshopStatus(models.TextChoices):
    DRAFT = "DRAFT", "Rascunho"
    PUBLISHED = "PUBLISHED", "Publicada"
    ARCHIVED = "ARCHIVED", "Arquivada"


class Workshop(UUIDTimestampedModel):
    title = models.CharField("nome", max_length=150)
    slug = models.SlugField("identificador", max_length=170, unique=True)
    summary = models.CharField("descrição", max_length=300)
    objective = models.TextField("objetivo")
    syllabus = models.TextField("conteúdo programático")
    estimated_hours = models.DecimalField(
        "carga horária estimada",
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
    )
    status = models.CharField(
        "situação", max_length=20, choices=WorkshopStatus.choices, default=WorkshopStatus.DRAFT
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="criada por",
        related_name="created_workshops",
        on_delete=models.PROTECT,
    )

    class Meta:
        verbose_name = "oficina"
        verbose_name_plural = "oficinas"
        ordering = ["title"]
        indexes = [models.Index(fields=["status"], name="workshops_workshop_status_idx")]

    def __str__(self) -> str:
        return self.title


class ClassGroupStatus(models.TextChoices):
    PLANNED = "PLANNED", "Planejada"
    OPEN = "OPEN", "Inscrições abertas"
    IN_PROGRESS = "IN_PROGRESS", "Em andamento"
    COMPLETED = "COMPLETED", "Concluída"
    CANCELLED = "CANCELLED", "Cancelada"


class ClassGroup(UUIDTimestampedModel):
    workshop = models.ForeignKey(
        Workshop, verbose_name="oficina", related_name="class_groups", on_delete=models.PROTECT
    )
    institution = models.ForeignKey(
        Institution,
        verbose_name="instituição parceira",
        related_name="class_groups",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    code = models.CharField("código", max_length=30, unique=True)
    title = models.CharField("título", max_length=150)
    location = models.CharField("local", max_length=255)
    capacity = models.PositiveIntegerField("capacidade", validators=[MinValueValidator(1)])
    waitlist_enabled = models.BooleanField("habilitar lista de espera", default=True)
    registration_opens_at = models.DateTimeField("início das inscrições")
    registration_closes_at = models.DateTimeField("fim das inscrições")
    start_date = models.DateField("início das atividades")
    end_date = models.DateField("fim das atividades")
    status = models.CharField(
        "situação",
        max_length=30,
        choices=ClassGroupStatus.choices,
        default=ClassGroupStatus.PLANNED,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="criada por",
        related_name="created_class_groups",
        on_delete=models.PROTECT,
    )

    class Meta:
        verbose_name = "turma"
        verbose_name_plural = "turmas"
        ordering = ["-start_date", "code"]
        constraints = [
            models.CheckConstraint(condition=Q(capacity__gt=0), name="workshops_capacity_gt_zero")
        ]
        indexes = [
            models.Index(
                fields=["workshop", "status", "start_date"], name="workshops_class_search_idx"
            )
        ]

    def clean(self) -> None:
        super().clean()
        errors = {}
        if (
            self._state.adding
            and self.workshop_id
            and self.workshop.status != WorkshopStatus.PUBLISHED
        ):
            errors["workshop"] = "Uma nova turma exige uma oficina publicada."
        if (
            self.registration_opens_at
            and self.registration_closes_at
            and self.registration_opens_at > self.registration_closes_at
        ):
            errors["registration_closes_at"] = "O fim deve ser posterior ao início das inscrições."
        if self.start_date and self.end_date and self.start_date > self.end_date:
            errors["end_date"] = "O fim deve ser igual ou posterior ao início das atividades."
        if self.start_date and self.registration_closes_at:
            closes_date = timezone.localtime(self.registration_closes_at).date()
            if self.start_date < closes_date:
                errors["start_date"] = (
                    "As atividades não podem começar antes do fim das inscrições."
                )
        if errors:
            raise ValidationError(errors)

    def __str__(self) -> str:
        return f"{self.code} — {self.title}"


class ClassInstructor(UUIDTimestampedModel):
    class_group = models.ForeignKey(
        ClassGroup, verbose_name="turma", related_name="instructor_links", on_delete=models.CASCADE
    )
    instructor = models.ForeignKey(
        Instructor, verbose_name="instrutor", related_name="class_links", on_delete=models.PROTECT
    )
    is_lead = models.BooleanField("instrutor principal", default=False)
    assigned_at = models.DateTimeField("atribuído em", auto_now_add=True)

    class Meta:
        verbose_name = "instrutor da turma"
        verbose_name_plural = "instrutores da turma"
        ordering = ["-is_lead", "instructor__user__full_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["class_group", "instructor"], name="workshops_class_instructor_unique"
            ),
            models.UniqueConstraint(
                fields=["class_group"],
                condition=Q(is_lead=True),
                name="workshops_class_lead_unique",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.class_group} — {self.instructor}"


class MeetingStatus(models.TextChoices):
    PLANNED = "PLANNED", "Planejado"
    COMPLETED = "COMPLETED", "Realizado"
    CANCELLED = "CANCELLED", "Cancelado"


class Meeting(UUIDTimestampedModel):
    class_group = models.ForeignKey(
        ClassGroup, verbose_name="turma", related_name="meetings", on_delete=models.CASCADE
    )
    title = models.CharField("tema", max_length=150)
    description = models.TextField("conteúdo e observações", blank=True)
    starts_at = models.DateTimeField("início")
    ends_at = models.DateTimeField("fim")
    status = models.CharField(
        "situação", max_length=20, choices=MeetingStatus.choices, default=MeetingStatus.PLANNED
    )

    class Meta:
        verbose_name = "encontro"
        verbose_name_plural = "encontros"
        ordering = ["starts_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["class_group", "starts_at"], name="workshops_meeting_start_unique"
            ),
            models.CheckConstraint(
                condition=Q(ends_at__gt=models.F("starts_at")),
                name="workshops_meeting_end_after_start",
            ),
        ]
        indexes = [
            models.Index(
                fields=["class_group", "status", "starts_at"],
                name="workshops_meeting_schedule_idx",
            )
        ]

    def clean(self) -> None:
        super().clean()
        errors = {}
        if self.starts_at and self.ends_at and self.ends_at <= self.starts_at:
            errors["ends_at"] = "O fim do encontro deve ser posterior ao início."
        if self.class_group_id and self.starts_at and self.ends_at:
            start = timezone.localtime(self.starts_at).date()
            end = timezone.localtime(self.ends_at).date()
            if start < self.class_group.start_date or end > self.class_group.end_date:
                errors["starts_at"] = "O encontro deve ocorrer dentro do período da turma."
        if errors:
            raise ValidationError(errors)

    def __str__(self) -> str:
        return f"{self.class_group.code} — {self.title}"
