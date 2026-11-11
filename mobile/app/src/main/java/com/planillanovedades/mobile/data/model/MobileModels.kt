package com.planillanovedades.mobile.data.model

import com.google.gson.annotations.SerializedName

data class PaginatedResponse<T>(
    val count: Int,
    val next: String?,
    val previous: String?,
    val results: List<T>,
)

data class ColaboradorMovil(
    val id: Int,
    val rut: String,
    val nombres: String,
    val apellidos: String,
    val sucursal: Int,
    @SerializedName("sucursal_nombre")
    val sucursalNombre: String,
    val activo: Boolean,
) {
    val nombreCompleto: String
        get() = listOf(nombres, apellidos)
            .filter { it.isNotBlank() }
            .joinToString(" ")
}

data class NovedadMovil(
    val id: Int,
    val periodo: Int,
    @SerializedName("periodo_descripcion")
    val periodoDescripcion: String,
    @SerializedName("sucursal_nombre")
    val sucursalNombre: String,
    val colaborador: Int,
    @SerializedName("colaborador_nombre")
    val colaboradorNombre: String,
    @SerializedName("colaborador_rut")
    val colaboradorRut: String,
    @SerializedName("tipo_novedad")
    val tipoNovedad: Int,
    @SerializedName("tipo_novedad_nombre")
    val tipoNovedadNombre: String,
    @SerializedName("fecha_inicio")
    val fechaInicio: String?,
    @SerializedName("fecha_termino")
    val fechaTermino: String?,
    val cantidad: String?,
    val monto: String?,
    val observacion: String,
    val estado: String,
)
