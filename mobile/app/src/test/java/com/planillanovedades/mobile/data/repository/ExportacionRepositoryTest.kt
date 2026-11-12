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

class ExportacionRepositoryTest {
    @Test
    fun `listar recorre todas las paginas de exportaciones`() = runBlocking {
        val api = FakeExportacionesApiService()
        val repository = ExportacionRepository(api)

        val result = repository.listar()

        assertTrue(result is ExportacionesResult.Success)
        result as ExportacionesResult.Success
        assertEquals(2, result.total)
        assertEquals(2, result.exportaciones.size)
        assertEquals(listOf(1, 2), api.paginasConsultadas)
        assertEquals("XLSX", result.exportaciones.first().formato)
        assertEquals(
            "Sucursal Norte",
            result.exportaciones.first().sucursalNombre,
        )
    }
}

private class FakeExportacionesApiService : ApiService {
    val paginasConsultadas = mutableListOf<Int>()

    override suspend fun exportaciones(
        page: Int,
    ): PaginatedResponse<ExportacionMovil> {
        paginasConsultadas += page
        val exportacion = ExportacionMovil(
            id = page,
            periodo = 1,
            periodoDescripcion = "11/2026",
            sucursalNombre = "Sucursal Norte",
            generadoPor = 1,
            generadoPorNombre = "Usuario Prueba",
            fechaGeneracion = "2026-11-12T18:00:00Z",
            formato = if (page == 1) "XLSX" else "CSV",
            nombreArchivo = "exportacion-prueba-$page.xlsx",
            cantidadRegistros = 8,
        )
        return PaginatedResponse(
            count = 2,
            next = if (page == 1) "pagina-2" else null,
            previous = if (page == 1) null else "pagina-1",
            results = listOf(exportacion),
        )
    }

    override suspend fun colaboradores(
        page: Int,
    ): PaginatedResponse<ColaboradorMovil> = emptyResponse()

    override suspend fun novedades(
        page: Int,
    ): PaginatedResponse<NovedadMovil> = emptyResponse()

    override suspend fun periodos(
        page: Int,
    ): PaginatedResponse<PeriodoMovil> = emptyResponse()

    override suspend fun tiposNovedad(
        page: Int,
    ): PaginatedResponse<TipoNovedadMovil> = emptyResponse()

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
        puedeExportar = true,
    )

    private fun <T> emptyResponse(): PaginatedResponse<T> = PaginatedResponse(
        count = 0,
        next = null,
        previous = null,
        results = emptyList(),
    )
}
