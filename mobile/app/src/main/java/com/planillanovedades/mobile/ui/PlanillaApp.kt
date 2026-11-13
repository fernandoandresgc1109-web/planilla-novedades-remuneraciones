package com.planillanovedades.mobile.ui

import androidx.activity.compose.BackHandler
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeDrawingPadding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.AssistChip
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.HorizontalDivider
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
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.planillanovedades.mobile.data.model.ColaboradorMovil
import com.planillanovedades.mobile.data.model.ExportacionMovil
import com.planillanovedades.mobile.data.model.NovedadMovil
import com.planillanovedades.mobile.data.model.PeriodoMovil
import com.planillanovedades.mobile.data.model.UsuarioMovil
import com.planillanovedades.mobile.ui.auth.AuthUiState
import com.planillanovedades.mobile.ui.colaboradores.ColaboradoresUiState
import com.planillanovedades.mobile.ui.exportaciones.ExportacionesUiState
import com.planillanovedades.mobile.ui.novedades.NovedadesUiState
import com.planillanovedades.mobile.ui.novedades.NuevaNovedadFormData
import com.planillanovedades.mobile.ui.novedades.NuevaNovedadScreen
import com.planillanovedades.mobile.ui.novedades.NuevaNovedadUiState
import com.planillanovedades.mobile.ui.periodos.PeriodosUiState

private const val DESTINO_INICIO = "inicio"
private const val DESTINO_COLABORADORES = "colaboradores"
private const val DESTINO_NOVEDADES = "novedades"
private const val DESTINO_NUEVA_NOVEDAD = "nueva_novedad"
private const val DESTINO_PERIODOS = "periodos"
private const val DESTINO_EXPORTACIONES = "exportaciones"

@Composable
fun PlanillaApp(
    state: AuthUiState,
    colaboradoresState: ColaboradoresUiState,
    novedadesState: NovedadesUiState,
    nuevaNovedadState: NuevaNovedadUiState,
    periodosState: PeriodosUiState,
    exportacionesState: ExportacionesUiState,
    onLogin: (String, String) -> Unit,
    onLogout: () -> Unit,
    onDismissError: () -> Unit,
    onOpenColaboradores: () -> Unit,
    onRefreshColaboradores: () -> Unit,
    onSearchColaboradores: (String) -> Unit,
    onOpenNovedades: () -> Unit,
    onRefreshNovedades: () -> Unit,
    onSearchNovedades: (String) -> Unit,
    onValidarNovedad: (Int) -> Unit,
    onAnularNovedad: (Int, String) -> Unit,
    onDismissNovedadFeedback: () -> Unit,
    onOpenNuevaNovedad: () -> Unit,
    onRetryNuevaNovedad: () -> Unit,
    onDismissNuevaNovedadError: () -> Unit,
    onSubmitNuevaNovedad: (NuevaNovedadFormData) -> Unit,
    onCreatedNovedad: () -> Unit,
    onOpenPeriodos: () -> Unit,
    onRefreshPeriodos: () -> Unit,
    onSearchPeriodos: (String) -> Unit,
    onOpenExportaciones: () -> Unit,
    onRefreshExportaciones: () -> Unit,
    onSearchExportaciones: (String) -> Unit,
) {
    var destino by rememberSaveable(state.user?.id) {
        mutableStateOf(DESTINO_INICIO)
    }

    when {
        state.restoringSession -> LoadingScreen("Comprobando sesión…")
        state.user == null -> LoginScreen(
            loading = state.working,
            errorMessage = state.errorMessage,
            onLogin = onLogin,
            onDismissError = onDismissError,
        )
        destino == DESTINO_COLABORADORES -> ColaboradoresScreen(
            user = state.user,
            state = colaboradoresState,
            onBack = { destino = DESTINO_INICIO },
            onRefresh = onRefreshColaboradores,
            onSearch = onSearchColaboradores,
        )
        destino == DESTINO_NOVEDADES -> NovedadesScreen(
            user = state.user,
            state = novedadesState,
            onBack = { destino = DESTINO_INICIO },
            onRefresh = onRefreshNovedades,
            onSearch = onSearchNovedades,
            onValidate = onValidarNovedad,
            onAnnul = onAnularNovedad,
            onDismissFeedback = onDismissNovedadFeedback,
        )
        destino == DESTINO_NUEVA_NOVEDAD -> NuevaNovedadScreen(
            user = state.user,
            state = nuevaNovedadState,
            onBack = { destino = DESTINO_INICIO },
            onRetryOptions = onRetryNuevaNovedad,
            onDismissError = onDismissNuevaNovedadError,
            onSubmit = onSubmitNuevaNovedad,
            onViewNovedades = {
                destino = DESTINO_NOVEDADES
                onCreatedNovedad()
            },
        )
        destino == DESTINO_PERIODOS -> PeriodosScreen(
            user = state.user,
            state = periodosState,
            onBack = { destino = DESTINO_INICIO },
            onRefresh = onRefreshPeriodos,
            onSearch = onSearchPeriodos,
        )
        destino == DESTINO_EXPORTACIONES -> ExportacionesScreen(
            user = state.user,
            state = exportacionesState,
            onBack = { destino = DESTINO_INICIO },
            onRefresh = onRefreshExportaciones,
            onSearch = onSearchExportaciones,
        )
        else -> HomeScreen(
            user = state.user,
            loggingOut = state.working,
            onOpenColaboradores = {
                destino = DESTINO_COLABORADORES
                onOpenColaboradores()
            },
            onOpenNovedades = {
                destino = DESTINO_NOVEDADES
                onOpenNovedades()
            },
            onOpenNuevaNovedad = {
                destino = DESTINO_NUEVA_NOVEDAD
                onOpenNuevaNovedad()
            },
            onOpenPeriodos = {
                destino = DESTINO_PERIODOS
                onOpenPeriodos()
            },
            onOpenExportaciones = {
                destino = DESTINO_EXPORTACIONES
                onOpenExportaciones()
            },
            onLogout = {
                destino = DESTINO_INICIO
                onLogout()
            },
        )
    }
}

