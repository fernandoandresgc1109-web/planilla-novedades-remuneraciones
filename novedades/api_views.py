from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

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

class CatalogoAutenticadoModelViewSet(
    AutenticadoModelViewSet
):
    http_method_names = [
        "get",
        "post",
        "put",
        "patch",
        "head",
        "options",
    ]

class AutenticadoReadOnlyModelViewSet(
    viewsets.ReadOnlyModelViewSet
):
    permission_classes = (permissions.IsAuthenticated,)

class SucursalViewSet(CatalogoAutenticadoModelViewSet):
    queryset = Sucursal.objects.all().order_by("nombre")
    serializer_class = SucursalSerializer


class BancoViewSet(CatalogoAutenticadoModelViewSet):
    queryset = Banco.objects.all().order_by("nombre")
    serializer_class = BancoSerializer


class AFPViewSet(CatalogoAutenticadoModelViewSet):
    queryset = AFP.objects.all().order_by("nombre")
    serializer_class = AFPSerializer


class InstitucionSaludViewSet(
    CatalogoAutenticadoModelViewSet
):
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


class TipoNovedadViewSet(
    CatalogoAutenticadoModelViewSet
):
    queryset = TipoNovedad.objects.all().order_by("nombre")
    serializer_class = TipoNovedadSerializer


class NovedadViewSet(AutenticadoModelViewSet):
    http_method_names = [
        "get",
        "post",
        "put",
        "patch",
        "head",
        "options",
    ]
    queryset = (
        Novedad.objects.select_related(
            "periodo",
            "periodo__sucursal",
            "colaborador",
            "tipo_novedad",
            "creado_por",
            "validado_por",
            "anulado_por",
        )
        .all()
        .order_by("-creado_en")
    )
    serializer_class = NovedadSerializer

    def perform_create(self, serializer):
        serializer.save(
            creado_por=self.request.user,
            estado=Novedad.Estado.BORRADOR,
        )

    def perform_update(self, serializer):
        if not serializer.instance.puede_editar:
            raise ValidationError(
                {
                    "detail": (
                        "Solo se pueden editar novedades en borrador "
                        "pertenecientes a un período abierto."
                    )
                }
            )

        serializer.save()

    @action(detail=True, methods=["post"])
    def validar(self, request, pk=None):
        novedad = self.get_object()

        try:
            novedad.validar(request.user)
        except DjangoValidationError as error:
            if hasattr(error, "message_dict"):
                detalle = error.message_dict
            else:
                detalle = {"detail": error.messages}

            return Response(
                detalle,
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(self.get_serializer(novedad).data)


    @action(detail=True, methods=["post"])
    def anular(self, request, pk=None):
        novedad = self.get_object()
        motivo = request.data.get("motivo_anulacion", "")

        try:
            novedad.anular(request.user, motivo)
        except DjangoValidationError as error:
            if hasattr(error, "message_dict"):
                detalle = error.message_dict
            else:
                detalle = {"detail": error.messages}

            return Response(
                detalle,
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(self.get_serializer(novedad).data)




class ExportacionViewSet(
    AutenticadoReadOnlyModelViewSet
):
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