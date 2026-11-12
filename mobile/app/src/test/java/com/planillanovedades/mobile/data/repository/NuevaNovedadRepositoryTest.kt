package com.planillanovedades.mobile.data.repository

import com.planillanovedades.mobile.data.model.ColaboradorMovil
import com.planillanovedades.mobile.data.model.AnularNovedadRequest
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

class NuevaNovedadRepositoryTest {
    @Test
    fun `cargar opciones conserva solamente registros disponibles`() = runBlocking {
        val repository = NuevaNovedadRepository(FakeNuevaNovedadApiService())

        val result = repository.cargarOpciones()

        assertTrue(result is OpcionesNuevaNovedadResult.Success)
        result as OpcionesNuevaNovedadResult.Success
        assertEquals(listOf(1), result.periodos.map { it.id })
        assertEquals(listOf(1), result.colaboradores.map { it.id })
        assertEquals(listOf(1), result.tipos.map { it.id })
    }

    @Test
    fun `crear envia los datos y recibe borrador`() = runBlocking {
        val api = FakeNuevaNovedadApiService()
        val repository = NuevaNovedadRepository(api)
        val request = NuevaNovedadRequest(
            periodo = 1,
            colaborador = 1,
            tipoNovedad = 1,
            fechaInicio = null,
            fechaTermino = null,
            cantidad = null,
            monto = "50000",
            observacion = "Bono móvil",
        )

        val result = repository.crear(request)

        assertTrue(result is CrearNovedadResult.Success)
        result as CrearNovedadResult.Success
        assertEquals(request, api.ultimaCreacion)
        assertEquals("BORRADOR", result.novedad.estado)
    }
}

private class FakeNuevaNovedadApiService : ApiService {
    var ultimaCreacion: NuevaNovedadRequest? = null

    override suspend fun periodos(page: Int) = PaginatedResponse(
        count = 2,
        next = null,
        previous = null,
        results = listOf(
            PeriodoMovil(
                1,
                1,
                "Norte",
                2026,
                11,
                "2026-11-01",
                null,
                "ABIERTO",
            ),
            PeriodoMovil(
                2,
                1,
                "Norte",
                2026,
                10,
                "2026-10-01",
                "2026-10-31T18:00:00Z",
                "CERRADO",
            ),
        ),
    )

    override suspend fun colaboradores(page: Int) = PaginatedResponse(
        count = 2,
        next = null,
        previous = null,
        results = listOf(
            ColaboradorMovil(1, "RUT-1", "Ana", "Prueba", 1, "Norte", true),
            ColaboradorMovil(2, "RUT-2", "Luis", "Prueba", 1, "Norte", false),
        ),
    )

    override suspend fun tiposNovedad(page: Int) = PaginatedResponse(
        count = 2,
        next = null,
        previous = null,
        results = listOf(
            TipoNovedadMovil(1, "BONO", "Bono", "PESOS", "HABER", true),
            TipoNovedadMovil(2, "ANTIGUO", "Antiguo", "PESOS", "HABER", false),
        ),
    )

    override suspend fun crearNovedad(
        request: NuevaNovedadRequest,
    ): NovedadMovil {
        ultimaCreacion = request
        return NovedadMovil(
            id = 10,
            periodo = request.periodo,
            periodoDescripcion = "11/2026",
            sucursalNombre = "Norte",
            colaborador = request.colaborador,
            colaboradorNombre = "Ana Prueba",
            colaboradorRut = "RUT-1",
            tipoNovedad = request.tipoNovedad,
            tipoNovedadNombre = "Bono",
            fechaInicio = request.fechaInicio,
            fechaTermino = request.fechaTermino,
            cantidad = request.cantidad,
            monto = request.monto,
            observacion = request.observacion,
            estado = "BORRADOR",
            puedeValidar = true,
            puedeAnular = true,
        )
    }

    override suspend fun novedades(page: Int): PaginatedResponse<NovedadMovil> =
        PaginatedResponse(0, null, null, emptyList())

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
}
