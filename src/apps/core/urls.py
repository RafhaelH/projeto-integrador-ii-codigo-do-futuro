from django.urls import path

from .views import health_check, home, readiness_check

urlpatterns = [
    path("", home, name="home"),
    path("healthz/", health_check, name="health-check"),
    path("readyz/", readiness_check, name="readiness-check"),
]
