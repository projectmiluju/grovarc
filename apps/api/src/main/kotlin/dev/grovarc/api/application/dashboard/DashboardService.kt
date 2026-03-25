package dev.grovarc.api.application.dashboard

import dev.grovarc.api.domain.retrospective.RetrospectiveRepository
import dev.grovarc.api.domain.user.User
import dev.grovarc.api.domain.user.UserRepository
import dev.grovarc.api.domain.worklog.WorkLogRepository
import dev.grovarc.api.infrastructure.cache.CacheConfig
import dev.grovarc.api.interfaces.dto.*
import org.springframework.cache.annotation.Cacheable
import org.springframework.data.domain.PageRequest
import org.springframework.data.domain.Sort
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.time.DayOfWeek
import java.time.LocalDate
import java.time.temporal.TemporalAdjusters
import java.util.UUID

@Service
@Transactional(readOnly = true)
class DashboardService(
    private val userRepository: UserRepository,
    private val workLogRepository: WorkLogRepository,
    private val retrospectiveRepository: RetrospectiveRepository,
) {

    @Cacheable(cacheNames = [CacheConfig.DASHBOARD], key = "#userId")
    fun getDashboard(userId: UUID): DashboardResponse {
        val user = userRepository.findById(userId)
            .orElseThrow { NoSuchElementException("유저를 찾을 수 없습니다") }

        val today = LocalDate.now()
        val weekStart = today.with(TemporalAdjusters.previousOrSame(DayOfWeek.MONDAY))
        val monthStart = today.withDayOfMonth(1)

        val allLogs = workLogRepository.findAllByUserOrderByLogDateDesc(user, PageRequest.of(0, Int.MAX_VALUE, Sort.by("logDate").descending()))
        val totalLogs = allLogs.totalElements

        val thisWeekLogs = workLogRepository.findByUserAndDateRange(user, weekStart, today).size
        val thisMonthLogs = workLogRepository.findByUserAndDateRange(user, monthStart, today).size

        val logDates = allLogs.content.map { it.logDate }.toSortedSet(compareByDescending { it })
        val (currentStreak, longestStreak) = calculateStreaks(logDates, today)

        val recentLogs = allLogs.content.take(5).map { log ->
            WorkLogSummary(
                id = log.id.toString(),
                title = log.title,
                logDate = log.logDate,
                mood = log.mood?.name,
                tagCount = log.tags.size,
            )
        }

        val recentRetros = retrospectiveRepository
            .findAllByUserOrderByCreatedAtDesc(user, PageRequest.of(0, 3))
            .content.map { retro ->
                RetrospectiveSummary(
                    id = retro.id.toString(),
                    title = retro.title,
                    periodFrom = retro.periodFrom,
                    periodTo = retro.periodTo,
                    status = retro.status.name,
                )
            }

        return DashboardResponse(
            totalLogs = totalLogs,
            currentStreak = currentStreak,
            longestStreak = longestStreak,
            thisWeekLogs = thisWeekLogs,
            thisMonthLogs = thisMonthLogs,
            recentLogs = recentLogs,
            recentRetrospectives = recentRetros,
        )
    }

    private fun calculateStreaks(dates: Set<LocalDate>, today: LocalDate): Pair<Int, Int> {
        if (dates.isEmpty()) return Pair(0, 0)

        val dateSet = dates.toHashSet()
        var currentStreak = 0
        var check = today
        while (dateSet.contains(check)) {
            currentStreak++
            check = check.minusDays(1)
        }

        var longestStreak = 0
        var streak = 1
        val sorted = dates.sortedDescending()
        for (i in 1 until sorted.size) {
            if (sorted[i - 1].minusDays(1) == sorted[i]) {
                streak++
                if (streak > longestStreak) longestStreak = streak
            } else {
                streak = 1
            }
        }
        longestStreak = maxOf(longestStreak, currentStreak, if (sorted.isNotEmpty()) 1 else 0)

        return Pair(currentStreak, longestStreak)
    }
}
