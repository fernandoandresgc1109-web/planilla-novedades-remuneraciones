package com.planillanovedades.mobile.data.repository

import com.planillanovedades.mobile.data.model.PeriodoMovil
import com.planillanovedades.mobile.data.remote.ApiService
import java.io.IOException
import kotlinx.coroutines.CancellationException
import retrofit2.HttpException

sealed interface PeriodosResult {
    data class Success(
        val periodos: List<PeriodoMovil>,
        val total: Int,
    ) : PeriodosResult

    data class Error(val message: String) : PeriodosResult
}

class PeriodoRepository(
    private val apiService: ApiService,
) {
    suspend fun listar(): PeriodosResult {
        return try {
            val periodos = mutableListOf<PeriodoMovil>()
            var pagina = 1
            var total = 0
            var haySiguiente: Boolean

            do {
                val respuesta = apiService.periodos(pagina)
                total = respuesta.count
                periodos += respuesta.results
                haySiguiente = respuesta.next != null
                pagina += 1
            } while (haySiguiente)

            PeriodosResult.Success(
                periodos = periodos,
                total = total,
            )
        } catch (error: HttpException) {
            PeriodosResult.Error(
                if (error.code() == 401 || error.code() == 403) {
                    "La sesión no tiene permiso para consultar períodos."
                } else {
                    "El servidor no pudo entregar los períodos."
                },
            )
        } catch (_: IOException) {
            PeriodosResult.Error(
                "No fue posible conectarse. Revisa Internet e inténtalo nuevamente.",
            )
        } catch (error: CancellationException) {
            throw error
        } catch (_: Exception) {
            PeriodosResult.Error(
                "Ocurrió un error inesperado al consultar períodos.",
            )
        }
    }
}
