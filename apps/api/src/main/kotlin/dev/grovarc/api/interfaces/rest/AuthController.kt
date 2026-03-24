package dev.grovarc.api.interfaces.rest

import dev.grovarc.api.application.user.AuthService
import dev.grovarc.api.interfaces.dto.LoginRequest
import dev.grovarc.api.interfaces.dto.RefreshRequest
import dev.grovarc.api.interfaces.dto.SignupRequest
import dev.grovarc.api.interfaces.dto.SignupResponse
import dev.grovarc.api.interfaces.dto.TokenResponse
import jakarta.validation.Valid
import org.springframework.http.HttpStatus
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.PostMapping
import org.springframework.web.bind.annotation.RequestBody
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController

@RestController
@RequestMapping("/api/v1/auth")
class AuthController(private val authService: AuthService) {

    @PostMapping("/signup")
    fun signup(@Valid @RequestBody request: SignupRequest): ResponseEntity<SignupResponse> {
        return ResponseEntity.status(HttpStatus.CREATED).body(authService.signup(request))
    }

    @PostMapping("/login")
    fun login(@Valid @RequestBody request: LoginRequest): ResponseEntity<TokenResponse> {
        return ResponseEntity.ok(authService.login(request))
    }

    @PostMapping("/refresh")
    fun refresh(@Valid @RequestBody request: RefreshRequest): ResponseEntity<TokenResponse> {
        return ResponseEntity.ok(authService.refresh(request.refreshToken))
    }
}
