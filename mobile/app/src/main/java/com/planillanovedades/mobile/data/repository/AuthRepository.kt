package com.planillanovedades.mobile.data.repository

import com.planillanovedades.mobile.data.model.LoginRequest
import com.planillanovedades.mobile.data.model.UsuarioMovil
import com.planillanovedades.mobile.data.remote.ApiService
import com.planillanovedades.mobile.data.session.TokenStore
import java.io.IOException
import kotlinx.coroutines.CancellationException
import retrofit2.HttpException

sealed interface LoginResult {
    data class Success(val user: UsuarioMovil) : LoginResult
    data class Error(val message: String) : LoginResult
}

class AuthRepository(
    private val apiService: ApiService,
    private val tokenStore: TokenStore,
) {
    suspend fun restoreSession(): UsuarioMovil? {
        if (tokenStore.read().isNullOrBlank()) return null

        return try {
            apiService.currentUser().usuario
        } catch (error: CancellationException) {
            throw error
        } catch (_: Exception) {
            tokenStore.clear()
            null
        }
    }

    suspend fun login(username: String, password: String): LoginResult {
        return try {
            val response = apiService.login(
                LoginRequest(username = username.trim(), password = password),
            )
            tokenStore.save(response.token)
            LoginResult.Success(response.usuario)
        } catch (error: HttpException) {
            LoginResult.Error(
                if (error.code() == 400 || error.code() == 401) {
                    "El usuario o la contraseña no son correctos."
                } else {
                    "El servidor no pudo completar el inicio de sesión."
                },
            )
        } catch (_: IOException) {
            LoginResult.Error(
                "No fue posible conectarse. Revisa Internet e inténtalo nuevamente.",
            )
        } catch (error: CancellationException) {
            throw error
        } catch (_: Exception) {
            LoginResult.Error("Ocurrió un error inesperado al iniciar sesión.")
        }
    }

    suspend fun logout() {
        try {
            apiService.logout()
        } finally {
            tokenStore.clear()
        }
    }
}
