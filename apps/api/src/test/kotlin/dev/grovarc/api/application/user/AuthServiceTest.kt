package dev.grovarc.api.application.user

import dev.grovarc.api.domain.user.RefreshToken
import dev.grovarc.api.domain.user.RefreshTokenRepository
import dev.grovarc.api.domain.user.Role
import dev.grovarc.api.domain.user.User
import dev.grovarc.api.domain.user.UserRepository
import dev.grovarc.api.infrastructure.security.JwtProperties
import dev.grovarc.api.infrastructure.security.JwtProvider
import dev.grovarc.api.interfaces.dto.LoginRequest
import dev.grovarc.api.interfaces.dto.SignupRequest
import org.assertj.core.api.Assertions.assertThat
import org.assertj.core.api.Assertions.assertThatThrownBy
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.extension.ExtendWith
import org.mockito.InjectMocks
import org.mockito.Mock
import org.mockito.junit.jupiter.MockitoExtension
import org.mockito.kotlin.any
import org.mockito.kotlin.whenever
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder
import java.time.LocalDateTime
import java.util.UUID

@ExtendWith(MockitoExtension::class)
class AuthServiceTest {

    @Mock lateinit var userRepository: UserRepository
    @Mock lateinit var refreshTokenRepository: RefreshTokenRepository

    private lateinit var authService: AuthService
    private lateinit var passwordEncoder: BCryptPasswordEncoder
    private lateinit var jwtProvider: JwtProvider

    @BeforeEach
    fun setUp() {
        passwordEncoder = BCryptPasswordEncoder()
        jwtProvider = JwtProvider(
            JwtProperties(
                secret = "test-secret-key-must-be-at-least-256-bits-long-for-hs256-algorithm",
                expirationMs = 3_600_000L,
            )
        )
        authService = AuthService(userRepository, refreshTokenRepository, passwordEncoder, jwtProvider, JwtProperties(
            secret = "test-secret-key-must-be-at-least-256-bits-long-for-hs256-algorithm",
            expirationMs = 3_600_000L,
        ))
    }

    @Test
    fun `회원가입 성공 시 유저 정보를 반환한다`() {
        val request = SignupRequest("test@grovarc.dev", "password123", "tester")
        val savedUser = User(
            id = UUID.randomUUID(),
            email = request.email,
            password = passwordEncoder.encode(request.password),
            nickname = request.nickname,
        )
        whenever(userRepository.existsByEmail(request.email)).thenReturn(false)
        whenever(userRepository.save(any())).thenReturn(savedUser)

        val response = authService.signup(request)

        assertThat(response.email).isEqualTo(request.email)
        assertThat(response.nickname).isEqualTo(request.nickname)
    }

    @Test
    fun `이미 존재하는 이메일로 회원가입 시 예외가 발생한다`() {
        val request = SignupRequest("dup@grovarc.dev", "password123", "tester")
        whenever(userRepository.existsByEmail(request.email)).thenReturn(true)

        assertThatThrownBy { authService.signup(request) }
            .isInstanceOf(IllegalArgumentException::class.java)
            .hasMessage("이미 사용 중인 이메일입니다")
    }

    @Test
    fun `로그인 성공 시 토큰을 반환한다`() {
        val rawPassword = "password123"
        val user = User(
            id = UUID.randomUUID(),
            email = "test@grovarc.dev",
            password = passwordEncoder.encode(rawPassword),
            nickname = "tester",
            role = Role.USER,
        )
        whenever(userRepository.findByEmail(user.email)).thenReturn(user)
        whenever(refreshTokenRepository.save(any())).thenReturn(
            RefreshToken(user = user, token = "token", expiresAt = LocalDateTime.now().plusDays(7))
        )

        val response = authService.login(LoginRequest(user.email, rawPassword))

        assertThat(response.accessToken).isNotBlank()
        assertThat(response.refreshToken).isNotBlank()
    }

    @Test
    fun `잘못된 비밀번호로 로그인 시 예외가 발생한다`() {
        val user = User(
            id = UUID.randomUUID(),
            email = "test@grovarc.dev",
            password = passwordEncoder.encode("correct"),
            nickname = "tester",
        )
        whenever(userRepository.findByEmail(user.email)).thenReturn(user)

        assertThatThrownBy { authService.login(LoginRequest(user.email, "wrong")) }
            .isInstanceOf(IllegalArgumentException::class.java)
            .hasMessage("이메일 또는 비밀번호가 올바르지 않습니다")
    }
}
