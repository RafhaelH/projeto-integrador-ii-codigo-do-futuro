from django.urls import path

from .views import health_check, home

urlpatterns = [
    path("", home, name="home"),
    path("healthz/", health_check, name="health-check"),
]
