import os

from .base import *  # noqa: F403

DEBUG = os.getenv("DJANGO_DEBUG", "true").lower() == "true"
ALLOWED_HOSTS = [  # noqa: F405
    host.strip()
    for host in os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if host.strip()
]

EMAIL_BACKEND = os.getenv(  # noqa: F405
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend",
)
