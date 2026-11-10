package com.planillanovedades.mobile.data.session

import android.content.Context
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey

class SecureTokenStore(context: Context) : TokenStore {
    private val preferences = EncryptedSharedPreferences.create(
        context,
        FILE_NAME,
        MasterKey.Builder(context)
            .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
            .build(),
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM,
    )

    override fun read(): String? = preferences.getString(TOKEN_KEY, null)

    override fun save(token: String) {
        preferences.edit().putString(TOKEN_KEY, token).apply()
    }

    override fun clear() {
        preferences.edit().remove(TOKEN_KEY).apply()
    }

    private companion object {
        const val FILE_NAME = "planilla_secure_session"
        const val TOKEN_KEY = "auth_token"
    }
}
