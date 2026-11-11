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
    class Meta:
        model = PeriodoLiquidacion
        fields = (
            "id",
            "sucursal",
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

    def get_periodo_descripcion(self, obj):
        return f"{obj.periodo.mes:02d}/{obj.periodo.anio}"

    def get_colaborador_nombre(self, obj):
        return f"{obj.colaborador.nombres} {obj.colaborador.apellidos}".strip()

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
    class Meta:
        model = Exportacion
        fields = (
            "id",
            "periodo",
            "generado_por",
            "fecha_generacion",
            "formato",
            "nombre_archivo",
            "cantidad_registros",
        )
        read_only_fields = fields
