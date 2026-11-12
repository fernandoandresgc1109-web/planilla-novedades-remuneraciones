package com.planillanovedades.mobile.ui.exportaciones

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.planillanovedades.mobile.data.model.ExportacionMovil
import com.planillanovedades.mobile.data.repository.ExportacionRepository
import com.planillanovedades.mobile.data.repository.ExportacionesResult
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class ExportacionesUiState(
    val loading: Boolean = false,
    val loaded: Boolean = false,
    val exportaciones: List<ExportacionMovil> = emptyList(),
    val total: Int = 0,
    val query: String = "",
    val errorMessage: String? = null,
)

class ExportacionesViewModel(
    private val repository: ExportacionRepository,
) : ViewModel() {
    private val _uiState = MutableStateFlow(ExportacionesUiState())
    val uiState: StateFlow<ExportacionesUiState> = _uiState.asStateFlow()

    fun load(force: Boolean = false) {
        if (_uiState.value.loading) return
        if (_uiState.value.loaded && !force) return

        viewModelScope.launch {
            _uiState.update {
                it.copy(loading = true, errorMessage = null)
            }

            when (val result = repository.listar()) {
                is ExportacionesResult.Success -> _uiState.update {
                    it.copy(
                        loading = false,
                        loaded = true,
                        exportaciones = result.exportaciones,
                        total = result.total,
                    )
                }

                is ExportacionesResult.Error -> _uiState.update {
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
        _uiState.value = ExportacionesUiState()
    }

    class Factory(
        private val repository: ExportacionRepository,
    ) : ViewModelProvider.Factory {
        @Suppress("UNCHECKED_CAST")
        override fun <T : ViewModel> create(modelClass: Class<T>): T {
            require(modelClass.isAssignableFrom(ExportacionesViewModel::class.java))
            return ExportacionesViewModel(repository) as T
        }
    }
}
