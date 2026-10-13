import os

import dj_database_url
from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403


def required_environment(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ImproperlyConfigured(f"A variável de ambiente {name} é obrigatória.")
    return value


def environment_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def environment_int(name: str, default: int) -> int:
    value = os.getenv(name)
    return int(value) if value else default


SECRET_KEY = required_environment("DJANGO_SECRET_KEY")
DATABASES = {
    "default": dj_database_url.parse(
        required_environment("DATABASE_URL"),
        conn_max_age=60,
        conn_health_checks=True,
    )
}
ALLOWED_HOSTS = [
    host.strip() for host in required_environment("DJANGO_ALLOWED_HOSTS").split(",") if host.strip()
]

DEBUG = False
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"
SECURE_HSTS_SECONDS = environment_int("DJANGO_SECURE_HSTS_SECONDS", 31_536_000)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]

EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend",
)
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "nao-responda@codigodofuturo.local")
EMAIL_HOST = os.getenv("EMAIL_HOST", "")
EMAIL_PORT = environment_int("EMAIL_PORT", 587)
EMAIL_USE_TLS = environment_bool("EMAIL_USE_TLS", True)
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_TIMEOUT = environment_int("EMAIL_TIMEOUT", 10)
