package com.planillanovedades.mobile.data.repository

import com.planillanovedades.mobile.data.model.ColaboradorMovil
import com.planillanovedades.mobile.data.remote.ApiService
import java.io.IOException
import kotlinx.coroutines.CancellationException
import retrofit2.HttpException

sealed interface ColaboradoresResult {
    data class Success(
        val colaboradores: List<ColaboradorMovil>,
        val total: Int,
    ) : ColaboradoresResult

    data class Error(val message: String) : ColaboradoresResult
}

class ColaboradorRepository(
    private val apiService: ApiService,
) {
    suspend fun listar(): ColaboradoresResult {
        return try {
            val colaboradores = mutableListOf<ColaboradorMovil>()
            var pagina = 1
            var total = 0
            var haySiguiente: Boolean

            do {
                val respuesta = apiService.colaboradores(pagina)
                total = respuesta.count
                colaboradores += respuesta.results
                haySiguiente = respuesta.next != null
                pagina += 1
            } while (haySiguiente)

            ColaboradoresResult.Success(
                colaboradores = colaboradores,
                total = total,
            )
        } catch (error: HttpException) {
            ColaboradoresResult.Error(
                if (error.code() == 401 || error.code() == 403) {
                    "La sesión no tiene permiso para consultar colaboradores."
                } else {
                    "El servidor no pudo entregar los colaboradores."
                },
            )
        } catch (_: IOException) {
            ColaboradoresResult.Error(
                "No fue posible conectarse. Revisa Internet e inténtalo nuevamente.",
            )
        } catch (error: CancellationException) {
            throw error
        } catch (_: Exception) {
            ColaboradoresResult.Error(
                "Ocurrió un error inesperado al consultar colaboradores.",
            )
        }
    }
}
