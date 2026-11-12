package com.planillanovedades.mobile

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.viewModels
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.planillanovedades.mobile.ui.PlanillaApp
import com.planillanovedades.mobile.ui.auth.AuthViewModel
import com.planillanovedades.mobile.ui.colaboradores.ColaboradoresViewModel
import com.planillanovedades.mobile.ui.exportaciones.ExportacionesViewModel
import com.planillanovedades.mobile.ui.novedades.NovedadesViewModel
import com.planillanovedades.mobile.ui.novedades.NuevaNovedadViewModel
import com.planillanovedades.mobile.ui.periodos.PeriodosViewModel
import com.planillanovedades.mobile.ui.theme.PlanillaNovedadesTheme

class MainActivity : ComponentActivity() {
    private val authViewModel: AuthViewModel by viewModels {
        val repository = (application as PlanillaApplication).authRepository
        AuthViewModel.Factory(repository)
    }

    private val colaboradoresViewModel: ColaboradoresViewModel by viewModels {
        val repository = (application as PlanillaApplication).colaboradorRepository
        ColaboradoresViewModel.Factory(repository)
    }

    private val novedadesViewModel: NovedadesViewModel by viewModels {
        val repository = (application as PlanillaApplication).novedadRepository
        NovedadesViewModel.Factory(repository)
    }

    private val nuevaNovedadViewModel: NuevaNovedadViewModel by viewModels {
        val repository = (application as PlanillaApplication).nuevaNovedadRepository
        NuevaNovedadViewModel.Factory(repository)
    }

    private val periodosViewModel: PeriodosViewModel by viewModels {
        val repository = (application as PlanillaApplication).periodoRepository
        PeriodosViewModel.Factory(repository)
    }

    private val exportacionesViewModel: ExportacionesViewModel by viewModels {
        val repository = (application as PlanillaApplication).exportacionRepository
        ExportacionesViewModel.Factory(repository)
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            PlanillaNovedadesTheme {
                val authState = authViewModel.uiState
                    .collectAsStateWithLifecycle().value
                val colaboradoresState = colaboradoresViewModel.uiState
                    .collectAsStateWithLifecycle().value
                val novedadesState = novedadesViewModel.uiState
                    .collectAsStateWithLifecycle().value
                val nuevaNovedadState = nuevaNovedadViewModel.uiState
                    .collectAsStateWithLifecycle().value
                val periodosState = periodosViewModel.uiState
                    .collectAsStateWithLifecycle().value
                val exportacionesState = exportacionesViewModel.uiState
                    .collectAsStateWithLifecycle().value

                PlanillaApp(
                    state = authState,
                    colaboradoresState = colaboradoresState,
                    novedadesState = novedadesState,
                    nuevaNovedadState = nuevaNovedadState,
                    periodosState = periodosState,
                    exportacionesState = exportacionesState,
                    onLogin = authViewModel::login,
                    onLogout = {
                        colaboradoresViewModel.clear()
                        novedadesViewModel.clear()
                        nuevaNovedadViewModel.clear()
                        periodosViewModel.clear()
                        exportacionesViewModel.clear()
                        authViewModel.logout()
                    },
                    onDismissError = authViewModel::dismissError,
                    onOpenColaboradores = {
                        colaboradoresViewModel.load()
                    },
                    onRefreshColaboradores = {
                        colaboradoresViewModel.load(force = true)
                    },
                    onSearchColaboradores = colaboradoresViewModel::updateQuery,
                    onOpenNovedades = {
                        novedadesViewModel.load()
                    },
                    onRefreshNovedades = {
                        novedadesViewModel.load(force = true)
                    },
                    onSearchNovedades = novedadesViewModel::updateQuery,
                    onValidarNovedad = novedadesViewModel::validar,
                    onAnularNovedad = novedadesViewModel::anular,
                    onDismissNovedadFeedback = {
                        novedadesViewModel.dismissActionFeedback()
                    },
                    onOpenNuevaNovedad = {
                        nuevaNovedadViewModel.loadOptions()
                    },
                    onRetryNuevaNovedad = {
                        nuevaNovedadViewModel.loadOptions(force = true)
                    },
                    onDismissNuevaNovedadError = {
                        nuevaNovedadViewModel.dismissError()
                    },
                    onSubmitNuevaNovedad = nuevaNovedadViewModel::submit,
                    onCreatedNovedad = {
                        nuevaNovedadViewModel.clear()
                        novedadesViewModel.load(force = true)
                    },
                    onOpenPeriodos = {
                        periodosViewModel.load()
                    },
                    onRefreshPeriodos = {
                        periodosViewModel.load(force = true)
                    },
                    onSearchPeriodos = periodosViewModel::updateQuery,
                    onOpenExportaciones = {
                        exportacionesViewModel.load()
                    },
                    onRefreshExportaciones = {
                        exportacionesViewModel.load(force = true)
                    },
                    onSearchExportaciones = exportacionesViewModel::updateQuery,
                )
            }
        }
    }
}
