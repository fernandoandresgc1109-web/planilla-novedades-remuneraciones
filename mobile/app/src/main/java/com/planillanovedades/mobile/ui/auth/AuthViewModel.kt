package com.planillanovedades.mobile.ui.auth

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.planillanovedades.mobile.data.model.UsuarioMovil
import com.planillanovedades.mobile.data.repository.AuthRepository
import com.planillanovedades.mobile.data.repository.LoginResult
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class AuthUiState(
    val restoringSession: Boolean = true,
    val working: Boolean = false,
    val user: UsuarioMovil? = null,
    val errorMessage: String? = null,
)

class AuthViewModel(
    private val repository: AuthRepository,
) : ViewModel() {
    private val _uiState = MutableStateFlow(AuthUiState())
    val uiState: StateFlow<AuthUiState> = _uiState.asStateFlow()

    init {
        viewModelScope.launch {
            val restoredUser = repository.restoreSession()
            _uiState.update {
                it.copy(restoringSession = false, user = restoredUser)
            }
        }
    }

    fun login(username: String, password: String) {
        if (_uiState.value.working) return

        if (username.isBlank() || password.isBlank()) {
            _uiState.update {
                it.copy(errorMessage = "Escribe el usuario y la contraseña.")
            }
            return
        }

        viewModelScope.launch {
            _uiState.update { it.copy(working = true, errorMessage = null) }
            when (val result = repository.login(username, password)) {
                is LoginResult.Success -> _uiState.update {
                    it.copy(working = false, user = result.user)
                }

                is LoginResult.Error -> _uiState.update {
                    it.copy(working = false, errorMessage = result.message)
                }
            }
        }
    }

    fun logout() {
        if (_uiState.value.working) return

        viewModelScope.launch {
            _uiState.update { it.copy(working = true, errorMessage = null) }
            runCatching { repository.logout() }
            _uiState.value = AuthUiState(restoringSession = false)
        }
    }

    fun dismissError() {
        _uiState.update { it.copy(errorMessage = null) }
    }

    class Factory(
        private val repository: AuthRepository,
    ) : ViewModelProvider.Factory {
        @Suppress("UNCHECKED_CAST")
        override fun <T : ViewModel> create(modelClass: Class<T>): T {
            require(modelClass.isAssignableFrom(AuthViewModel::class.java))
            return AuthViewModel(repository) as T
        }
    }
}
