package com.planillanovedades.mobile.data.repository

import com.planillanovedades.mobile.data.model.ColaboradorMovil
import com.planillanovedades.mobile.data.model.LoginRequest
import com.planillanovedades.mobile.data.model.LoginResponse
import com.planillanovedades.mobile.data.model.NovedadMovil
import com.planillanovedades.mobile.data.model.PaginatedResponse
import com.planillanovedades.mobile.data.model.UsuarioMovil
import com.planillanovedades.mobile.data.model.UsuarioResponse
import com.planillanovedades.mobile.data.remote.ApiService
import kotlinx.coroutines.runBlocking
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import retrofit2.Response

class ColaboradorRepositoryTest {
    @Test
    fun `listar recorre todas las paginas de colaboradores`() = runBlocking {
        val api = FakeColaboradoresApiService()
        val repository = ColaboradorRepository(api)

        val result = repository.listar()

        assertTrue(result is ColaboradoresResult.Success)
        result as ColaboradoresResult.Success
        assertEquals(2, result.total)
        assertEquals(2, result.colaboradores.size)
        assertEquals(listOf(1, 2), api.paginasConsultadas)
        assertEquals("Sucursal Norte", result.colaboradores.first().sucursalNombre)
    }
}

private class FakeColaboradoresApiService : ApiService {
    val paginasConsultadas = mutableListOf<Int>()

    override suspend fun colaboradores(
        page: Int,
    ): PaginatedResponse<ColaboradorMovil> {
        paginasConsultadas += page
        val colaborador = ColaboradorMovil(
            id = page,
            rut = "RUT-$page",
            nombres = "Nombre $page",
            apellidos = "Apellido $page",
            sucursal = 1,
            sucursalNombre = "Sucursal Norte",
            activo = true,
        )
        return PaginatedResponse(
            count = 2,
            next = if (page == 1) "pagina-2" else null,
            previous = if (page == 1) null else "pagina-1",
            results = listOf(colaborador),
        )
    }

    override suspend fun login(request: LoginRequest): LoginResponse =
        LoginResponse(token = "", usuario = usuarioPrueba())

    override suspend fun currentUser(): UsuarioResponse =
        UsuarioResponse(usuarioPrueba())

    override suspend fun logout(): Response<Unit> = Response.success(Unit)

    override suspend fun novedades(
        page: Int,
    ): PaginatedResponse<NovedadMovil> = PaginatedResponse(
        count = 0,
        next = null,
        previous = null,
        results = emptyList(),
    )

    private fun usuarioPrueba() = UsuarioMovil(
        id = 1,
        username = "operador",
        nombre = "Operador",
        rol = "OPERADOR_SUCURSAL",
        sucursal = null,
        accesoGlobal = false,
        puedeModificar = true,
        puedeExportar = false,
    )
}
