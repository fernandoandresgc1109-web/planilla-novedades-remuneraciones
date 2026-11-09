package com.planillanovedades.mobile.data.model

import com.google.gson.annotations.SerializedName

data class LoginRequest(
    val username: String,
    val password: String,
)

data class LoginResponse(
    val token: String,
    val usuario: UsuarioMovil,
)

data class UsuarioResponse(
    val usuario: UsuarioMovil,
)

data class UsuarioMovil(
    val id: Int,
    val username: String,
    val nombre: String,
    val rol: String,
    val sucursal: SucursalMovil?,
    @SerializedName("acceso_global")
    val accesoGlobal: Boolean,
    @SerializedName("puede_modificar")
    val puedeModificar: Boolean,
    @SerializedName("puede_exportar")
    val puedeExportar: Boolean,
)

data class SucursalMovil(
    val id: Int,
    val codigo: String,
    val nombre: String,
)
