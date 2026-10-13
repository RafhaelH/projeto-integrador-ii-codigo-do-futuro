"""Restricted operations on explicitly proven fictitious project records."""

import json
import os
from pathlib import Path

from django.conf import settings
from django.core.management.base import CommandError
from django.db import connection


def guard_database(expected):
    if settings.AUTH_USER_MODEL != "accounts.User" or str(connection.settings_dict["NAME"]) != str(
        expected
    ):
        raise CommandError("Banco ou assinatura da aplicação diferente do projeto confirmado.")
    configured = os.environ.get("POSTGRES_DB")
    if configured and configured != expected:
        raise CommandError("O banco confirmado diverge do POSTGRES_DB deste projeto.")


def private_path(value):
    path = Path(value).resolve()
    if path.is_relative_to(settings.ROOT_DIR):
        raise CommandError("Arquivo restrito deve ficar fora do repositório.")
    if not path.parent.is_dir() or path.parent.stat().st_mode & 0o077:
        raise CommandError("Crie previamente o diretório restrito com modo 700.")
    if path.exists() and (not path.is_file() or path.stat().st_mode & 0o077):
        raise CommandError("Arquivo existente precisa ter modo 600.")
    return path


def write_private(path, value):
    # Exclusive creation prevents overwriting an archive or a credential file.
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, default=str)
        stream.flush()
        os.fsync(stream.fileno())
