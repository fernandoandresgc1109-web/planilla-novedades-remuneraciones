package com.planillanovedades.mobile.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

private val ColorScheme = lightColorScheme(
    primary = GreenPrimary,
    onPrimary = SoftSurface,
    primaryContainer = Color(0xFF9BF3CF),
    onPrimaryContainer = GreenDark,
    secondary = MintSecondary,
    background = SoftBackground,
    onBackground = Ink,
    surface = SoftSurface,
    onSurface = Ink,
)

@Composable
fun PlanillaNovedadesTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = ColorScheme,
        content = content,
    )
}
