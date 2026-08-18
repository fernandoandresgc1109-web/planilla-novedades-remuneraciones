from rest_framework.routers import DefaultRouter

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

urlpatterns = router.urls