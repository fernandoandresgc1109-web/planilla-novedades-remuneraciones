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
import com.planillanovedades.mobile.data.session.TokenStore
import kotlinx.coroutines.runBlocking
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test
import retrofit2.Response

class AuthRepositoryTest {
    @Test
    fun `login guarda el token y entrega el usuario`() = runBlocking {
        val tokenStore = FakeTokenStore()
        val api = FakeApiService()
        val repository = AuthRepository(api, tokenStore)

        val result = repository.login("operador", "clave-segura")

        assertTrue(result is LoginResult.Success)
        assertEquals("token-prueba", tokenStore.read())
        assertEquals("operador", api.lastLogin?.username)
    }

    @Test
    fun `restaurar sesion consulta el usuario cuando existe token`() = runBlocking {
        val tokenStore = FakeTokenStore().apply { save("token-prueba") }
        val repository = AuthRepository(FakeApiService(), tokenStore)

        val user = repository.restoreSession()

        assertEquals("operador", user?.username)
    }

    @Test
    fun `cerrar sesion elimina el token local`() = runBlocking {
        val tokenStore = FakeTokenStore().apply { save("token-prueba") }
        val repository = AuthRepository(FakeApiService(), tokenStore)

        repository.logout()

        assertNull(tokenStore.read())
    }
}

private class FakeTokenStore : TokenStore {
    private var token: String? = null

    override fun read(): String? = token

    override fun save(token: String) {
        this.token = token
    }

    override fun clear() {
        token = null
    }
}

private class FakeApiService : ApiService {
    var lastLogin: LoginRequest? = null
    private val user = UsuarioMovil(
        id = 1,
        username = "operador",
        nombre = "Operador Prueba",
        rol = "OPERADOR_SUCURSAL",
        sucursal = null,
        accesoGlobal = false,
        puedeModificar = true,
        puedeExportar = false,
    )

    override suspend fun login(request: LoginRequest): LoginResponse {
        lastLogin = request
        return LoginResponse(token = "token-prueba", usuario = user)
    }

    override suspend fun currentUser(): UsuarioResponse = UsuarioResponse(user)

    override suspend fun logout(): Response<Unit> = Response.success(Unit)

    override suspend fun colaboradores(
        page: Int,
    ): PaginatedResponse<ColaboradorMovil> = PaginatedResponse(
        count = 0,
        next = null,
        previous = null,
        results = emptyList(),
    )

    override suspend fun novedades(
        page: Int,
    ): PaginatedResponse<NovedadMovil> = PaginatedResponse(
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

    override suspend fun validarNovedad(id: Int): NovedadMovil =
        error("No utilizado en estas pruebas")

    override suspend fun anularNovedad(
        id: Int,
        request: AnularNovedadRequest,
    ): NovedadMovil = error("No utilizado en estas pruebas")
}
