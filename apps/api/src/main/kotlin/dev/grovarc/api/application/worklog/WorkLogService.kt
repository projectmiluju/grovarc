package dev.grovarc.api.application.worklog

import dev.grovarc.api.domain.tag.TagRepository
import dev.grovarc.api.domain.user.User
import dev.grovarc.api.domain.user.UserRepository
import dev.grovarc.api.domain.worklog.WorkLog
import dev.grovarc.api.domain.worklog.WorkLogRepository
import dev.grovarc.api.infrastructure.kafka.WorkLogEventPublisher
import dev.grovarc.api.interfaces.dto.*
import org.springframework.data.domain.Pageable
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.time.DayOfWeek
import java.time.LocalDate
import java.time.temporal.TemporalAdjusters
import java.util.UUID

@Service
@Transactional
class WorkLogService(
    private val workLogRepository: WorkLogRepository,
    private val userRepository: UserRepository,
    private val tagRepository: TagRepository,
    private val eventPublisher: WorkLogEventPublisher,
) {

    fun create(userId: UUID, request: WorkLogCreateRequest): WorkLogResponse {
        val user = findUser(userId)
        val tags = resolveTagsForUser(request.tagIds, user)

        val workLog = workLogRepository.save(
            WorkLog(
                user = user,
                title = request.title,
                content = request.content,
                logDate = request.logDate,
                mood = request.mood,
                tags = tags.toMutableSet(),
            )
        )

        eventPublisher.publishWorkLogSaved(workLog.id!!, userId, workLog.logDate)
        return WorkLogResponse.from(workLog)
    }

    @Transactional(readOnly = true)
    fun getList(userId: UUID, pageable: Pageable): PageResponse<WorkLogResponse> {
        val user = findUser(userId)
        val page = workLogRepository.findAllByUserOrderByLogDateDesc(user, pageable)
        return PageResponse(
            content = page.content.map { WorkLogResponse.from(it) },
            page = page.number,
            size = page.size,
            totalElements = page.totalElements,
            totalPages = page.totalPages,
        )
    }

    @Transactional(readOnly = true)
    fun getOne(userId: UUID, logId: UUID): WorkLogResponse {
        val user = findUser(userId)
        val workLog = workLogRepository.findByIdAndUser(logId, user)
            ?: throw NoSuchElementException("작업 로그를 찾을 수 없습니다")
        return WorkLogResponse.from(workLog)
    }

    fun update(userId: UUID, logId: UUID, request: WorkLogUpdateRequest): WorkLogResponse {
        val user = findUser(userId)
        val workLog = workLogRepository.findByIdAndUser(logId, user)
            ?: throw NoSuchElementException("작업 로그를 찾을 수 없습니다")
        val tags = resolveTagsForUser(request.tagIds, user)

        workLog.update(request.title, request.content, request.logDate, request.mood)
        workLog.replaceTags(tags)
        return WorkLogResponse.from(workLog)
    }

    fun delete(userId: UUID, logId: UUID) {
        val user = findUser(userId)
        val workLog = workLogRepository.findByIdAndUser(logId, user)
            ?: throw NoSuchElementException("작업 로그를 찾을 수 없습니다")
        workLogRepository.delete(workLog)
    }

    @Transactional(readOnly = true)
    fun getWeeklyStats(userId: UUID, date: LocalDate): WeeklyStatsResponse {
        val user = findUser(userId)
        val weekStart = date.with(TemporalAdjusters.previousOrSame(DayOfWeek.MONDAY))
        val weekEnd = weekStart.plusDays(6)

        val rawStats = workLogRepository.findDailyStats(user, weekStart, weekEnd)
        val dailyStats = rawStats.map { row ->
            DailyStat(
                date = row[0] as LocalDate,
                count = row[1] as Long,
                avgMoodScore = (row[2] as? Double),
            )
        }

        return WeeklyStatsResponse(
            weekStart = weekStart,
            weekEnd = weekEnd,
            totalLogs = dailyStats.sumOf { it.count }.toInt(),
            dailyStats = dailyStats,
        )
    }

    private fun findUser(userId: UUID): User =
        userRepository.findById(userId).orElseThrow { NoSuchElementException("유저를 찾을 수 없습니다") }

    private fun resolveTagsForUser(tagIds: Set<UUID>, user: User) =
        tagIds.mapNotNull { tagRepository.findByIdAndUser(it, user) }.toSet()
}
