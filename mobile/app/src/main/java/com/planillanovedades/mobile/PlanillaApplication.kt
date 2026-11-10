package com.planillanovedades.mobile

import android.app.Application
import com.planillanovedades.mobile.data.remote.ApiService
import com.planillanovedades.mobile.data.remote.AuthInterceptor
import com.planillanovedades.mobile.data.repository.AuthRepository
import com.planillanovedades.mobile.data.repository.ColaboradorRepository
import com.planillanovedades.mobile.data.session.SecureTokenStore
import java.util.concurrent.TimeUnit
import okhttp3.OkHttpClient
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

class PlanillaApplication : Application() {
    lateinit var authRepository: AuthRepository
        private set

    lateinit var colaboradorRepository: ColaboradorRepository
        private set

    override fun onCreate() {
        super.onCreate()

        val tokenStore = SecureTokenStore(this)
        val httpClient = OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(75, TimeUnit.SECONDS)
            .writeTimeout(30, TimeUnit.SECONDS)
            .callTimeout(90, TimeUnit.SECONDS)
            .addInterceptor(AuthInterceptor(tokenStore))
            .build()
        val apiService = Retrofit.Builder()
            .baseUrl(BuildConfig.API_BASE_URL)
            .client(httpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(ApiService::class.java)

        authRepository = AuthRepository(apiService, tokenStore)
        colaboradorRepository = ColaboradorRepository(apiService)
    }
}