@Composable
private fun LoadingScreen(message: String) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
            .safeDrawingPadding(),
        contentAlignment = Alignment.Center,
    ) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            CircularProgressIndicator()
            Spacer(Modifier.height(16.dp))
            Text(message)
        }
    }
}

@Composable
private fun LoginScreen(
    loading: Boolean,
    errorMessage: String?,
    onLogin: (String, String) -> Unit,
    onDismissError: () -> Unit,
) {
    var username by rememberSaveable { mutableStateOf("") }
    var password by rememberSaveable { mutableStateOf("") }

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
                verticalArrangement = Arrangement.spacedBy(16.dp),
            ) {
                Text(
                    text = "PLANILLA DE NOVEDADES",
                    color = MaterialTheme.colorScheme.primary,
                    style = MaterialTheme.typography.labelLarge,
                    fontWeight = FontWeight.Bold,
                )
                Text(
                    text = "Acceso móvil",
                    style = MaterialTheme.typography.headlineMedium,
                    fontWeight = FontWeight.Bold,
                )
                Text(
                    text = "Ingresa con el mismo usuario del sistema web.",
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
                OutlinedTextField(
                    value = username,
                    onValueChange = {
                        username = it
                        if (errorMessage != null) onDismissError()
                    },
                    modifier = Modifier.fillMaxWidth(),
                    label = { Text("Usuario") },
                    singleLine = true,
                    enabled = !loading,
                    keyboardOptions = KeyboardOptions(
                        keyboardType = KeyboardType.Text,
                        imeAction = ImeAction.Next,
                    ),
                )
                OutlinedTextField(
                    value = password,
                    onValueChange = {
                        password = it
                        if (errorMessage != null) onDismissError()
                    },
                    modifier = Modifier.fillMaxWidth(),
                    label = { Text("Contraseña") },
                    singleLine = true,
                    enabled = !loading,
                    visualTransformation = PasswordVisualTransformation(),
                    keyboardOptions = KeyboardOptions(
                        keyboardType = KeyboardType.Password,
                        imeAction = ImeAction.Done,
                    ),
                    keyboardActions = KeyboardActions(
                        onDone = { onLogin(username, password) },
                    ),
                )
                if (errorMessage != null) {
                    Text(
                        text = errorMessage,
                        color = MaterialTheme.colorScheme.error,
                        style = MaterialTheme.typography.bodyMedium,
                    )
                }
                Button(
                    onClick = { onLogin(username, password) },
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(52.dp),
                    enabled = !loading,
                ) {
                    if (loading) {
                        CircularProgressIndicator(
                            color = MaterialTheme.colorScheme.onPrimary,
                            strokeWidth = 2.dp,
                        )
                    } else {
                        Text("Iniciar sesión")
                    }
                }
                if (loading) {
                    Text(
                        text = "Conectando con el servidor. Si estaba inactivo, puede tardar hasta un minuto.",
                        modifier = Modifier.fillMaxWidth(),
                        textAlign = TextAlign.Center,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        style = MaterialTheme.typography.bodySmall,
                    )
                }
                Text(
                    text = "Conexión protegida mediante HTTPS",
                    modifier = Modifier.fillMaxWidth(),
                    textAlign = TextAlign.Center,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    style = MaterialTheme.typography.labelMedium,
                )
            }
        }
    }
}

