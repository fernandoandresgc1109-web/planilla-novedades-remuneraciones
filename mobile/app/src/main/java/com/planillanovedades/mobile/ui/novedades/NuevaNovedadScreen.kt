package com.planillanovedades.mobile.ui.novedades

import androidx.activity.compose.BackHandler
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeDrawingPadding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.planillanovedades.mobile.data.model.UsuarioMovil

@Composable
fun NuevaNovedadScreen(
    user: UsuarioMovil,
    state: NuevaNovedadUiState,
    onBack: () -> Unit,
    onRetryOptions: () -> Unit,
    onDismissError: () -> Unit,
    onSubmit: (NuevaNovedadFormData) -> Unit,
    onViewNovedades: () -> Unit,
) {
    BackHandler(onBack = onBack)

    if (!user.puedeModificar) {
        MessageScreen(
            title = "Acceso de solo lectura",
            message = "Tu perfil puede consultar, pero no registrar novedades.",
            buttonText = "Volver al panel",
            onClick = onBack,
        )
        return
    }

    state.created?.let { creada ->
        MessageScreen(
            title = "Novedad registrada",
            message = (
                "La novedad de ${creada.colaboradorNombre} " +
                    "quedó guardada como borrador."
            ),
            buttonText = "Ver novedades",
            onClick = onViewNovedades,
        )
        return
    }

    if (state.loadingOptions) {
        MessageScreen(
            title = "Preparando formulario",
            message = "Consultando períodos, colaboradores y tipos de novedad…",
            showProgress = true,
        )
        return
    }

    if (!state.optionsLoaded && state.errorMessage != null) {
        MessageScreen(
            title = "No fue posible abrir el formulario",
            message = state.errorMessage,
            buttonText = "Intentar nuevamente",
            onClick = onRetryOptions,
            secondaryButtonText = "Volver",
            onSecondaryClick = onBack,
        )
        return
    }

    var periodoId by rememberSaveable { mutableStateOf<Int?>(null) }
    var colaboradorId by rememberSaveable { mutableStateOf<Int?>(null) }
    var tipoId by rememberSaveable { mutableStateOf<Int?>(null) }
    var fechaInicio by rememberSaveable { mutableStateOf("") }
    var fechaTermino by rememberSaveable { mutableStateOf("") }
    var cantidad by rememberSaveable { mutableStateOf("") }
    var monto by rememberSaveable { mutableStateOf("") }
    var observacion by rememberSaveable { mutableStateOf("") }

    val periodo = state.periodos.firstOrNull { it.id == periodoId }
    val colaboradoresDisponibles = remember(
        periodoId,
        periodo?.sucursal,
        state.colaboradores,
    ) {
        if (periodoId == null) {
            emptyList()
        } else {
            state.colaboradores.filter {
                it.sucursal == periodo?.sucursal
            }
        }
    }
    val tipo = state.tipos.firstOrNull { it.id == tipoId }

    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
            .safeDrawingPadding()
            .padding(horizontal = 20.dp),
        contentPadding = PaddingValues(vertical = 12.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp),
    ) {
        item {
            TextButton(onClick = onBack) {
                Text("← Volver al panel")
            }
        }
        item {
            Text(
                text = "Registrar novedad",
                style = MaterialTheme.typography.headlineMedium,
                fontWeight = FontWeight.Bold,
            )
        }
        item {
            Text(
                text = "El registro quedará en estado borrador para su revisión.",
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
        item {
            SelectorField(
                label = "Período abierto",
                selectedId = periodoId,
                options = state.periodos.map { it.id to it.descripcion },
                emptyMessage = "No existen períodos abiertos",
                onSelect = {
                    periodoId = it
                    colaboradorId = null
                    onDismissError()
                },
            )
        }
        item {
            SelectorField(
                label = "Colaborador",
                selectedId = colaboradorId,
                options = colaboradoresDisponibles.map {
                    it.id to "${it.nombreCompleto} · ${it.rut}"
                },
                emptyMessage = if (periodoId == null) {
                    "Selecciona primero un período"
                } else {
                    "No hay colaboradores activos en esta sucursal"
                },
                onSelect = {
                    colaboradorId = it
                    onDismissError()
                },
            )
        }
        item {
            SelectorField(
                label = "Tipo de novedad",
                selectedId = tipoId,
                options = state.tipos.map { it.id to it.nombre },
                emptyMessage = "No existen tipos activos",
                onSelect = {
                    tipoId = it
                    onDismissError()
                },
            )
        }
        if (tipo?.unidadMedida in setOf("DIAS", "MINUTOS")) {
            item {
                OutlinedTextField(
                    value = cantidad,
                    onValueChange = {
                        cantidad = it
                        onDismissError()
                    },
                    modifier = Modifier.fillMaxWidth(),
                    label = { Text("Cantidad requerida") },
                    supportingText = {
                        Text(if (tipo?.unidadMedida == "DIAS") "Número de días" else "Número de minutos")
                    },
                    keyboardOptions = KeyboardOptions(
                        keyboardType = KeyboardType.Decimal,
                    ),
                    singleLine = true,
                )
            }
        }
        if (tipo?.unidadMedida == "PESOS") {
            item {
                OutlinedTextField(
                    value = monto,
                    onValueChange = {
                        monto = it
                        onDismissError()
                    },
                    modifier = Modifier.fillMaxWidth(),
                    label = { Text("Monto requerido") },
                    keyboardOptions = KeyboardOptions(
                        keyboardType = KeyboardType.Decimal,
                    ),
                    singleLine = true,
                )
            }
        }
        item {
            OutlinedTextField(
                value = fechaInicio,
                onValueChange = {
                    fechaInicio = it
                    onDismissError()
                },
                modifier = Modifier.fillMaxWidth(),
                label = { Text("Fecha inicial (opcional)") },
                supportingText = { Text("Formato: AAAA-MM-DD") },
                keyboardOptions = KeyboardOptions(
                    keyboardType = KeyboardType.Text,
                ),
                singleLine = true,
            )
        }
        item {
            OutlinedTextField(
                value = fechaTermino,
                onValueChange = {
                    fechaTermino = it
                    onDismissError()
                },
                modifier = Modifier.fillMaxWidth(),
                label = { Text("Fecha final (opcional)") },
                supportingText = { Text("Formato: AAAA-MM-DD") },
                keyboardOptions = KeyboardOptions(
                    keyboardType = KeyboardType.Text,
                ),
                singleLine = true,
            )
        }
        item {
            OutlinedTextField(
                value = observacion,
                onValueChange = {
                    observacion = it
                    onDismissError()
                },
                modifier = Modifier.fillMaxWidth(),
                label = { Text("Observación (opcional)") },
                minLines = 3,
                maxLines = 5,
            )
        }
        if (state.errorMessage != null) {
            item {
                Text(
                    text = state.errorMessage,
                    color = MaterialTheme.colorScheme.error,
                )
            }
        }
        item {
            Button(
                onClick = {
                    onSubmit(
                        NuevaNovedadFormData(
                            periodoId = periodoId,
                            colaboradorId = colaboradorId,
                            tipoId = tipoId,
                            fechaInicio = fechaInicio,
                            fechaTermino = fechaTermino,
                            cantidad = cantidad,
                            monto = monto,
                            observacion = observacion,
                        )
                    )
                },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(52.dp),
                enabled = !state.submitting,
            ) {
                if (state.submitting) {
                    CircularProgressIndicator(
                        color = MaterialTheme.colorScheme.onPrimary,
                        strokeWidth = 2.dp,
                    )
                } else {
                    Text("Guardar como borrador")
                }
            }
        }
        item {
            Text(
                text = "Django comprobará nuevamente el rol, la sucursal y los datos antes de guardar.",
                modifier = Modifier.fillMaxWidth(),
                textAlign = TextAlign.Center,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                style = MaterialTheme.typography.bodySmall,
            )
        }
    }
}

@Composable
private fun SelectorField(
    label: String,
    selectedId: Int?,
    options: List<Pair<Int, String>>,
    emptyMessage: String,
    onSelect: (Int) -> Unit,
) {
    var expanded by remember { mutableStateOf(false) }
    val selectedLabel = options.firstOrNull { it.first == selectedId }?.second

    Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
        Text(
            text = label,
            style = MaterialTheme.typography.labelLarge,
            fontWeight = FontWeight.SemiBold,
        )
        Box(modifier = Modifier.fillMaxWidth()) {
            OutlinedButton(
                onClick = { expanded = true },
                modifier = Modifier.fillMaxWidth(),
                enabled = options.isNotEmpty(),
            ) {
                Text(
                    text = selectedLabel ?: emptyMessage,
                    modifier = Modifier.fillMaxWidth(),
                    textAlign = TextAlign.Start,
                )
            }
            DropdownMenu(
                expanded = expanded,
                onDismissRequest = { expanded = false },
            ) {
                options.forEach { option ->
                    DropdownMenuItem(
                        text = { Text(option.second) },
                        onClick = {
                            onSelect(option.first)
                            expanded = false
                        },
                    )
                }
            }
        }
    }
}

