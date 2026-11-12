package com.planillanovedades.mobile.ui.novedades

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.planillanovedades.mobile.data.model.NovedadMovil
import com.planillanovedades.mobile.data.repository.AccionNovedadResult
import com.planillanovedades.mobile.data.repository.NovedadRepository
import com.planillanovedades.mobile.data.repository.NovedadesResult
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class NovedadesUiState(
    val loading: Boolean = false,
    val loaded: Boolean = false,
    val novedades: List<NovedadMovil> = emptyList(),
    val total: Int = 0,
    val query: String = "",
    val errorMessage: String? = null,
    val workingId: Int? = null,
    val actionMessage: String? = null,
    val actionError: String? = null,
)

class NovedadesViewModel(
    private val repository: NovedadRepository,
) : ViewModel() {
    private val _uiState = MutableStateFlow(NovedadesUiState())
    val uiState: StateFlow<NovedadesUiState> = _uiState.asStateFlow()

    fun load(force: Boolean = false) {
        if (_uiState.value.loading) return
        if (_uiState.value.loaded && !force) return

        viewModelScope.launch {
            _uiState.update {
                it.copy(loading = true, errorMessage = null)
            }

            when (val result = repository.listar()) {
                is NovedadesResult.Success -> _uiState.update {
                    it.copy(
                        loading = false,
                        loaded = true,
                        novedades = result.novedades,
                        total = result.total,
                    )
                }

                is NovedadesResult.Error -> _uiState.update {
                    it.copy(
                        loading = false,
                        loaded = false,
                        errorMessage = result.message,
                    )
                }
            }
        }
    }

    fun updateQuery(query: String) {
        _uiState.update { it.copy(query = query) }
    }

    fun validar(id: Int) {
        ejecutarAccion(
            id = id,
            successMessage = "Novedad validada correctamente.",
        ) {
            repository.validar(id)
        }
    }

    fun anular(id: Int, motivo: String) {
        val motivoLimpio = motivo.trim()
        if (motivoLimpio.length !in 10..500) {
            _uiState.update {
                it.copy(
                    actionError = "El motivo debe tener entre 10 y 500 caracteres.",
                    actionMessage = null,
                )
            }
            return
        }

        ejecutarAccion(
            id = id,
            successMessage = "Novedad anulada correctamente.",
        ) {
            repository.anular(id, motivoLimpio)
        }
    }

    fun dismissActionFeedback() {
        _uiState.update {
            it.copy(actionMessage = null, actionError = null)
        }
    }

    private fun ejecutarAccion(
        id: Int,
        successMessage: String,
        action: suspend () -> AccionNovedadResult,
    ) {
        if (_uiState.value.workingId != null) return

        viewModelScope.launch {
            _uiState.update {
                it.copy(
                    workingId = id,
                    actionMessage = null,
                    actionError = null,
                )
            }

            when (val result = action()) {
                is AccionNovedadResult.Success -> _uiState.update { state ->
                    state.copy(
                        workingId = null,
                        novedades = state.novedades.map { novedad ->
                            if (novedad.id == result.novedad.id) {
                                result.novedad
                            } else {
                                novedad
                            }
                        },
                        actionMessage = successMessage,
                    )
                }

                is AccionNovedadResult.Error -> _uiState.update {
                    it.copy(
                        workingId = null,
                        actionError = result.message,
                    )
                }
            }
        }
    }

    fun clear() {
        _uiState.value = NovedadesUiState()
    }

    class Factory(
        private val repository: NovedadRepository,
    ) : ViewModelProvider.Factory {
        @Suppress("UNCHECKED_CAST")
        override fun <T : ViewModel> create(modelClass: Class<T>): T {
            require(modelClass.isAssignableFrom(NovedadesViewModel::class.java))
            return NovedadesViewModel(repository) as T
        }
    }
}
