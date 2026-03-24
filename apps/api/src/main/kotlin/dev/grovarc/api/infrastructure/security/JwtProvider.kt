package dev.grovarc.api.infrastructure.security

import io.jsonwebtoken.JwtException
import io.jsonwebtoken.Jwts
import io.jsonwebtoken.security.Keys
import org.springframework.stereotype.Component
import java.util.Date
import java.util.UUID

@Component
class JwtProvider(private val props: JwtProperties) {

    private val key by lazy {
        Keys.hmacShaKeyFor(props.secret.toByteArray())
    }

    fun generateAccessToken(userId: UUID, email: String): String {
        val now = Date()
        return Jwts.builder()
            .subject(userId.toString())
            .claim("email", email)
            .issuedAt(now)
            .expiration(Date(now.time + props.expirationMs))
            .signWith(key)
            .compact()
    }

    fun generateRefreshToken(): String = UUID.randomUUID().toString()

    fun validateToken(token: String): Boolean {
        return try {
            Jwts.parser().verifyWith(key).build().parseSignedClaims(token)
            true
        } catch (e: JwtException) {
            false
        } catch (e: IllegalArgumentException) {
            false
        }
    }

    fun getUserId(token: String): UUID {
        val claims = Jwts.parser().verifyWith(key).build()
            .parseSignedClaims(token).payload
        return UUID.fromString(claims.subject)
    }

    fun getEmail(token: String): String {
        val claims = Jwts.parser().verifyWith(key).build()
            .parseSignedClaims(token).payload
        return claims["email"] as String
    }
}
