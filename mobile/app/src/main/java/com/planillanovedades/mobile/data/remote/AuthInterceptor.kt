package com.planillanovedades.mobile.data.remote

import com.planillanovedades.mobile.data.session.TokenStore
import okhttp3.Interceptor
import okhttp3.Response

class AuthInterceptor(
    private val tokenStore: TokenStore,
) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val originalRequest = chain.request()
        val token = tokenStore.read()
        val authenticatedRequest = if (
            token.isNullOrBlank() || originalRequest.header("Authorization") != null
        ) {
            originalRequest
        } else {
            originalRequest.newBuilder()
                .header("Authorization", "Token $token")
                .build()
        }

        return chain.proceed(authenticatedRequest)
    }
}
