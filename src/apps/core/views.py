from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render


def health_check(request):
    return JsonResponse({"status": "ok", "service": "codigo-do-futuro"})


@login_required
def home(request):
    return render(request, "core/home.html")
