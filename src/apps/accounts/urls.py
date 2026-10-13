from django.urls import path

from .views import OwnProfileView

app_name = "accounts"

urlpatterns = [path("perfil/", OwnProfileView.as_view(), name="profile")]
