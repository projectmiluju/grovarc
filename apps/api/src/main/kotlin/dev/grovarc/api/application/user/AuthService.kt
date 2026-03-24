package dev.grovarc.api.application.user

import dev.grovarc.api.domain.user.RefreshToken
import dev.grovarc.api.domain.user.RefreshTokenRepository
import dev.grovarc.api.domain.user.User
import dev.grovarc.api.domain.user.UserRepository
import dev.grovarc.api.infrastructure.security.JwtProperties
import dev.grovarc.api.infrastructure.security.JwtProvider
import dev.grovarc.api.interfaces.dto.LoginRequest
import dev.grovarc.api.interfaces.dto.SignupRequest
import dev.grovarc.api.interfaces.dto.SignupResponse
import dev.grovarc.api.interfaces.dto.TokenResponse
import org.springframework.security.crypto.password.PasswordEncoder
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.time.LocalDateTime

@Service
@Transactional
class AuthService(
    private val userRepository: UserRepository,
    private val refreshTokenRepository: RefreshTokenRepository,
    private val passwordEncoder: PasswordEncoder,
    private val jwtProvider: JwtProvider,
    private val jwtProperties: JwtProperties,
) {

    fun signup(request: SignupRequest): SignupResponse {
        if (userRepository.existsByEmail(request.email)) {
            throw IllegalArgumentException("이미 사용 중인 이메일입니다")
        }

        val user = userRepository.save(
            User(
                email = request.email,
                password = passwordEncoder.encode(request.password),
                nickname = request.nickname,
            )
        )

        return SignupResponse(
            id = user.id.toString(),
            email = user.email,
            nickname = user.nickname,
        )
    }

    fun login(request: LoginRequest): TokenResponse {
        val user = userRepository.findByEmail(request.email)
            ?: throw IllegalArgumentException("이메일 또는 비밀번호가 올바르지 않습니다")

        if (!passwordEncoder.matches(request.password, user.password)) {
            throw IllegalArgumentException("이메일 또는 비밀번호가 올바르지 않습니다")
        }

        return issueTokens(user)
    }

    fun refresh(refreshTokenValue: String): TokenResponse {
        val refreshToken = refreshTokenRepository.findByToken(refreshTokenValue)
            ?: throw IllegalArgumentException("유효하지 않은 Refresh Token입니다")

        if (refreshToken.isExpired()) {
            refreshTokenRepository.delete(refreshToken)
            throw IllegalArgumentException("만료된 Refresh Token입니다")
        }

        refreshTokenRepository.delete(refreshToken)
        return issueTokens(refreshToken.user)
    }

    private fun issueTokens(user: User): TokenResponse {
        refreshTokenRepository.deleteByUser(user)

        val accessToken = jwtProvider.generateAccessToken(user.id!!, user.email)
        val rawRefreshToken = jwtProvider.generateRefreshToken()

        refreshTokenRepository.save(
            RefreshToken(
                user = user,
                token = rawRefreshToken,
                expiresAt = LocalDateTime.now().plusSeconds(jwtProperties.refreshExpirationMs / 1000),
            )
        )

        return TokenResponse(
            accessToken = accessToken,
            refreshToken = rawRefreshToken,
        )
    }
}
