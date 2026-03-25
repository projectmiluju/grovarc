package dev.grovarc.api.interfaces.dto

import dev.grovarc.api.domain.retrospective.Retrospective
import dev.grovarc.api.domain.retrospective.RetrospectiveStatus
import jakarta.validation.constraints.NotBlank
import java.time.LocalDate
import java.time.LocalDateTime
import java.util.UUID

data class RetrospectiveUpdateRequest(
    @field:NotBlank(message = "제목은 필수입니다")
    val title: String,

    @field:NotBlank(message = "내용은 필수입니다")
    val content: String,
)

data class RetrospectiveResponse(
    val id: UUID,
    val title: String,
    val content: String,
    val periodFrom: LocalDate,
    val periodTo: LocalDate,
    val status: RetrospectiveStatus,
    val createdAt: LocalDateTime,
    val updatedAt: LocalDateTime,
) {
    companion object {
        fun from(r: Retrospective) = RetrospectiveResponse(
            id = r.id!!,
            title = r.title,
            content = r.content,
            periodFrom = r.periodFrom,
            periodTo = r.periodTo,
            status = r.status,
            createdAt = r.createdAt,
            updatedAt = r.updatedAt,
        )
    }
}
