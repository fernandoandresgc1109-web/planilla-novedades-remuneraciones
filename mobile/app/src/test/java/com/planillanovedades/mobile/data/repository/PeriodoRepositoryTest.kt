package com.planillanovedades.mobile.data.repository

import com.planillanovedades.mobile.data.model.AnularNovedadRequest
import com.planillanovedades.mobile.data.model.ColaboradorMovil
import com.planillanovedades.mobile.data.model.ExportacionMovil
import com.planillanovedades.mobile.data.model.LoginRequest
import com.planillanovedades.mobile.data.model.LoginResponse
import com.planillanovedades.mobile.data.model.NovedadMovil
import com.planillanovedades.mobile.data.model.NuevaNovedadRequest
import com.planillanovedades.mobile.data.model.PaginatedResponse
import com.planillanovedades.mobile.data.model.PeriodoMovil
import com.planillanovedades.mobile.data.model.TipoNovedadMovil
import com.planillanovedades.mobile.data.model.UsuarioMovil
import com.planillanovedades.mobile.data.model.UsuarioResponse
import com.planillanovedades.mobile.data.remote.ApiService
import kotlinx.coroutines.runBlocking
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import retrofit2.Response

class PeriodoRepositoryTest {
    @Test
    fun `listar recorre todas las paginas de periodos`() = runBlocking {
        val api = FakePeriodosApiService()
        val repository = PeriodoRepository(api)

        val result = repository.listar()

        assertTrue(result is PeriodosResult.Success)
        result as PeriodosResult.Success
        assertEquals(2, result.total)
        assertEquals(2, result.periodos.size)
        assertEquals(listOf(1, 2), api.paginasConsultadas)
        assertEquals("Sucursal Norte", result.periodos.first().sucursalNombre)
        assertEquals("ABIERTO", result.periodos.first().estado)
        assertEquals("Diciembre", result.periodos.first().nombreMes)
        assertEquals(
            "2026-11-30",
            result.periodos.last().fechaCierreLegible,
        )
    }
}

private class FakePeriodosApiService : ApiService {
    val paginasConsultadas = mutableListOf<Int>()

    override suspend fun periodos(
        page: Int,
    ): PaginatedResponse<PeriodoMovil> {
        paginasConsultadas += page
        val periodo = PeriodoMovil(
            id = page,
            sucursal = 1,
            sucursalNombre = "Sucursal Norte",
            anio = 2026,
            mes = 13 - page,
            fechaInicio = "2026-${(13 - page).toString().padStart(2, '0')}-01",
            fechaCierre = if (page == 1) null else "2026-11-30T18:00:00Z",
            estado = if (page == 1) "ABIERTO" else "CERRADO",
        )
        return PaginatedResponse(
            count = 2,
            next = if (page == 1) "pagina-2" else null,
            previous = if (page == 1) null else "pagina-1",
            results = listOf(periodo),
        )
    }

    override suspend fun colaboradores(
        page: Int,
    ): PaginatedResponse<ColaboradorMovil> = emptyResponse()

    override suspend fun novedades(
        page: Int,
    ): PaginatedResponse<NovedadMovil> = emptyResponse()

    override suspend fun tiposNovedad(
        page: Int,
    ): PaginatedResponse<TipoNovedadMovil> = emptyResponse()

    override suspend fun exportaciones(
        page: Int,
    ): PaginatedResponse<ExportacionMovil> = emptyResponse()

    override suspend fun crearNovedad(
        request: NuevaNovedadRequest,
    ): NovedadMovil = error("No utilizado en estas pruebas")

    override suspend fun validarNovedad(id: Int): NovedadMovil =
        error("No utilizado en estas pruebas")

    override suspend fun anularNovedad(
        id: Int,
        request: AnularNovedadRequest,
    ): NovedadMovil = error("No utilizado en estas pruebas")

    override suspend fun login(request: LoginRequest): LoginResponse =
        LoginResponse("", usuarioPrueba())

    override suspend fun currentUser(): UsuarioResponse =
        UsuarioResponse(usuarioPrueba())

    override suspend fun logout(): Response<Unit> = Response.success(Unit)

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

    private fun <T> emptyResponse(): PaginatedResponse<T> = PaginatedResponse(
        count = 0,
        next = null,
        previous = null,
        results = emptyList(),
    )
}