@Composable
private fun HomeScreen(
    user: UsuarioMovil,
    loggingOut: Boolean,
    onOpenColaboradores: () -> Unit,
    onOpenNovedades: () -> Unit,
    onOpenNuevaNovedad: () -> Unit,
    onOpenPeriodos: () -> Unit,
    onOpenExportaciones: () -> Unit,
    onLogout: () -> Unit,
) {
    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
            .safeDrawingPadding()
            .padding(horizontal = 24.dp),
        contentPadding = PaddingValues(vertical = 24.dp),
        verticalArrangement = Arrangement.spacedBy(18.dp),
    ) {
        item {
            Text(
                text = "PLANILLA DE NOVEDADES",
                color = MaterialTheme.colorScheme.primary,
                style = MaterialTheme.typography.labelLarge,
                fontWeight = FontWeight.Bold,
            )
        }
        item {
            Text(
                text = "Bienvenido, ${user.nombre.ifBlank { user.username }}",
                style = MaterialTheme.typography.headlineMedium,
                fontWeight = FontWeight.Bold,
            )
        }
        item {
            Text(
                text = "Selecciona una función para trabajar con la información autorizada para tu perfil.",
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
        item {
            Surface(
                modifier = Modifier.fillMaxWidth(),
                shape = MaterialTheme.shapes.large,
                tonalElevation = 2.dp,
            ) {
                Column(
                    modifier = Modifier.padding(20.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp),
                ) {
                    DetailRow("Usuario", user.username)
                    HorizontalDivider()
                    DetailRow("Rol", user.rol)
                    HorizontalDivider()
                    DetailRow(
                        "Sucursal",
                        user.sucursal?.nombre ?: "Acceso a todas las sucursales",
                    )
                }
            }
        }
        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                if (user.puedeModificar) {
                    AssistChip(onClick = {}, label = { Text("Puede modificar") })
                }
                if (user.puedeExportar) {
                    AssistChip(onClick = {}, label = { Text("Puede exportar") })
                }
            }
        }
        item {
            Text(
                text = "Gestión móvil",
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold,
            )
        }
        item {
            ModuleCard(
                title = "Colaboradores",
                description = "Consulta y busca el personal visible para tu sucursal.",
                onClick = onOpenColaboradores,
            )
        }
        item {
            ModuleCard(
                title = "Novedades",
                description = "Consulta los registros autorizados y su estado actual.",
                onClick = onOpenNovedades,
            )
        }
        item {
            ModuleCard(
                title = "Períodos",
                description = "Consulta los meses disponibles y su estado actual.",
                onClick = onOpenPeriodos,
            )
        }
        if (user.puedeModificar) {
            item {
                ModuleCard(
                    title = "Registrar novedad",
                    description = "Crea un registro en borrador para revisión.",
                    onClick = onOpenNuevaNovedad,
                )
            }
        }
        if (user.puedeExportar) {
            item {
                ModuleCard(
                    title = "Exportaciones",
                    description = "Consulta el historial de archivos generados.",
                    onClick = onOpenExportaciones,
                )
            }
        }
        item {
            OutlinedButton(
                onClick = onLogout,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(52.dp),
                enabled = !loggingOut,
            ) {
                Text(if (loggingOut) "Cerrando sesión…" else "Cerrar sesión")
            }
        }
    }
}

@Composable
private fun ModuleCard(
    title: String,
    description: String,
    onClick: () -> Unit,
) {
    Surface(
        onClick = onClick,
        modifier = Modifier.fillMaxWidth(),
        shape = MaterialTheme.shapes.large,
        color = MaterialTheme.colorScheme.primaryContainer,
        tonalElevation = 2.dp,
    ) {
        Column(
            modifier = Modifier.padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(6.dp),
        ) {
            Text(
                text = title,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onPrimaryContainer,
            )
            Text(
                text = description,
                color = MaterialTheme.colorScheme.onPrimaryContainer,
            )
            Text(
                text = "Abrir →",
                style = MaterialTheme.typography.labelLarge,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.primary,
            )
        }
    }
}

