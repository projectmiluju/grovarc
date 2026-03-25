package dev.grovarc.api.interfaces.dto

import dev.grovarc.api.domain.tag.Tag
import jakarta.validation.constraints.NotBlank
import jakarta.validation.constraints.Pattern
import jakarta.validation.constraints.Size
import java.time.LocalDateTime
import java.util.UUID

data class TagCreateRequest(
    @field:NotBlank(message = "태그 이름은 필수입니다")
    @field:Size(min = 1, max = 20, message = "태그 이름은 1~20자여야 합니다")
    val name: String,

    @field:Pattern(regexp = "^#[0-9A-Fa-f]{6}$", message = "색상은 #RRGGBB 형식이어야 합니다")
    val color: String? = null,
)

data class TagDetailResponse(
    val id: UUID,
    val name: String,
    val color: String?,
    val createdAt: LocalDateTime,
) {
    companion object {
        fun from(tag: Tag) = TagDetailResponse(
            id = tag.id!!,
            name = tag.name,
            color = tag.color,
            createdAt = tag.createdAt,
        )
    }
}
