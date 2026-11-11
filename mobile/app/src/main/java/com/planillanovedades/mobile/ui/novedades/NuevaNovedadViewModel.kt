package com.planillanovedades.mobile.ui.novedades

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.planillanovedades.mobile.data.model.ColaboradorMovil
import com.planillanovedades.mobile.data.model.NovedadMovil
import com.planillanovedades.mobile.data.model.NuevaNovedadRequest
import com.planillanovedades.mobile.data.model.PeriodoMovil
import com.planillanovedades.mobile.data.model.TipoNovedadMovil
import com.planillanovedades.mobile.data.repository.CrearNovedadResult
import com.planillanovedades.mobile.data.repository.NuevaNovedadRepository
import com.planillanovedades.mobile.data.repository.OpcionesNuevaNovedadResult
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class NuevaNovedadFormData(
    val periodoId: Int?,
    val colaboradorId: Int?,
    val tipoId: Int?,
    val fechaInicio: String,
    val fechaTermino: String,
    val cantidad: String,
    val monto: String,
    val observacion: String,
)

data class NuevaNovedadUiState(
    val loadingOptions: Boolean = false,
    val optionsLoaded: Boolean = false,
    val submitting: Boolean = false,
    val periodos: List<PeriodoMovil> = emptyList(),
    val colaboradores: List<ColaboradorMovil> = emptyList(),
    val tipos: List<TipoNovedadMovil> = emptyList(),
    val created: NovedadMovil? = null,
    val errorMessage: String? = null,
)

class NuevaNovedadViewModel(
    private val repository: NuevaNovedadRepository,
) : ViewModel() {
    private val _uiState = MutableStateFlow(NuevaNovedadUiState())
    val uiState: StateFlow<NuevaNovedadUiState> = _uiState.asStateFlow()

    fun loadOptions(force: Boolean = false) {
        if (_uiState.value.loadingOptions) return
        if (_uiState.value.optionsLoaded && !force) return

        viewModelScope.launch {
            _uiState.update {
                it.copy(
                    loadingOptions = true,
                    errorMessage = null,
                    created = null,
                )
            }
            when (val result = repository.cargarOpciones()) {
                is OpcionesNuevaNovedadResult.Success -> _uiState.update {
                    it.copy(
                        loadingOptions = false,
                        optionsLoaded = true,
                        periodos = result.periodos,
                        colaboradores = result.colaboradores,
                        tipos = result.tipos,
                    )
                }

                is OpcionesNuevaNovedadResult.Error -> _uiState.update {
                    it.copy(
                        loadingOptions = false,
                        optionsLoaded = false,
                        errorMessage = result.message,
                    )
                }
            }
        }
    }

    fun submit(form: NuevaNovedadFormData) {
        if (_uiState.value.submitting) return

        val validationError = validateForm(form)
        if (validationError != null) {
            _uiState.update { it.copy(errorMessage = validationError) }
            return
        }

        val request = NuevaNovedadRequest(
            periodo = requireNotNull(form.periodoId),
            colaborador = requireNotNull(form.colaboradorId),
            tipoNovedad = requireNotNull(form.tipoId),
            fechaInicio = form.fechaInicio.trim().ifBlank { null },
            fechaTermino = form.fechaTermino.trim().ifBlank { null },
            cantidad = form.cantidad.trim().ifBlank { null },
            monto = form.monto.trim().ifBlank { null },
            observacion = form.observacion.trim(),
        )

        viewModelScope.launch {
            _uiState.update {
                it.copy(submitting = true, errorMessage = null)
            }
            when (val result = repository.crear(request)) {
                is CrearNovedadResult.Success -> _uiState.update {
                    it.copy(
                        submitting = false,
                        created = result.novedad,
                    )
                }

                is CrearNovedadResult.Error -> _uiState.update {
                    it.copy(
                        submitting = false,
                        errorMessage = result.message,
                    )
                }
            }
        }
    }

    fun dismissError() {
        _uiState.update { it.copy(errorMessage = null) }
    }

    fun clear() {
        _uiState.value = NuevaNovedadUiState()
    }

    private fun validateForm(form: NuevaNovedadFormData): String? {
        if (form.periodoId == null) return "Selecciona un período abierto."
        if (form.colaboradorId == null) return "Selecciona un colaborador."
        if (form.tipoId == null) return "Selecciona un tipo de novedad."

        val tipo = _uiState.value.tipos.firstOrNull { it.id == form.tipoId }
        if (tipo?.unidadMedida == "PESOS" && form.monto.isBlank()) {
            return "Este tipo de novedad requiere un monto."
        }
        if (
            tipo?.unidadMedida in setOf("DIAS", "MINUTOS")
            && form.cantidad.isBlank()
        ) {
            return "Este tipo de novedad requiere una cantidad."
        }
        if (
            form.monto.isNotBlank()
            && form.monto.toBigDecimalOrNull() == null
        ) {
            return "El monto debe ser un número válido."
        }
        if (
            form.cantidad.isNotBlank()
            && form.cantidad.toBigDecimalOrNull() == null
        ) {
            return "La cantidad debe ser un número válido."
        }

        val datePattern = Regex("\\d{4}-\\d{2}-\\d{2}")
        if (
            form.fechaInicio.isNotBlank()
            && !datePattern.matches(form.fechaInicio.trim())
        ) {
            return "La fecha inicial debe tener el formato AAAA-MM-DD."
        }
        if (
            form.fechaTermino.isNotBlank()
            && !datePattern.matches(form.fechaTermino.trim())
        ) {
            return "La fecha final debe tener el formato AAAA-MM-DD."
        }
        if (
            form.fechaInicio.isNotBlank()
            && form.fechaTermino.isNotBlank()
            && form.fechaTermino.trim() < form.fechaInicio.trim()
        ) {
            return "La fecha final no puede ser anterior a la fecha inicial."
        }

        return null
    }

    class Factory(
        private val repository: NuevaNovedadRepository,
    ) : ViewModelProvider.Factory {
        @Suppress("UNCHECKED_CAST")
        override fun <T : ViewModel> create(modelClass: Class<T>): T {
            require(modelClass.isAssignableFrom(NuevaNovedadViewModel::class.java))
            return NuevaNovedadViewModel(repository) as T
        }
    }
}
