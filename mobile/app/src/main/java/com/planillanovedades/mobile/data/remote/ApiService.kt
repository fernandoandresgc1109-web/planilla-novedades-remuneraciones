package com.planillanovedades.mobile.data.remote

import com.planillanovedades.mobile.data.model.ColaboradorMovil
import com.planillanovedades.mobile.data.model.LoginRequest
import com.planillanovedades.mobile.data.model.LoginResponse
import com.planillanovedades.mobile.data.model.NovedadMovil
import com.planillanovedades.mobile.data.model.PaginatedResponse
import com.planillanovedades.mobile.data.model.UsuarioResponse
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Query

interface ApiService {
    @POST("api/autenticacion/iniciar/")
    suspend fun login(@Body request: LoginRequest): LoginResponse

    @GET("api/autenticacion/usuario/")
    suspend fun currentUser(): UsuarioResponse

    @POST("api/autenticacion/cerrar/")
    suspend fun logout(): Response<Unit>

    @GET("api/colaboradores/")
    suspend fun colaboradores(
        @Query("page") page: Int = 1,
    ): PaginatedResponse<ColaboradorMovil>

    @GET("api/novedades/")
    suspend fun novedades(
        @Query("page") page: Int = 1,
    ): PaginatedResponse<NovedadMovil>
}
