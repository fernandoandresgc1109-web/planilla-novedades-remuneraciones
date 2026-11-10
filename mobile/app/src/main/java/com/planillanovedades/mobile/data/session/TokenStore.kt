package com.planillanovedades.mobile.data.session

interface TokenStore {
    fun read(): String?
    fun save(token: String)
    fun clear()
}
