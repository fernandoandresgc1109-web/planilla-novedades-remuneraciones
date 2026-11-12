package com.planillanovedades.mobile.ui.periodos

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.planillanovedades.mobile.data.model.PeriodoMovil
import com.planillanovedades.mobile.data.repository.PeriodoRepository
import com.planillanovedades.mobile.data.repository.PeriodosResult
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class PeriodosUiState(
    val loading: Boolean = false,
    val loaded: Boolean = false,
    val periodos: List<PeriodoMovil> = emptyList(),
    val total: Int = 0,
    val query: String = "",
    val errorMessage: String? = null,
)

class PeriodosViewModel(
    private val repository: PeriodoRepository,
) : ViewModel() {
    private val _uiState = MutableStateFlow(PeriodosUiState())
    val uiState: StateFlow<PeriodosUiState> = _uiState.asStateFlow()

    fun load(force: Boolean = false) {
        if (_uiState.value.loading) return
        if (_uiState.value.loaded && !force) return

        viewModelScope.launch {
            _uiState.update {
                it.copy(loading = true, errorMessage = null)
            }

            when (val result = repository.listar()) {
                is PeriodosResult.Success -> _uiState.update {
                    it.copy(
                        loading = false,
                        loaded = true,
                        periodos = result.periodos,
                        total = result.total,
                    )
                }

                is PeriodosResult.Error -> _uiState.update {
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

    fun clear() {
        _uiState.value = PeriodosUiState()
    }

    class Factory(
        private val repository: PeriodoRepository,
    ) : ViewModelProvider.Factory {
        @Suppress("UNCHECKED_CAST")
        override fun <T : ViewModel> create(modelClass: Class<T>): T {
            require(modelClass.isAssignableFrom(PeriodosViewModel::class.java))
            return PeriodosViewModel(repository) as T
        }
    }
}
