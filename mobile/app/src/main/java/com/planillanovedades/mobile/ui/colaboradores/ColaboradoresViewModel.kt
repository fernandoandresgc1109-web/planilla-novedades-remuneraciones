package com.planillanovedades.mobile.ui.colaboradores

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.planillanovedades.mobile.data.model.ColaboradorMovil
import com.planillanovedades.mobile.data.repository.ColaboradorRepository
import com.planillanovedades.mobile.data.repository.ColaboradoresResult
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class ColaboradoresUiState(
    val loading: Boolean = false,
    val loaded: Boolean = false,
    val colaboradores: List<ColaboradorMovil> = emptyList(),
    val total: Int = 0,
    val query: String = "",
    val errorMessage: String? = null,
)

class ColaboradoresViewModel(
    private val repository: ColaboradorRepository,
) : ViewModel() {
    private val _uiState = MutableStateFlow(ColaboradoresUiState())
    val uiState: StateFlow<ColaboradoresUiState> = _uiState.asStateFlow()

    fun load(force: Boolean = false) {
        if (_uiState.value.loading) return
        if (_uiState.value.loaded && !force) return

        viewModelScope.launch {
            _uiState.update {
                it.copy(loading = true, errorMessage = null)
            }

            when (val result = repository.listar()) {
                is ColaboradoresResult.Success -> _uiState.update {
                    it.copy(
                        loading = false,
                        loaded = true,
                        colaboradores = result.colaboradores,
                        total = result.total,
                    )
                }

                is ColaboradoresResult.Error -> _uiState.update {
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
        _uiState.value = ColaboradoresUiState()
    }

    class Factory(
        private val repository: ColaboradorRepository,
    ) : ViewModelProvider.Factory {
        @Suppress("UNCHECKED_CAST")
        override fun <T : ViewModel> create(modelClass: Class<T>): T {
            require(modelClass.isAssignableFrom(ColaboradoresViewModel::class.java))
            return ColaboradoresViewModel(repository) as T
        }
    }
}