@Composable
private fun ColaboradoresScreen(
    user: UsuarioMovil,
    state: ColaboradoresUiState,
    onBack: () -> Unit,
    onRefresh: () -> Unit,
    onSearch: (String) -> Unit,
) {
    BackHandler(onBack = onBack)

    val filtrados = remember(state.query, state.colaboradores) {
        val texto = state.query.trim()
        if (texto.isBlank()) {
            state.colaboradores
        } else {
            state.colaboradores.filter { colaborador ->
                colaborador.nombreCompleto.contains(texto, ignoreCase = true) ||
                    colaborador.rut.contains(texto, ignoreCase = true) ||
                    colaborador.sucursalNombre.contains(texto, ignoreCase = true)
            }
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
            .safeDrawingPadding()
            .padding(horizontal = 20.dp, vertical = 12.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        TextButton(onClick = onBack) {
            Text("← Volver al panel")
        }
        Text(
            text = "Colaboradores",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold,
        )
        Text(
            text = user.sucursal?.nombre ?: "Todas las sucursales autorizadas",
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        OutlinedTextField(
            value = state.query,
            onValueChange = onSearch,
            modifier = Modifier.fillMaxWidth(),
            label = { Text("Buscar por nombre, RUT o sucursal") },
            singleLine = true,
        )

        when {
            state.loading -> Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(1f),
                contentAlignment = Alignment.Center,
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    CircularProgressIndicator()
                    Spacer(Modifier.height(12.dp))
                    Text("Consultando colaboradores…")
                }
            }

            state.errorMessage != null -> Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(1f),
                contentAlignment = Alignment.Center,
            ) {
                Column(
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(12.dp),
                ) {
                    Text(
                        text = state.errorMessage,
                        color = MaterialTheme.colorScheme.error,
                        textAlign = TextAlign.Center,
                    )
                    Button(onClick = onRefresh) {
                        Text("Intentar nuevamente")
                    }
                }
            }

            else -> {
                Text(
                    text = "Mostrando ${filtrados.size} de ${state.total}",
                    style = MaterialTheme.typography.labelLarge,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
                if (filtrados.isEmpty()) {
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .weight(1f),
                        contentAlignment = Alignment.Center,
                    ) {
                        Text(
                            text = "No se encontraron colaboradores.",
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    }
                } else {
                    LazyColumn(
                        modifier = Modifier.weight(1f),
                        contentPadding = PaddingValues(bottom = 20.dp),
                        verticalArrangement = Arrangement.spacedBy(10.dp),
                    ) {
                        items(
                            items = filtrados,
                            key = { it.id },
                        ) { colaborador ->
                            ColaboradorCard(colaborador)
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun ColaboradorCard(colaborador: ColaboradorMovil) {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = MaterialTheme.shapes.large,
        tonalElevation = 2.dp,
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(6.dp),
        ) {
            Text(
                text = colaborador.nombreCompleto,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
            )
            Text(
                text = "RUT: ${colaborador.rut}",
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Text(
                text = "Sucursal: ${colaborador.sucursalNombre}",
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Surface(
                shape = MaterialTheme.shapes.small,
                color = if (colaborador.activo) {
                    MaterialTheme.colorScheme.primaryContainer
                } else {
                    MaterialTheme.colorScheme.errorContainer
                },
            ) {
                Text(
                    text = if (colaborador.activo) "Activo" else "Inactivo",
                    modifier = Modifier.padding(horizontal = 10.dp, vertical = 4.dp),
                    style = MaterialTheme.typography.labelMedium,
                    fontWeight = FontWeight.SemiBold,
                    color = if (colaborador.activo) {
                        MaterialTheme.colorScheme.onPrimaryContainer
                    } else {
                        MaterialTheme.colorScheme.onErrorContainer
                    },
                )
            }
        }
    }
}

@Composable
private fun PeriodosScreen(
    user: UsuarioMovil,
    state: PeriodosUiState,
    onBack: () -> Unit,
    onRefresh: () -> Unit,
    onSearch: (String) -> Unit,
) {
    BackHandler(onBack = onBack)

    val filtrados = remember(state.query, state.periodos) {
        val texto = state.query.trim()
        if (texto.isBlank()) {
            state.periodos
        } else {
            state.periodos.filter { periodo ->
                periodo.nombreMes.contains(texto, ignoreCase = true) ||
                    periodo.anio.toString().contains(texto) ||
                    periodo.descripcion.contains(texto, ignoreCase = true) ||
                    periodo.sucursalNombre.contains(texto, ignoreCase = true) ||
                    periodo.estado.contains(texto, ignoreCase = true) ||
                    periodo.fechaInicio.contains(texto)
            }
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
            .safeDrawingPadding()
            .padding(horizontal = 20.dp, vertical = 12.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        TextButton(onClick = onBack) {
            Text("← Volver al panel")
        }
        Text(
            text = "Períodos de liquidación",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold,
        )
        Text(
            text = user.sucursal?.nombre ?: "Todas las sucursales autorizadas",
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        OutlinedTextField(
            value = state.query,
            onValueChange = onSearch,
            modifier = Modifier.fillMaxWidth(),
            label = { Text("Buscar mes, año, sucursal o estado") },
            singleLine = true,
        )

        when {
            state.loading -> Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(1f),
                contentAlignment = Alignment.Center,
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    CircularProgressIndicator()
                    Spacer(Modifier.height(12.dp))
                    Text("Consultando períodos…")
                }
            }

            state.errorMessage != null -> Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(1f),
                contentAlignment = Alignment.Center,
            ) {
                Column(
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(12.dp),
                ) {
                    Text(
                        text = state.errorMessage,
                        color = MaterialTheme.colorScheme.error,
                        textAlign = TextAlign.Center,
                    )
                    Button(onClick = onRefresh) {
                        Text("Intentar nuevamente")
                    }
                }
            }

            else -> {
                val abiertos = filtrados.count { it.estado == "ABIERTO" }
                Text(
                    text = "Mostrando ${filtrados.size} de ${state.total} · Abiertos: $abiertos",
                    style = MaterialTheme.typography.labelLarge,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
                if (filtrados.isEmpty()) {
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .weight(1f),
                        contentAlignment = Alignment.Center,
                    ) {
                        Text(
                            text = "No se encontraron períodos.",
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    }
                } else {
                    LazyColumn(
                        modifier = Modifier.weight(1f),
                        contentPadding = PaddingValues(bottom = 20.dp),
                        verticalArrangement = Arrangement.spacedBy(10.dp),
                    ) {
                        items(
                            items = filtrados,
                            key = { it.id },
                        ) { periodo ->
                            PeriodoCard(periodo)
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun PeriodoCard(periodo: PeriodoMovil) {
    val estadoContainer = when (periodo.estado) {
        "ABIERTO" -> MaterialTheme.colorScheme.primaryContainer
        "EXPORTADO" -> MaterialTheme.colorScheme.tertiaryContainer
        else -> MaterialTheme.colorScheme.secondaryContainer
    }
    val estadoContent = when (periodo.estado) {
        "ABIERTO" -> MaterialTheme.colorScheme.onPrimaryContainer
        "EXPORTADO" -> MaterialTheme.colorScheme.onTertiaryContainer
        else -> MaterialTheme.colorScheme.onSecondaryContainer
    }

    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = MaterialTheme.shapes.large,
        tonalElevation = 2.dp,
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(6.dp),
        ) {
            Text(
                text = "${periodo.nombreMes} ${periodo.anio}",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
            )
            Text(
                text = "Sucursal: ${periodo.sucursalNombre}",
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Text(
                text = "Inicio: ${periodo.fechaInicio}",
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            periodo.fechaCierreLegible?.let { fecha ->
                Text(
                    text = "Cierre: $fecha",
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
            Surface(
                shape = MaterialTheme.shapes.small,
                color = estadoContainer,
            ) {
                Text(
                    text = periodo.estado.lowercase()
                        .replaceFirstChar { it.uppercase() },
                    modifier = Modifier.padding(horizontal = 10.dp, vertical = 4.dp),
                    style = MaterialTheme.typography.labelMedium,
                    fontWeight = FontWeight.SemiBold,
                    color = estadoContent,
                )
            }
        }
    }
}

@Composable
private fun ExportacionesScreen(
    user: UsuarioMovil,
    state: ExportacionesUiState,
    onBack: () -> Unit,
    onRefresh: () -> Unit,
    onSearch: (String) -> Unit,
) {
    BackHandler(onBack = onBack)

    val filtradas = remember(state.query, state.exportaciones) {
        val texto = state.query.trim()
        if (texto.isBlank()) {
            state.exportaciones
        } else {
            state.exportaciones.filter { exportacion ->
                exportacion.nombreArchivo.contains(texto, ignoreCase = true) ||
                    exportacion.periodoDescripcion.contains(texto, ignoreCase = true) ||
                    exportacion.sucursalNombre.contains(texto, ignoreCase = true) ||
                    exportacion.formato.contains(texto, ignoreCase = true) ||
                    exportacion.generadoPorNombre.contains(texto, ignoreCase = true) ||
                    exportacion.fechaGeneracionLegible.contains(texto, ignoreCase = true)
            }
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
            .safeDrawingPadding()
            .padding(horizontal = 20.dp, vertical = 12.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        TextButton(onClick = onBack) {
            Text("← Volver al panel")
        }
        Text(
            text = "Historial de exportaciones",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold,
        )
        Text(
            text = user.sucursal?.nombre ?: "Todas las sucursales autorizadas",
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        OutlinedTextField(
            value = state.query,
            onValueChange = onSearch,
            modifier = Modifier.fillMaxWidth(),
            label = { Text("Buscar archivo, período, sucursal o formato") },
            singleLine = true,
        )

        when {
            state.loading -> Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(1f),
                contentAlignment = Alignment.Center,
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    CircularProgressIndicator()
                    Spacer(Modifier.height(12.dp))
                    Text("Consultando exportaciones…")
                }
            }

            state.errorMessage != null -> Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(1f),
                contentAlignment = Alignment.Center,
            ) {
                Column(
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(12.dp),
                ) {
                    Text(
                        text = state.errorMessage,
                        color = MaterialTheme.colorScheme.error,
                        textAlign = TextAlign.Center,
                    )
                    Button(onClick = onRefresh) {
                        Text("Intentar nuevamente")
                    }
                }
            }

            else -> {
                Text(
                    text = "Mostrando ${filtradas.size} de ${state.total}",
                    style = MaterialTheme.typography.labelLarge,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
                if (filtradas.isEmpty()) {
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .weight(1f),
                        contentAlignment = Alignment.Center,
                    ) {
                        Text(
                            text = "No se encontraron exportaciones.",
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    }
                } else {
                    LazyColumn(
                        modifier = Modifier.weight(1f),
                        contentPadding = PaddingValues(bottom = 20.dp),
                        verticalArrangement = Arrangement.spacedBy(10.dp),
                    ) {
                        items(
                            items = filtradas,
                            key = { it.id },
                        ) { exportacion ->
                            ExportacionCard(exportacion)
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun ExportacionCard(exportacion: ExportacionMovil) {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = MaterialTheme.shapes.large,
        tonalElevation = 2.dp,
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(6.dp),
        ) {
            Text(
                text = exportacion.nombreArchivo,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
            )
            Text(
                text = "Período: ${exportacion.periodoDescripcion}",
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Text(
                text = "Sucursal: ${exportacion.sucursalNombre}",
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Text(
                text = "Registros: ${exportacion.cantidadRegistros}",
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Text(
                text = "Generado por: ${exportacion.generadoPorNombre}",
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Text(
                text = "Fecha: ${exportacion.fechaGeneracionLegible}",
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Surface(
                shape = MaterialTheme.shapes.small,
                color = MaterialTheme.colorScheme.tertiaryContainer,
            ) {
                Text(
                    text = exportacion.formato,
                    modifier = Modifier.padding(horizontal = 10.dp, vertical = 4.dp),
                    style = MaterialTheme.typography.labelMedium,
                    fontWeight = FontWeight.SemiBold,
                    color = MaterialTheme.colorScheme.onTertiaryContainer,
                )
            }
        }
    }
}

@Composable
private fun NovedadesScreen(
    user: UsuarioMovil,
    state: NovedadesUiState,
    onBack: () -> Unit,
    onRefresh: () -> Unit,
    onSearch: (String) -> Unit,
    onValidate: (Int) -> Unit,
    onAnnul: (Int, String) -> Unit,
    onDismissFeedback: () -> Unit,
) {
    BackHandler(onBack = onBack)
    var validarId by rememberSaveable { mutableStateOf<Int?>(null) }
    var anularId by rememberSaveable { mutableStateOf<Int?>(null) }
    var motivoAnulacion by rememberSaveable { mutableStateOf("") }

    validarId?.let { id ->
        AlertDialog(
            onDismissRequest = { validarId = null },
            title = { Text("Validar novedad") },
            text = {
                Text("La novedad quedará confirmada y ya no podrá editarse.")
            },
            confirmButton = {
                Button(
                    onClick = {
                        validarId = null
                        onValidate(id)
                    },
                ) {
                    Text("Validar")
                }
            },
            dismissButton = {
                TextButton(onClick = { validarId = null }) {
                    Text("Cancelar")
                }
            },
        )
    }

    anularId?.let { id ->
        AlertDialog(
            onDismissRequest = {
                anularId = null
                motivoAnulacion = ""
            },
            title = { Text("Anular novedad") },
            text = {
                Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text("Escribe el motivo. Esta acción quedará registrada.")
                    OutlinedTextField(
                        value = motivoAnulacion,
                        onValueChange = { motivoAnulacion = it.take(500) },
                        modifier = Modifier.fillMaxWidth(),
                        label = { Text("Motivo de anulación") },
                        supportingText = {
                            Text("${motivoAnulacion.trim().length}/500 · mínimo 10")
                        },
                        minLines = 3,
                    )
                }
            },
            confirmButton = {
                Button(
                    enabled = motivoAnulacion.trim().length in 10..500,
                    onClick = {
                        onAnnul(id, motivoAnulacion)
                        anularId = null
                        motivoAnulacion = ""
                    },
                ) {
                    Text("Anular")
                }
            },
            dismissButton = {
                TextButton(
                    onClick = {
                        anularId = null
                        motivoAnulacion = ""
                    },
                ) {
                    Text("Cancelar")
                }
            },
        )
    }

    val filtradas = remember(state.query, state.novedades) {
        val texto = state.query.trim()
        if (texto.isBlank()) {
            state.novedades
        } else {
            state.novedades.filter { novedad ->
                novedad.colaboradorNombre.contains(texto, ignoreCase = true) ||
                    novedad.colaboradorRut.contains(texto, ignoreCase = true) ||
                    novedad.tipoNovedadNombre.contains(texto, ignoreCase = true) ||
                    novedad.periodoDescripcion.contains(texto, ignoreCase = true) ||
                    novedad.sucursalNombre.contains(texto, ignoreCase = true) ||
                    novedad.estado.contains(texto, ignoreCase = true)
            }
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
            .safeDrawingPadding()
            .padding(horizontal = 20.dp, vertical = 12.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        TextButton(onClick = onBack) {
            Text("← Volver al panel")
        }
        Text(
            text = "Novedades",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold,
        )
        Text(
            text = user.sucursal?.nombre ?: "Todas las sucursales autorizadas",
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        OutlinedTextField(
            value = state.query,
            onValueChange = onSearch,
            modifier = Modifier.fillMaxWidth(),
            label = { Text("Buscar persona, RUT, tipo, período o sucursal") },
            singleLine = true,
        )
        (state.actionMessage ?: state.actionError)?.let { feedback ->
            Surface(
                modifier = Modifier.fillMaxWidth(),
                shape = MaterialTheme.shapes.medium,
                color = if (state.actionError == null) {
                    MaterialTheme.colorScheme.primaryContainer
                } else {
                    MaterialTheme.colorScheme.errorContainer
                },
            ) {
                Row(
                    modifier = Modifier.padding(horizontal = 14.dp, vertical = 8.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    Text(
                        text = feedback,
                        modifier = Modifier.weight(1f),
                        color = if (state.actionError == null) {
                            MaterialTheme.colorScheme.onPrimaryContainer
                        } else {
                            MaterialTheme.colorScheme.onErrorContainer
                        },
                    )
                    TextButton(onClick = onDismissFeedback) {
                        Text("Cerrar")
                    }
                }
            }
        }

        when {
            state.loading -> Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(1f),
                contentAlignment = Alignment.Center,
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    CircularProgressIndicator()
                    Spacer(Modifier.height(12.dp))
                    Text("Consultando novedades…")
                }
            }

            state.errorMessage != null -> Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(1f),
                contentAlignment = Alignment.Center,
            ) {
                Column(
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(12.dp),
                ) {
                    Text(
                        text = state.errorMessage,
                        color = MaterialTheme.colorScheme.error,
                        textAlign = TextAlign.Center,
                    )
                    Button(onClick = onRefresh) {
                        Text("Intentar nuevamente")
                    }
                }
            }

            else -> {
                Text(
                    text = "Mostrando ${filtradas.size} de ${state.total}",
                    style = MaterialTheme.typography.labelLarge,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
                if (filtradas.isEmpty()) {
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .weight(1f),
                        contentAlignment = Alignment.Center,
                    ) {
                        Text(
                            text = "No se encontraron novedades.",
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    }
                } else {
                    LazyColumn(
                        modifier = Modifier.weight(1f),
                        contentPadding = PaddingValues(bottom = 20.dp),
                        verticalArrangement = Arrangement.spacedBy(10.dp),
                    ) {
                        items(
                            items = filtradas,
                            key = { it.id },
                        ) { novedad ->
                            NovedadCard(
                                novedad = novedad,
                                canModify = user.puedeModificar,
                                busy = state.workingId == novedad.id,
                                actionsEnabled = state.workingId == null,
                                onValidate = { validarId = novedad.id },
                                onAnnul = {
                                    motivoAnulacion = ""
                                    anularId = novedad.id
                                },
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun NovedadCard(
    novedad: NovedadMovil,
    canModify: Boolean,
    busy: Boolean,
    actionsEnabled: Boolean,
    onValidate: () -> Unit,
    onAnnul: () -> Unit,
) {
    val estadoContainer = when (novedad.estado) {
        "VALIDADA" -> MaterialTheme.colorScheme.primaryContainer
        "ANULADA" -> MaterialTheme.colorScheme.errorContainer
        else -> MaterialTheme.colorScheme.secondaryContainer
    }
    val estadoContent = when (novedad.estado) {
        "VALIDADA" -> MaterialTheme.colorScheme.onPrimaryContainer
        "ANULADA" -> MaterialTheme.colorScheme.onErrorContainer
        else -> MaterialTheme.colorScheme.onSecondaryContainer
    }

    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = MaterialTheme.shapes.large,
        tonalElevation = 2.dp,
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(6.dp),
        ) {
            Text(
                text = novedad.colaboradorNombre,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
            )
            Text(
                text = "${novedad.tipoNovedadNombre} · ${novedad.periodoDescripcion}",
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Text(
                text = "RUT: ${novedad.colaboradorRut}",
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Text(
                text = "Sucursal: ${novedad.sucursalNombre}",
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            novedad.monto?.let {
                Text(
                    text = "Monto: \$$it",
                    fontWeight = FontWeight.SemiBold,
                )
            }
            novedad.cantidad?.let {
                Text(
                    text = "Cantidad: $it",
                    fontWeight = FontWeight.SemiBold,
                )
            }
            if (novedad.fechaInicio != null || novedad.fechaTermino != null) {
                Text(
                    text = listOfNotNull(
                        novedad.fechaInicio,
                        novedad.fechaTermino,
                    ).joinToString(" a ", prefix = "Fechas: "),
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
            if (novedad.observacion.isNotBlank()) {
                Text(
                    text = novedad.observacion,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    style = MaterialTheme.typography.bodySmall,
                )
            }
            Surface(
                shape = MaterialTheme.shapes.small,
                color = estadoContainer,
            ) {
                Text(
                    text = novedad.estado.lowercase()
                        .replaceFirstChar { it.uppercase() },
                    modifier = Modifier.padding(horizontal = 10.dp, vertical = 4.dp),
                    style = MaterialTheme.typography.labelMedium,
                    fontWeight = FontWeight.SemiBold,
                    color = estadoContent,
                )
            }
            if (canModify && (novedad.puedeValidar || novedad.puedeAnular)) {
                HorizontalDivider(modifier = Modifier.padding(vertical = 4.dp))
                if (busy) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                    ) {
                        CircularProgressIndicator(
                            modifier = Modifier.size(20.dp),
                            strokeWidth = 2.dp,
                        )
                        Text("Actualizando novedad…")
                    }
                } else {
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        if (novedad.puedeValidar) {
                            Button(
                                enabled = actionsEnabled,
                                onClick = onValidate,
                            ) {
                                Text("Validar")
                            }
                        }
                        if (novedad.puedeAnular) {
                            OutlinedButton(
                                enabled = actionsEnabled,
                                onClick = onAnnul,
                            ) {
                                Text("Anular")
                            }
                        }
                    }
                }
            }
            if (
                novedad.estado == "ANULADA" &&
                novedad.motivoAnulacion.isNotBlank()
            ) {
                Text(
                    text = "Motivo: ${novedad.motivoAnulacion}",
                    color = MaterialTheme.colorScheme.error,
                    style = MaterialTheme.typography.bodySmall,
                )
            }
        }
    }
}

@Composable
private fun DetailRow(label: String, value: String) {
    Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
        Text(
            text = label,
            style = MaterialTheme.typography.labelMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        Text(
            text = value,
            style = MaterialTheme.typography.bodyLarge,
            fontWeight = FontWeight.SemiBold,
        )
    }
}
