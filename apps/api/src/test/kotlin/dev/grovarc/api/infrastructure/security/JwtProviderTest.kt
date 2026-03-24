package dev.grovarc.api.infrastructure.security

import org.assertj.core.api.Assertions.assertThat
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import java.util.UUID

class JwtProviderTest {

    private lateinit var jwtProvider: JwtProvider

    @BeforeEach
    fun setUp() {
        val props = JwtProperties(
            secret = "test-secret-key-must-be-at-least-256-bits-long-for-hs256-algorithm",
            expirationMs = 3_600_000L,
        )
        jwtProvider = JwtProvider(props)
    }

    @Test
    fun `액세스 토큰 생성 후 검증이 성공한다`() {
        val userId = UUID.randomUUID()
        val email = "test@grovarc.dev"

        val token = jwtProvider.generateAccessToken(userId, email)

        assertThat(jwtProvider.validateToken(token)).isTrue()
        assertThat(jwtProvider.getUserId(token)).isEqualTo(userId)
        assertThat(jwtProvider.getEmail(token)).isEqualTo(email)
    }

    @Test
    fun `잘못된 토큰은 검증에 실패한다`() {
        assertThat(jwtProvider.validateToken("invalid.token.value")).isFalse()
    }

    @Test
    fun `만료된 토큰은 검증에 실패한다`() {
        val expiredProps = JwtProperties(
            secret = "test-secret-key-must-be-at-least-256-bits-long-for-hs256-algorithm",
            expirationMs = -1L,
        )
        val expiredProvider = JwtProvider(expiredProps)
        val token = expiredProvider.generateAccessToken(UUID.randomUUID(), "test@grovarc.dev")

        assertThat(expiredProvider.validateToken(token)).isFalse()
    }

    @Test
    fun `Refresh Token은 UUID 형식으로 생성된다`() {
        val token = jwtProvider.generateRefreshToken()
        assertThat(token).isNotBlank()
        assertThat(UUID.fromString(token)).isNotNull()
    }
}
