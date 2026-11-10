package com.planillanovedades.mobile

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.viewModels
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.planillanovedades.mobile.ui.PlanillaApp
import com.planillanovedades.mobile.ui.auth.AuthViewModel
import com.planillanovedades.mobile.ui.theme.PlanillaNovedadesTheme

class MainActivity : ComponentActivity() {
    private val authViewModel: AuthViewModel by viewModels {
        val repository = (application as PlanillaApplication).authRepository
        AuthViewModel.Factory(repository)
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            PlanillaNovedadesTheme {
                val state = authViewModel.uiState.collectAsStateWithLifecycle().value
                PlanillaApp(
                    state = state,
                    onLogin = authViewModel::login,
                    onLogout = authViewModel::logout,
                    onDismissError = authViewModel::dismissError,
                )
            }
        }
    }
}
