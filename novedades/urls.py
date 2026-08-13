from django.urls import path

from . import views

app_name = "novedades"

urlpatterns = [
    path("", views.inicio, name="inicio"),
]