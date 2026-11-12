package com.planillanovedades.mobile.data.repository

import com.planillanovedades.mobile.data.model.NovedadMovil
import com.planillanovedades.mobile.data.model.AnularNovedadRequest
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

sealed interface AccionNovedadResult {
    data class Success(val novedad: NovedadMovil) : AccionNovedadResult
    data class Error(val message: String) : AccionNovedadResult
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

    suspend fun validar(id: Int): AccionNovedadResult = ejecutarAccion {
        apiService.validarNovedad(id)
    }

    suspend fun anular(
        id: Int,
        motivo: String,
    ): AccionNovedadResult = ejecutarAccion {
        apiService.anularNovedad(
            id,
            AnularNovedadRequest(motivoAnulacion = motivo.trim()),
        )
    }

    private suspend fun ejecutarAccion(
        accion: suspend () -> NovedadMovil,
    ): AccionNovedadResult {
        return try {
            AccionNovedadResult.Success(accion())
        } catch (error: HttpException) {
            AccionNovedadResult.Error(
                when (error.code()) {
                    400 -> "La novedad cambió o no cumple las condiciones para esta acción."
                    401, 403 -> "Tu sesión no tiene permiso para modificar esta novedad."
                    404 -> "La novedad ya no está disponible."
                    else -> "El servidor no pudo actualizar la novedad."
                },
            )
        } catch (_: IOException) {
            AccionNovedadResult.Error(
                "No fue posible conectarse. Revisa Internet e inténtalo nuevamente.",
            )
        } catch (error: CancellationException) {
            throw error
        } catch (_: Exception) {
            AccionNovedadResult.Error(
                "Ocurrió un error inesperado al actualizar la novedad.",
            )
        }
    }
}
