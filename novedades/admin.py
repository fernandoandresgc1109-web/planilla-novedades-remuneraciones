from django.contrib import admin

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


@admin.register(Sucursal)
class SucursalAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "activo")
    search_fields = ("codigo", "nombre")
    list_filter = ("activo",)
    ordering = ("nombre",)


@admin.register(Banco)
class BancoAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "activo")
    search_fields = ("codigo", "nombre")
    list_filter = ("activo",)
    ordering = ("nombre",)


@admin.register(AFP)
class AFPAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "activo")
    search_fields = ("codigo", "nombre")
    list_filter = ("activo",)
    ordering = ("nombre",)


@admin.register(InstitucionSalud)
class InstitucionSaludAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "tipo", "activo")
    search_fields = ("codigo", "nombre")
    list_filter = ("tipo", "activo")
    ordering = ("nombre",)


@admin.register(Colaborador)
class ColaboradorAdmin(admin.ModelAdmin):
    list_display = (
        "rut",
        "apellidos",
        "nombres",
        "sucursal",
        "activo",
    )
    search_fields = ("rut", "nombres", "apellidos")
    list_filter = (
        "activo",
        "sucursal",
        "afp",
        "institucion_salud",
    )
    ordering = ("apellidos", "nombres")


@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    list_display = (
        "colaborador",
        "tipo_contrato",
        "cargo",
        "fecha_inicio",
        "fecha_termino",
        "activo",
    )
    search_fields = (
        "colaborador__rut",
        "colaborador__nombres",
        "colaborador__apellidos",
        "cargo",
        "centro_costo",
    )
    list_filter = ("tipo_contrato", "activo", "fecha_inicio")
    ordering = ("-fecha_inicio",)


@admin.register(PeriodoLiquidacion)
class PeriodoLiquidacionAdmin(admin.ModelAdmin):
    list_display = (
        "sucursal",
        "anio",
        "mes",
        "estado",
        "fecha_inicio",
        "fecha_cierre",
    )
    search_fields = ("sucursal__codigo", "sucursal__nombre")
    list_filter = ("estado", "anio", "mes", "sucursal")
    ordering = ("-anio", "-mes")
    readonly_fields = ("creado_en",)


@admin.register(TipoNovedad)
class TipoNovedadAdmin(admin.ModelAdmin):
    list_display = (
        "codigo",
        "nombre",
        "unidad_medida",
        "naturaleza",
        "activo",
    )
    search_fields = ("codigo", "nombre")
    list_filter = ("unidad_medida", "naturaleza", "activo")
    ordering = ("nombre",)


@admin.register(Novedad)
class NovedadAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "periodo",
        "colaborador",
        "tipo_novedad",
        "estado",
        "creado_en",
    )
    search_fields = (
        "colaborador__rut",
        "colaborador__nombres",
        "colaborador__apellidos",
        "tipo_novedad__codigo",
        "tipo_novedad__nombre",
        "observacion",
    )
    list_filter = ("estado", "tipo_novedad", "periodo")
    ordering = ("-creado_en",)
    date_hierarchy = "creado_en"
    readonly_fields = ("creado_en", "actualizado_en")


@admin.register(Exportacion)
class ExportacionAdmin(admin.ModelAdmin):
    list_display = (
        "nombre_archivo",
        "periodo",
        "formato",
        "cantidad_registros",
        "generado_por",
        "fecha_generacion",
    )
    search_fields = ("nombre_archivo",)
    list_filter = ("formato", "periodo")
    ordering = ("-fecha_generacion",)
    date_hierarchy = "fecha_generacion"
    readonly_fields = ("fecha_generacion",)