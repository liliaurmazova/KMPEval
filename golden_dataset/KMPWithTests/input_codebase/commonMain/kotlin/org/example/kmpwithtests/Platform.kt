package org.example.kmpwithtests

interface Platform {
    val name: String
}

expect fun getPlatform(): Platform