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
