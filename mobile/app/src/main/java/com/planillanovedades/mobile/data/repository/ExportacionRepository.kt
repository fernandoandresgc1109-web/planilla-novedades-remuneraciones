package com.planillanovedades.mobile.data.repository

import com.planillanovedades.mobile.data.model.ExportacionMovil
import com.planillanovedades.mobile.data.remote.ApiService
import java.io.IOException
import kotlinx.coroutines.CancellationException
import retrofit2.HttpException

sealed interface ExportacionesResult {
    data class Success(
        val exportaciones: List<ExportacionMovil>,
        val total: Int,
    ) : ExportacionesResult

    data class Error(val message: String) : ExportacionesResult
}

class ExportacionRepository(
    private val apiService: ApiService,
) {
    suspend fun listar(): ExportacionesResult {
        return try {
            val exportaciones = mutableListOf<ExportacionMovil>()
            var pagina = 1
            var total = 0
            var haySiguiente: Boolean

            do {
                val respuesta = apiService.exportaciones(pagina)
                total = respuesta.count
                exportaciones += respuesta.results
                haySiguiente = respuesta.next != null
                pagina += 1
            } while (haySiguiente)

            ExportacionesResult.Success(
                exportaciones = exportaciones,
                total = total,
            )
        } catch (error: HttpException) {
            ExportacionesResult.Error(
                if (error.code() == 401 || error.code() == 403) {
                    "La sesión no tiene permiso para consultar exportaciones."
                } else {
                    "El servidor no pudo entregar las exportaciones."
                },
            )
        } catch (_: IOException) {
            ExportacionesResult.Error(
                "No fue posible conectarse. Revisa Internet e inténtalo nuevamente.",
            )
        } catch (error: CancellationException) {
            throw error
        } catch (_: Exception) {
            ExportacionesResult.Error(
                "Ocurrió un error inesperado al consultar exportaciones.",
            )
        }
    }
}
