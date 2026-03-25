package dev.grovarc.api.application.dashboard

import dev.grovarc.api.domain.retrospective.RetrospectiveRepository
import dev.grovarc.api.domain.user.User
import dev.grovarc.api.domain.user.UserRepository
import dev.grovarc.api.domain.worklog.WorkLog
import dev.grovarc.api.domain.worklog.WorkLogRepository
import org.assertj.core.api.Assertions.assertThat
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.extension.ExtendWith
import org.mockito.Mock
import org.mockito.junit.jupiter.MockitoExtension
import org.mockito.kotlin.any
import org.mockito.kotlin.whenever
import org.springframework.data.domain.PageImpl
import org.springframework.data.domain.PageRequest
import java.time.LocalDate
import java.util.Optional
import java.util.UUID

@ExtendWith(MockitoExtension::class)
class DashboardServiceTest {

    @Mock lateinit var userRepository: UserRepository
    @Mock lateinit var workLogRepository: WorkLogRepository
    @Mock lateinit var retrospectiveRepository: RetrospectiveRepository

    private lateinit var dashboardService: DashboardService
    private lateinit var testUser: User
    private val userId = UUID.randomUUID()

    @BeforeEach
    fun setUp() {
        dashboardService = DashboardService(userRepository, workLogRepository, retrospectiveRepository)
        testUser = User(id = userId, email = "test@grovarc.dev", password = "hashed", nickname = "tester")
        whenever(userRepository.findById(userId)).thenReturn(Optional.of(testUser))
        whenever(retrospectiveRepository.findAllByUserOrderByCreatedAtDesc(any(), any()))
            .thenReturn(PageImpl(emptyList()))
    }

    private fun makeLog(daysAgo: Long) = WorkLog(
        id = UUID.randomUUID(), user = testUser,
        title = "log", content = "content",
        logDate = LocalDate.now().minusDays(daysAgo),
    )

    @Test
    fun `로그가 없을 때 스트릭은 0이다`() {
        whenever(workLogRepository.findAllByUserOrderByLogDateDesc(any(), any()))
            .thenReturn(PageImpl(emptyList()))
        whenever(workLogRepository.findByUserAndDateRange(any(), any(), any()))
            .thenReturn(emptyList())

        val result = dashboardService.getDashboard(userId)

        assertThat(result.currentStreak).isEqualTo(0)
        assertThat(result.longestStreak).isEqualTo(0)
        assertThat(result.totalLogs).isEqualTo(0)
    }

    @Test
    fun `오늘 포함 연속 3일 로그 작성 시 스트릭은 3이다`() {
        val logs = listOf(makeLog(0), makeLog(1), makeLog(2))
        whenever(workLogRepository.findAllByUserOrderByLogDateDesc(any(), any()))
            .thenReturn(PageImpl(logs))
        whenever(workLogRepository.findByUserAndDateRange(any(), any(), any()))
            .thenReturn(logs)

        val result = dashboardService.getDashboard(userId)

        assertThat(result.currentStreak).isEqualTo(3)
        assertThat(result.longestStreak).isEqualTo(3)
    }

    @Test
    fun `어제부터 끊긴 경우 현재 스트릭은 0이다`() {
        val logs = listOf(makeLog(1), makeLog(2), makeLog(3))
        whenever(workLogRepository.findAllByUserOrderByLogDateDesc(any(), any()))
            .thenReturn(PageImpl(logs))
        whenever(workLogRepository.findByUserAndDateRange(any(), any(), any()))
            .thenReturn(emptyList())

        val result = dashboardService.getDashboard(userId)

        assertThat(result.currentStreak).isEqualTo(0)
        assertThat(result.longestStreak).isEqualTo(3)
    }

    @Test
    fun `이번주 로그 수가 정확히 집계된다`() {
        val allLogs = listOf(makeLog(0), makeLog(1))
        whenever(workLogRepository.findAllByUserOrderByLogDateDesc(any(), any()))
            .thenReturn(PageImpl(allLogs))
        whenever(workLogRepository.findByUserAndDateRange(any(), any(), any()))
            .thenReturn(allLogs)

        val result = dashboardService.getDashboard(userId)

        assertThat(result.thisWeekLogs).isEqualTo(2)
    }

    @Test
    fun `최근 로그는 최대 5개까지 반환한다`() {
        val logs = (0L..9L).map { makeLog(it) }
        whenever(workLogRepository.findAllByUserOrderByLogDateDesc(any(), any()))
            .thenReturn(PageImpl(logs))
        whenever(workLogRepository.findByUserAndDateRange(any(), any(), any()))
            .thenReturn(logs.take(2))

        val result = dashboardService.getDashboard(userId)

        assertThat(result.recentLogs).hasSize(5)
    }
}
