package dev.grovarc.api.interfaces.rest

import dev.grovarc.api.application.dashboard.DashboardService
import dev.grovarc.api.interfaces.dto.DashboardResponse
import org.springframework.http.ResponseEntity
import org.springframework.security.core.annotation.AuthenticationPrincipal
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController
import java.util.UUID

@RestController
@RequestMapping("/api/v1/dashboard")
class DashboardController(private val dashboardService: DashboardService) {

    @GetMapping
    fun getDashboard(
        @AuthenticationPrincipal userId: UUID,
    ): ResponseEntity<DashboardResponse> =
        ResponseEntity.ok(dashboardService.getDashboard(userId))
}