@Composable
private fun MessageScreen(
    title: String,
    message: String,
    buttonText: String? = null,
    onClick: (() -> Unit)? = null,
    secondaryButtonText: String? = null,
    onSecondaryClick: (() -> Unit)? = null,
    showProgress: Boolean = false,
) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
            .safeDrawingPadding()
            .padding(24.dp),
        contentAlignment = Alignment.Center,
    ) {
        Surface(
            modifier = Modifier.fillMaxWidth(),
            shape = MaterialTheme.shapes.extraLarge,
            tonalElevation = 3.dp,
        ) {
            Column(
                modifier = Modifier.padding(28.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(16.dp),
            ) {
                if (showProgress) CircularProgressIndicator()
                Text(
                    text = title,
                    style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.Bold,
                    textAlign = TextAlign.Center,
                )
                Text(
                    text = message,
                    textAlign = TextAlign.Center,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
                if (buttonText != null && onClick != null) {
                    Button(
                        onClick = onClick,
                        modifier = Modifier.fillMaxWidth(),
                    ) {
                        Text(buttonText)
                    }
                }
                if (
                    secondaryButtonText != null
                    && onSecondaryClick != null
                ) {
                    OutlinedButton(
                        onClick = onSecondaryClick,
                        modifier = Modifier.fillMaxWidth(),
                    ) {
                        Text(secondaryButtonText)
                    }
                }
                Spacer(Modifier.height(2.dp))
            }
        }
    }
}
