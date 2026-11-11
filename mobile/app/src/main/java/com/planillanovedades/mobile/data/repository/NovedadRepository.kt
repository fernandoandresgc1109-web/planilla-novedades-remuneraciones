package com.planillanovedades.mobile.data.repository

import com.planillanovedades.mobile.data.model.NovedadMovil
import com.planillanovedades.mobile.data.remote.ApiService
import java.io.IOException
import kotlinx.coroutines.CancellationException
import retrofit2.HttpException

sealed interface NovedadesResult {
    data class Success(
        val novedades: List<NovedadMovil>,
        val total: Int,
    ) : NovedadesResult

    data class Error(val message: String) : NovedadesResult
}

class NovedadRepository(
    private val apiService: ApiService,
) {
    suspend fun listar(): NovedadesResult {
        return try {
            val novedades = mutableListOf<NovedadMovil>()
            var pagina = 1
            var total = 0
            var haySiguiente: Boolean

            do {
                val respuesta = apiService.novedades(pagina)
                total = respuesta.count
                novedades += respuesta.results
                haySiguiente = respuesta.next != null
                pagina += 1
            } while (haySiguiente)

            NovedadesResult.Success(
                novedades = novedades,
                total = total,
            )
        } catch (error: HttpException) {
            NovedadesResult.Error(
                if (error.code() == 401 || error.code() == 403) {
                    "La sesión no tiene permiso para consultar novedades."
                } else {
                    "El servidor no pudo entregar las novedades."
                },
            )
        } catch (_: IOException) {
            NovedadesResult.Error(
                "No fue posible conectarse. Revisa Internet e inténtalo nuevamente.",
            )
        } catch (error: CancellationException) {
            throw error
        } catch (_: Exception) {
            NovedadesResult.Error(
                "Ocurrió un error inesperado al consultar novedades.",
            )
        }
    }
}
