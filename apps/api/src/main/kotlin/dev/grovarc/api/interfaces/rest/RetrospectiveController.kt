package dev.grovarc.api.interfaces.rest

import dev.grovarc.api.application.retrospective.RetrospectiveService
import dev.grovarc.api.interfaces.dto.PageResponse
import dev.grovarc.api.interfaces.dto.RetrospectiveResponse
import dev.grovarc.api.interfaces.dto.RetrospectiveUpdateRequest
import jakarta.validation.Valid
import org.springframework.data.domain.PageRequest
import org.springframework.data.domain.Sort
import org.springframework.http.ResponseEntity
import org.springframework.security.core.annotation.AuthenticationPrincipal
import org.springframework.web.bind.annotation.*
import java.util.UUID

@RestController
@RequestMapping("/api/v1/retrospectives")
class RetrospectiveController(private val retrospectiveService: RetrospectiveService) {

    @GetMapping
    fun getList(
        @AuthenticationPrincipal userId: UUID,
        @RequestParam(defaultValue = "0") page: Int,
        @RequestParam(defaultValue = "10") size: Int,
    ): ResponseEntity<PageResponse<RetrospectiveResponse>> {
        val pageable = PageRequest.of(page, size, Sort.by("createdAt").descending())
        return ResponseEntity.ok(retrospectiveService.getList(userId, pageable))
    }

    @GetMapping("/{retroId}")
    fun getOne(
        @AuthenticationPrincipal userId: UUID,
        @PathVariable retroId: UUID,
    ): ResponseEntity<RetrospectiveResponse> =
        ResponseEntity.ok(retrospectiveService.getOne(userId, retroId))

    @PutMapping("/{retroId}")
    fun update(
        @AuthenticationPrincipal userId: UUID,
        @PathVariable retroId: UUID,
        @Valid @RequestBody request: RetrospectiveUpdateRequest,
    ): ResponseEntity<RetrospectiveResponse> =
        ResponseEntity.ok(retrospectiveService.update(userId, retroId, request))

    @PostMapping("/{retroId}/publish")
    fun publish(
        @AuthenticationPrincipal userId: UUID,
        @PathVariable retroId: UUID,
    ): ResponseEntity<RetrospectiveResponse> =
        ResponseEntity.ok(retrospectiveService.publish(userId, retroId))
}
