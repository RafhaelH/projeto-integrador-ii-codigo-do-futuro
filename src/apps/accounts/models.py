import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.functions import Lower

from .managers import UserManager


class UserRole(models.TextChoices):
    ADMIN = "ADMIN", "Administrador"
    INSTRUCTOR = "INSTRUCTOR", "Instrutor"
    PARTICIPANT = "PARTICIPANT", "Participante"


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None
    first_name = None
    last_name = None
    email = models.EmailField("e-mail", unique=True)
    full_name = models.CharField("nome completo", max_length=150)
    role = models.CharField(
        "perfil de acesso",
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.PARTICIPANT,
    )
    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("alterado em", auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = ["full_name"]

    class Meta:
        verbose_name = "usuário"
        verbose_name_plural = "usuários"
        ordering = ["full_name", "email"]
        constraints = [
            models.UniqueConstraint(Lower("email"), name="accounts_user_email_ci_unique")
        ]

    def save(self, *args, **kwargs):
        self.email = self.__class__.objects.normalize_email(self.email).lower()
        super().save(*args, **kwargs)

    def get_full_name(self) -> str:
        return self.full_name.strip()

    def get_short_name(self) -> str:
        return self.full_name.strip().split()[0]

    def __str__(self) -> str:
        return f"{self.full_name} <{self.email}>"
