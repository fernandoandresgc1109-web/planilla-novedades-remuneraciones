from rest_framework import permissions, viewsets

from .models import (
    AFP,
    Banco,
    Colaborador,
    Contrato,
    Exportacion,
    InstitucionSalud,
    Novedad,
    PeriodoLiquidacion,
    Sucursal,
    TipoNovedad,
)
from .serializers import (
    AFPSerializer,
    BancoSerializer,
    ColaboradorSerializer,
    ContratoSerializer,
    ExportacionSerializer,
    InstitucionSaludSerializer,
    NovedadSerializer,
    PeriodoLiquidacionSerializer,
    SucursalSerializer,
    TipoNovedadSerializer,
)


class AutenticadoModelViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)


class SucursalViewSet(AutenticadoModelViewSet):
    queryset = Sucursal.objects.all().order_by("nombre")
    serializer_class = SucursalSerializer


class BancoViewSet(AutenticadoModelViewSet):
    queryset = Banco.objects.all().order_by("nombre")
    serializer_class = BancoSerializer


class AFPViewSet(AutenticadoModelViewSet):
    queryset = AFP.objects.all().order_by("nombre")
    serializer_class = AFPSerializer


class InstitucionSaludViewSet(AutenticadoModelViewSet):
    queryset = InstitucionSalud.objects.all().order_by("nombre")
    serializer_class = InstitucionSaludSerializer


class ColaboradorViewSet(AutenticadoModelViewSet):
    queryset = (
        Colaborador.objects.select_related(
            "sucursal",
            "banco",
            "afp",
            "institucion_salud",
        )
        .all()
        .order_by("apellidos", "nombres")
    )
    serializer_class = ColaboradorSerializer


class ContratoViewSet(AutenticadoModelViewSet):
    queryset = (
        Contrato.objects.select_related("colaborador")
        .all()
        .order_by("-fecha_inicio")
    )
    serializer_class = ContratoSerializer


class PeriodoLiquidacionViewSet(AutenticadoModelViewSet):
    queryset = (
        PeriodoLiquidacion.objects.select_related("sucursal")
        .all()
        .order_by("-anio", "-mes")
    )
    serializer_class = PeriodoLiquidacionSerializer


class TipoNovedadViewSet(AutenticadoModelViewSet):
    queryset = TipoNovedad.objects.all().order_by("nombre")
    serializer_class = TipoNovedadSerializer


class NovedadViewSet(AutenticadoModelViewSet):
    queryset = (
        Novedad.objects.select_related(
            "periodo",
            "periodo__sucursal",
            "colaborador",
            "tipo_novedad",
            "creado_por",
            "validado_por",
        )
        .all()
        .order_by("-creado_en")
    )
    serializer_class = NovedadSerializer

    def perform_create(self, serializer):
        datos_auditoria = {
            "creado_por": self.request.user,
        }

        if (
            serializer.validated_data.get("estado")
            == Novedad.Estado.VALIDADA
        ):
            datos_auditoria["validado_por"] = self.request.user

        serializer.save(**datos_auditoria)

    def perform_update(self, serializer):
        estado = serializer.validated_data.get(
            "estado",
            serializer.instance.estado,
        )

        validado_por = None
        if estado == Novedad.Estado.VALIDADA:
            validado_por = self.request.user

        serializer.save(validado_por=validado_por)


class ExportacionViewSet(AutenticadoModelViewSet):
    queryset = (
        Exportacion.objects.select_related(
            "periodo",
            "periodo__sucursal",
            "generado_por",
        )
        .all()
        .order_by("-fecha_generacion")
    )
    serializer_class = ExportacionSerializer

    def perform_create(self, serializer):
        serializer.save(generado_por=self.request.user)