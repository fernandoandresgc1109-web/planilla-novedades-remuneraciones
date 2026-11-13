from rest_framework import serializers

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


class SucursalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sucursal
        fields = (
            "id",
            "codigo",
            "nombre",
            "direccion",
            "activo",
        )
        read_only_fields = ("id",)


class BancoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banco
        fields = (
            "id",
            "codigo",
            "nombre",
            "activo",
        )
        read_only_fields = ("id",)


class AFPSerializer(serializers.ModelSerializer):
    class Meta:
        model = AFP
        fields = (
            "id",
            "codigo",
            "nombre",
            "activo",
        )
        read_only_fields = ("id",)


class InstitucionSaludSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstitucionSalud
        fields = (
            "id",
            "codigo",
            "nombre",
            "tipo",
            "activo",
        )
        read_only_fields = ("id",)


class ColaboradorSerializer(serializers.ModelSerializer):
    sucursal_nombre = serializers.CharField(
        source="sucursal.nombre",
        read_only=True,
    )

    class Meta:
        model = Colaborador
        fields = (
            "id",
            "rut",
            "nombres",
            "apellidos",
            "sucursal",
            "sucursal_nombre",
            "banco",
            "numero_cuenta",
            "tipo_cuenta",
            "afp",
            "institucion_salud",
            "cargas_familiares",
            "seguro_cesantia",
            "activo",
        )
        read_only_fields = ("id",)


class ContratoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contrato
        fields = (
            "id",
            "colaborador",
            "fecha_inicio",
            "fecha_termino",
            "tipo_contrato",
            "sueldo_base",
            "cargo",
            "centro_costo",
            "activo",
        )
        read_only_fields = ("id",)


class PeriodoLiquidacionSerializer(serializers.ModelSerializer):
    sucursal_nombre = serializers.CharField(
        source="sucursal.nombre",
        read_only=True,
    )

    class Meta:
        model = PeriodoLiquidacion
        fields = (
            "id",
            "sucursal",
            "sucursal_nombre",
            "anio",
            "mes",
            "fecha_inicio",
            "fecha_cierre",
            "estado",
            "creado_en",
        )
        read_only_fields = ("id", "creado_en")


class TipoNovedadSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoNovedad
        fields = (
            "id",
            "codigo",
            "nombre",
            "unidad_medida",
            "naturaleza",
            "activo",
        )
        read_only_fields = ("id",)


class NovedadSerializer(serializers.ModelSerializer):
    periodo_descripcion = serializers.SerializerMethodField()
    sucursal_nombre = serializers.CharField(
        source="periodo.sucursal.nombre",
        read_only=True,
    )
    colaborador_nombre = serializers.SerializerMethodField()
    colaborador_rut = serializers.CharField(
        source="colaborador.rut",
        read_only=True,
    )
    tipo_novedad_nombre = serializers.CharField(
        source="tipo_novedad.nombre",
        read_only=True,
    )
    puede_validar = serializers.BooleanField(read_only=True)
    puede_anular = serializers.BooleanField(read_only=True)

    def get_periodo_descripcion(self, obj):
        return f"{obj.periodo.mes:02d}/{obj.periodo.anio}"

    def get_colaborador_nombre(self, obj):
        return f"{obj.colaborador.nombres} {obj.colaborador.apellidos}".strip()

    def validate(self, attrs):
        instancia = getattr(self, "instance", None)
        periodo = attrs.get(
            "periodo",
            getattr(instancia, "periodo", None),
        )
        colaborador = attrs.get(
            "colaborador",
            getattr(instancia, "colaborador", None),
        )
        tipo_novedad = attrs.get(
            "tipo_novedad",
            getattr(instancia, "tipo_novedad", None),
        )
        fecha_inicio = attrs.get(
            "fecha_inicio",
            getattr(instancia, "fecha_inicio", None),
        )
        fecha_termino = attrs.get(
            "fecha_termino",
            getattr(instancia, "fecha_termino", None),
        )
        cantidad = attrs.get(
            "cantidad",
            getattr(instancia, "cantidad", None),
        )
        monto = attrs.get(
            "monto",
            getattr(instancia, "monto", None),
        )
        errores = {}

        if (
            periodo
            and periodo.estado
            != PeriodoLiquidacion.Estado.ABIERTO
        ):
            errores["periodo"] = (
                "Solo se pueden registrar novedades en períodos abiertos."
            )

        if (
            periodo
            and colaborador
            and periodo.sucursal_id != colaborador.sucursal_id
        ):
            errores["colaborador"] = (
                "El colaborador debe pertenecer a la misma sucursal del período."
            )

        if colaborador and not colaborador.activo:
            errores["colaborador"] = (
                "Solo se pueden registrar novedades para colaboradores activos."
            )

        if tipo_novedad and not tipo_novedad.activo:
            errores["tipo_novedad"] = (
                "Solo se pueden utilizar tipos de novedad activos."
            )

        if (
            fecha_inicio
            and fecha_termino
            and fecha_termino < fecha_inicio
        ):
            errores["fecha_termino"] = (
                "La fecha de término no puede ser anterior a la fecha de inicio."
            )

        if tipo_novedad:
            if (
                tipo_novedad.unidad_medida
                == TipoNovedad.UnidadMedida.PESOS
                and monto is None
            ):
                errores["monto"] = (
                    "Este tipo de novedad requiere un monto."
                )

            if (
                tipo_novedad.unidad_medida
                in {
                    TipoNovedad.UnidadMedida.DIAS,
                    TipoNovedad.UnidadMedida.MINUTOS,
                }
                and cantidad is None
            ):
                errores["cantidad"] = (
                    "Este tipo de novedad requiere una cantidad."
                )

        if errores:
            raise serializers.ValidationError(errores)

        return attrs

    class Meta:
        model = Novedad
        fields = (
            "id",
            "periodo",
            "periodo_descripcion",
            "sucursal_nombre",
            "colaborador",
            "colaborador_nombre",
            "colaborador_rut",
            "tipo_novedad",
            "tipo_novedad_nombre",
            "fecha_inicio",
            "fecha_termino",
            "cantidad",
            "monto",
            "observacion",
            "estado",
            "puede_validar",
            "puede_anular",
            "creado_por",
            "validado_por",
            "validado_en",
            "anulado_por",
            "anulado_en",
            "motivo_anulacion",
            "creado_en",
            "actualizado_en",
        )
        read_only_fields = (
            "id",
            "estado",
            "creado_por",
            "validado_por",
            "validado_en",
            "anulado_por",
            "anulado_en",
            "motivo_anulacion",
            "creado_en",
            "actualizado_en",
        )


class ExportacionSerializer(serializers.ModelSerializer):
    periodo_descripcion = serializers.SerializerMethodField()
    sucursal_nombre = serializers.CharField(
        source="periodo.sucursal.nombre",
        read_only=True,
    )
    generado_por_nombre = serializers.SerializerMethodField()

    def get_periodo_descripcion(self, obj):
        return f"{obj.periodo.mes:02d}/{obj.periodo.anio}"

    def get_generado_por_nombre(self, obj):
        nombre = obj.generado_por.get_full_name().strip()
        return nombre or obj.generado_por.get_username()

    class Meta:
        model = Exportacion
        fields = (
            "id",
            "periodo",
            "periodo_descripcion",
            "sucursal_nombre",
            "generado_por",
            "generado_por_nombre",
            "fecha_generacion",
            "formato",
            "nombre_archivo",
            "cantidad_registros",
        )
        read_only_fields = fields
