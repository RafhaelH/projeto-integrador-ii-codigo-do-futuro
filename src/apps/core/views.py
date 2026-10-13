import logging

from django.contrib.auth.decorators import login_required
from django.db import connection
from django.db.utils import DatabaseError
from django.http import JsonResponse
from django.shortcuts import render

logger = logging.getLogger(__name__)


def health_check(request):
    return JsonResponse({"status": "ok", "service": "codigo-do-futuro"})


def readiness_check(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except DatabaseError:
        logger.warning("Falha na verificação de prontidão do banco de dados.")
        return JsonResponse(
            {"status": "unavailable", "service": "codigo-do-futuro"},
            status=503,
        )
    return JsonResponse({"status": "ready", "service": "codigo-do-futuro"})


@login_required
def home(request):
    return render(request, "core/home.html")
