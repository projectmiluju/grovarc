package dev.grovarc.api.interfaces.rest

import dev.grovarc.api.application.tag.TagService
import dev.grovarc.api.interfaces.dto.TagCreateRequest
import dev.grovarc.api.interfaces.dto.TagDetailResponse
import jakarta.validation.Valid
import org.springframework.http.HttpStatus
import org.springframework.http.ResponseEntity
import org.springframework.security.core.annotation.AuthenticationPrincipal
import org.springframework.web.bind.annotation.*
import java.util.UUID

@RestController
@RequestMapping("/api/v1/tags")
class TagController(private val tagService: TagService) {

    @GetMapping
    fun getAll(
        @AuthenticationPrincipal userId: UUID,
    ): ResponseEntity<List<TagDetailResponse>> =
        ResponseEntity.ok(tagService.getAll(userId))

    @PostMapping
    fun create(
        @AuthenticationPrincipal userId: UUID,
        @Valid @RequestBody request: TagCreateRequest,
    ): ResponseEntity<TagDetailResponse> =
        ResponseEntity.status(HttpStatus.CREATED).body(tagService.create(userId, request))

    @DeleteMapping("/{tagId}")
    fun delete(
        @AuthenticationPrincipal userId: UUID,
        @PathVariable tagId: UUID,
    ): ResponseEntity<Unit> {
        tagService.delete(userId, tagId)
        return ResponseEntity.noContent().build()
    }
}
