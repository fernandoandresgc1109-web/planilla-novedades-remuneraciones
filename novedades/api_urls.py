from django.urls import path
from rest_framework.routers import DefaultRouter

from .api_auth import (
    CerrarSesionMovilAPIView,
    InicioSesionMovilAPIView,
    UsuarioActualMovilAPIView,
)
from .api_views import (
    AFPViewSet,
    BancoViewSet,
    ColaboradorViewSet,
    ContratoViewSet,
    ExportacionViewSet,
    InstitucionSaludViewSet,
    NovedadViewSet,
    PeriodoLiquidacionViewSet,
    SucursalViewSet,
    TipoNovedadViewSet,
)

app_name = "api"

router = DefaultRouter()
router.register("sucursales", SucursalViewSet, basename="sucursal")
router.register("bancos", BancoViewSet, basename="banco")
router.register("afp", AFPViewSet, basename="afp")
router.register(
    "instituciones-salud",
    InstitucionSaludViewSet,
    basename="institucion-salud",
)
router.register(
    "colaboradores",
    ColaboradorViewSet,
    basename="colaborador",
)
router.register("contratos", ContratoViewSet, basename="contrato")
router.register(
    "periodos",
    PeriodoLiquidacionViewSet,
    basename="periodo",
)
router.register(
    "tipos-novedad",
    TipoNovedadViewSet,
    basename="tipo-novedad",
)
router.register("novedades", NovedadViewSet, basename="novedad")
router.register(
    "exportaciones",
    ExportacionViewSet,
    basename="exportacion",
)

urlpatterns = [
    path(
        "autenticacion/iniciar/",
        InicioSesionMovilAPIView.as_view(),
        name="autenticacion-iniciar",
    ),
    path(
        "autenticacion/usuario/",
        UsuarioActualMovilAPIView.as_view(),
        name="autenticacion-usuario",
    ),
    path(
        "autenticacion/cerrar/",
        CerrarSesionMovilAPIView.as_view(),
        name="autenticacion-cerrar",
    ),
]
urlpatterns += router.urls
