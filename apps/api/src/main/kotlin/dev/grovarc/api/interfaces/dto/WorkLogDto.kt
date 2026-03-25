package dev.grovarc.api.interfaces.dto

import dev.grovarc.api.domain.worklog.Mood
import dev.grovarc.api.domain.worklog.WorkLog
import jakarta.validation.constraints.NotBlank
import jakarta.validation.constraints.NotNull
import jakarta.validation.constraints.Size
import org.springframework.format.annotation.DateTimeFormat
import java.time.LocalDate
import java.time.LocalDateTime
import java.util.UUID

data class WorkLogCreateRequest(
    @field:NotBlank(message = "제목은 필수입니다")
    @field:Size(max = 255, message = "제목은 255자 이하여야 합니다")
    val title: String,

    @field:NotBlank(message = "내용은 필수입니다")
    val content: String,

    @field:NotNull(message = "날짜는 필수입니다")
    val logDate: LocalDate,

    val mood: Mood? = null,
    val tagIds: Set<UUID> = emptySet(),
)

data class WorkLogUpdateRequest(
    @field:NotBlank(message = "제목은 필수입니다")
    @field:Size(max = 255, message = "제목은 255자 이하여야 합니다")
    val title: String,

    @field:NotBlank(message = "내용은 필수입니다")
    val content: String,

    @field:NotNull(message = "날짜는 필수입니다")
    val logDate: LocalDate,

    val mood: Mood? = null,
    val tagIds: Set<UUID> = emptySet(),
)

data class WorkLogResponse(
    val id: UUID,
    val title: String,
    val content: String,
    val logDate: LocalDate,
    val mood: Mood?,
    val tags: List<TagResponse>,
    val createdAt: LocalDateTime,
    val updatedAt: LocalDateTime,
) {
    companion object {
        fun from(workLog: WorkLog) = WorkLogResponse(
            id = workLog.id!!,
            title = workLog.title,
            content = workLog.content,
            logDate = workLog.logDate,
            mood = workLog.mood,
            tags = workLog.tags.map { TagResponse(it.id!!, it.name, it.color) },
            createdAt = workLog.createdAt,
            updatedAt = workLog.updatedAt,
        )
    }
}

data class TagResponse(
    val id: UUID,
    val name: String,
    val color: String?,
)

data class WeeklyStatsResponse(
    val weekStart: LocalDate,
    val weekEnd: LocalDate,
    val totalLogs: Int,
    val dailyStats: List<DailyStat>,
)

data class DailyStat(
    val date: LocalDate,
    val count: Long,
    val avgMoodScore: Double?,
)

data class PageResponse<T>(
    val content: List<T>,
    val page: Int,
    val size: Int,
    val totalElements: Long,
    val totalPages: Int,
)
