import os

import dj_database_url
from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403


def required_environment(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ImproperlyConfigured(f"A variável de ambiente {name} é obrigatória.")
    return value


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
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31_536_000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]
