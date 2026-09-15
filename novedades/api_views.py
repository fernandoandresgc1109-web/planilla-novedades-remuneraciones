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
from .permisos import obtener_sucursal_usuario, puede_modificar_novedades
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



class PermisoModificacionOReadOnly(permissions.BasePermission):
    """
    Permite métodos de solo lectura (GET, HEAD, OPTIONS) a todo usuario autenticado.
    Las mutaciones (POST, PUT, PATCH, DELETE) requieren no pertenecer a Contabilidad.
    """
    message = (
        "El perfil de Contabilidad solo tiene permisos para visualizar "
        "y exportar información."
    )

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method in permissions.SAFE_METHODS:
            return True

        return puede_modificar_novedades(request.user)


class AutenticadoModelViewSet(viewsets.ModelViewSet):
    permission_classes = (
        permissions.IsAuthenticated,
        PermisoModificacionOReadOnly,
    )

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
    serializer_class = SucursalSerializer

    def get_queryset(self):
        qs = Sucursal.objects.all().order_by("nombre")
        sucursal_usuario = obtener_sucursal_usuario(self.request.user)
        if sucursal_usuario:
            return qs.filter(pk=sucursal_usuario.pk)
        return qs


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
    serializer_class = ColaboradorSerializer

    def get_queryset(self):
        qs = (
            Colaborador.objects.select_related(
                "sucursal",
                "banco",
                "afp",
                "institucion_salud",
            )
            .all()
            .order_by("apellidos", "nombres")
        )
        sucursal_usuario = obtener_sucursal_usuario(self.request.user)
        if sucursal_usuario:
            return qs.filter(sucursal=sucursal_usuario)
        return qs


class ContratoViewSet(AutenticadoModelViewSet):
    serializer_class = ContratoSerializer

    def get_queryset(self):
        qs = (
            Contrato.objects.select_related("colaborador", "colaborador__sucursal")
            .all()
            .order_by("-fecha_inicio")
        )
        sucursal_usuario = obtener_sucursal_usuario(self.request.user)
        if sucursal_usuario:
            return qs.filter(colaborador__sucursal=sucursal_usuario)
        return qs


class PeriodoLiquidacionViewSet(AutenticadoModelViewSet):
    serializer_class = PeriodoLiquidacionSerializer

    def get_queryset(self):
        qs = (
            PeriodoLiquidacion.objects.select_related("sucursal")
            .all()
            .order_by("-anio", "-mes")
        )
        sucursal_usuario = obtener_sucursal_usuario(self.request.user)
        if sucursal_usuario:
            return qs.filter(sucursal=sucursal_usuario)
        return qs


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
    serializer_class = NovedadSerializer

    def get_queryset(self):
        qs = (
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
        sucursal_usuario = obtener_sucursal_usuario(self.request.user)
        if sucursal_usuario:
            return qs.filter(periodo__sucursal=sucursal_usuario)
        return qs

    def perform_create(self, serializer):
        sucursal_usuario = obtener_sucursal_usuario(self.request.user)
        periodo = serializer.validated_data.get("periodo")
        colaborador = serializer.validated_data.get("colaborador")

        if sucursal_usuario:
            if periodo and periodo.sucursal_id != sucursal_usuario.id:
                raise ValidationError(
                    {"periodo": "No tiene permisos para registrar novedades en otra sucursal."}
                )
            if colaborador and colaborador.sucursal_id != sucursal_usuario.id:
                raise ValidationError(
                    {"colaborador": "No tiene permisos para asociar colaboradores de otra sucursal."}
                )

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
    serializer_class = ExportacionSerializer

    def get_queryset(self):
        qs = (
            Exportacion.objects.select_related(
                "periodo",
                "periodo__sucursal",
                "generado_por",
            )
            .all()
            .order_by("-fecha_generacion")
        )
        sucursal_usuario = obtener_sucursal_usuario(self.request.user)
        if sucursal_usuario:
            return qs.filter(periodo__sucursal=sucursal_usuario)
        return qs