from django.urls import path

from . import views

app_name = "novedades"

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("panel/", views.panel, name="panel"),
    path(
        "novedades/",
        views.lista_novedades,
        name="lista_novedades",
    ),
    path(
        "novedades/nueva/",
        views.crear_novedad,
        name="crear_novedad",
    ),
]