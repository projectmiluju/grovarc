package dev.grovarc.api.infrastructure.security

import org.springframework.boot.context.properties.ConfigurationProperties

@ConfigurationProperties(prefix = "jwt")
data class JwtProperties(
    val secret: String,
    val expirationMs: Long,
    val refreshExpirationMs: Long = 604_800_000L, // 7일
)
