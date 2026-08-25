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
    path(
        "novedades/<int:pk>/editar/",
        views.editar_novedad,
        name="editar_novedad",
    ),
    path(
        "novedades/<int:pk>/validar/",
        views.validar_novedad,
        name="validar_novedad",
    ),
    path(
        "novedades/<int:pk>/anular/",
        views.anular_novedad,
        name="anular_novedad",
    ),

        path(
        "exportaciones/",
        views.exportar_novedades,
        name="exportar_novedades",
    ),
]