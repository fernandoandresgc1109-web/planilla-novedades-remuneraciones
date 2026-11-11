package com.planillanovedades.mobile.data.repository

import com.planillanovedades.mobile.data.model.ColaboradorMovil
import com.planillanovedades.mobile.data.model.NovedadMovil
import com.planillanovedades.mobile.data.model.NuevaNovedadRequest
import com.planillanovedades.mobile.data.model.PaginatedResponse
import com.planillanovedades.mobile.data.model.PeriodoMovil
import com.planillanovedades.mobile.data.model.TipoNovedadMovil
import com.planillanovedades.mobile.data.remote.ApiService
import java.io.IOException
import kotlinx.coroutines.CancellationException
import retrofit2.HttpException

sealed interface OpcionesNuevaNovedadResult {
    data class Success(
        val periodos: List<PeriodoMovil>,
        val colaboradores: List<ColaboradorMovil>,
        val tipos: List<TipoNovedadMovil>,
    ) : OpcionesNuevaNovedadResult

    data class Error(val message: String) : OpcionesNuevaNovedadResult
}

sealed interface CrearNovedadResult {
    data class Success(val novedad: NovedadMovil) : CrearNovedadResult
    data class Error(val message: String) : CrearNovedadResult
}

class NuevaNovedadRepository(
    private val apiService: ApiService,
) {
    suspend fun cargarOpciones(): OpcionesNuevaNovedadResult {
        return try {
            val periodos = cargarPaginas { pagina ->
                apiService.periodos(pagina)
            }.filter { it.estado == "ABIERTO" }
            val colaboradores = cargarPaginas { pagina ->
                apiService.colaboradores(pagina)
            }.filter { it.activo }
            val tipos = cargarPaginas { pagina ->
                apiService.tiposNovedad(pagina)
            }.filter { it.activo }

            OpcionesNuevaNovedadResult.Success(
                periodos = periodos,
                colaboradores = colaboradores,
                tipos = tipos,
            )
        } catch (error: HttpException) {
            OpcionesNuevaNovedadResult.Error(
                if (error.code() == 401 || error.code() == 403) {
                    "La sesión no tiene permiso para registrar novedades."
                } else {
                    "El servidor no pudo entregar las opciones del formulario."
                },
            )
        } catch (_: IOException) {
            OpcionesNuevaNovedadResult.Error(
                "No fue posible conectarse. Revisa Internet e inténtalo nuevamente.",
            )
        } catch (error: CancellationException) {
            throw error
        } catch (_: Exception) {
            OpcionesNuevaNovedadResult.Error(
                "Ocurrió un error inesperado al preparar el formulario.",
            )
        }
    }

    suspend fun crear(request: NuevaNovedadRequest): CrearNovedadResult {
        return try {
            CrearNovedadResult.Success(
                apiService.crearNovedad(request),
            )
        } catch (error: HttpException) {
            CrearNovedadResult.Error(
                when (error.code()) {
                    400 -> "El servidor rechazó los datos. Revisa los campos y la sucursal seleccionada."
                    401, 403 -> "Tu perfil no tiene permiso para registrar novedades."
                    else -> "El servidor no pudo guardar la novedad."
                },
            )
        } catch (_: IOException) {
            CrearNovedadResult.Error(
                "No fue posible conectarse. Revisa Internet e inténtalo nuevamente.",
            )
        } catch (error: CancellationException) {
            throw error
        } catch (_: Exception) {
            CrearNovedadResult.Error(
                "Ocurrió un error inesperado al guardar la novedad.",
            )
        }
    }

    private suspend fun <T> cargarPaginas(
        consultar: suspend (Int) -> PaginatedResponse<T>,
    ): List<T> {
        val registros = mutableListOf<T>()
        var pagina = 1
        var haySiguiente: Boolean

        do {
            val respuesta = consultar(pagina)
            registros += respuesta.results
            haySiguiente = respuesta.next != null
            pagina += 1
        } while (haySiguiente)

        return registros
    }
}
