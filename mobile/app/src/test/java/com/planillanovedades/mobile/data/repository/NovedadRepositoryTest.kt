package com.planillanovedades.mobile.data.repository

import com.planillanovedades.mobile.data.model.ColaboradorMovil
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

class NovedadRepositoryTest {
    @Test
    fun `listar recorre todas las paginas de novedades`() = runBlocking {
        val api = FakeNovedadesApiService()
        val repository = NovedadRepository(api)

        val result = repository.listar()

        assertTrue(result is NovedadesResult.Success)
        result as NovedadesResult.Success
        assertEquals(2, result.total)
        assertEquals(2, result.novedades.size)
        assertEquals(listOf(1, 2), api.paginasConsultadas)
        assertEquals(
            "Bono de producción",
            result.novedades.first().tipoNovedadNombre,
        )
    }
}

private class FakeNovedadesApiService : ApiService {
    val paginasConsultadas = mutableListOf<Int>()

    override suspend fun novedades(
        page: Int,
    ): PaginatedResponse<NovedadMovil> {
        paginasConsultadas += page
        val novedad = NovedadMovil(
            id = page,
            periodo = 1,
            periodoDescripcion = "11/2026",
            sucursalNombre = "Sucursal Norte",
            colaborador = page,
            colaboradorNombre = "Persona $page",
            colaboradorRut = "RUT-$page",
            tipoNovedad = 1,
            tipoNovedadNombre = "Bono de producción",
            fechaInicio = null,
            fechaTermino = null,
            cantidad = null,
            monto = "45000.00",
            observacion = "Prueba móvil",
            estado = "BORRADOR",
        )
        return PaginatedResponse(
            count = 2,
            next = if (page == 1) "pagina-2" else null,
            previous = if (page == 1) null else "pagina-1",
            results = listOf(novedad),
        )
    }

    override suspend fun colaboradores(
        page: Int,
    ): PaginatedResponse<ColaboradorMovil> = PaginatedResponse(
        count = 0,
        next = null,
        previous = null,
        results = emptyList(),
    )

    override suspend fun periodos(
        page: Int,
    ): PaginatedResponse<PeriodoMovil> = PaginatedResponse(
        count = 0,
        next = null,
        previous = null,
        results = emptyList(),
    )

    override suspend fun tiposNovedad(
        page: Int,
    ): PaginatedResponse<TipoNovedadMovil> = PaginatedResponse(
        count = 0,
        next = null,
        previous = null,
        results = emptyList(),
    )

    override suspend fun crearNovedad(
        request: NuevaNovedadRequest,
    ): NovedadMovil = error("No utilizado en estas pruebas")

    override suspend fun login(request: LoginRequest): LoginResponse =
        LoginResponse(token = "", usuario = usuarioPrueba())

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
}
