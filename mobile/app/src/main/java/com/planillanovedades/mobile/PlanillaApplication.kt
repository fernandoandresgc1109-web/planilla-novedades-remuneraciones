package com.planillanovedades.mobile

import android.app.Application
import com.planillanovedades.mobile.data.remote.ApiService
import com.planillanovedades.mobile.data.remote.AuthInterceptor
import com.planillanovedades.mobile.data.repository.AuthRepository
import com.planillanovedades.mobile.data.session.SecureTokenStore
import okhttp3.OkHttpClient
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

class PlanillaApplication : Application() {
    lateinit var authRepository: AuthRepository
        private set

    override fun onCreate() {
        super.onCreate()

        val tokenStore = SecureTokenStore(this)
        val httpClient = OkHttpClient.Builder()
            .addInterceptor(AuthInterceptor(tokenStore))
            .build()
        val apiService = Retrofit.Builder()
            .baseUrl(BuildConfig.API_BASE_URL)
            .client(httpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(ApiService::class.java)

        authRepository = AuthRepository(apiService, tokenStore)
    }
}
