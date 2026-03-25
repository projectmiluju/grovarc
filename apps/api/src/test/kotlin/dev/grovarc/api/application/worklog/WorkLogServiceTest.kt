package dev.grovarc.api.application.worklog

import dev.grovarc.api.domain.tag.Tag
import dev.grovarc.api.domain.tag.TagRepository
import dev.grovarc.api.domain.user.User
import dev.grovarc.api.domain.user.UserRepository
import dev.grovarc.api.domain.worklog.Mood
import dev.grovarc.api.domain.worklog.WorkLog
import dev.grovarc.api.domain.worklog.WorkLogRepository
import dev.grovarc.api.infrastructure.kafka.WorkLogEventPublisher
import dev.grovarc.api.interfaces.dto.WorkLogCreateRequest
import dev.grovarc.api.interfaces.dto.WorkLogUpdateRequest
import org.assertj.core.api.Assertions.assertThat
import org.assertj.core.api.Assertions.assertThatThrownBy
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.extension.ExtendWith
import org.mockito.Mock
import org.mockito.junit.jupiter.MockitoExtension
import org.mockito.kotlin.any
import org.mockito.kotlin.never
import org.mockito.kotlin.verify
import org.mockito.kotlin.whenever
import org.springframework.data.domain.PageImpl
import org.springframework.data.domain.PageRequest
import java.time.LocalDate
import java.util.Optional
import java.util.UUID

@ExtendWith(MockitoExtension::class)
class WorkLogServiceTest {

    @Mock lateinit var workLogRepository: WorkLogRepository
    @Mock lateinit var userRepository: UserRepository
    @Mock lateinit var tagRepository: TagRepository
    @Mock lateinit var eventPublisher: WorkLogEventPublisher

    private lateinit var workLogService: WorkLogService
    private lateinit var testUser: User
    private val userId = UUID.randomUUID()

    @BeforeEach
    fun setUp() {
        workLogService = WorkLogService(workLogRepository, userRepository, tagRepository, eventPublisher)
        testUser = User(id = userId, email = "test@grovarc.dev", password = "hashed", nickname = "tester")
        whenever(userRepository.findById(userId)).thenReturn(Optional.of(testUser))
    }

    @Test
    fun `로그 작성 시 저장 후 Kafka 이벤트를 발행한다`() {
        val request = WorkLogCreateRequest(
            title = "오늘의 작업",
            content = "Spring Boot 세팅 완료",
            logDate = LocalDate.now(),
            mood = Mood.GOOD,
        )
        val savedLog = WorkLog(
            id = UUID.randomUUID(),
            user = testUser,
            title = request.title,
            content = request.content,
            logDate = request.logDate,
            mood = request.mood,
        )
        whenever(workLogRepository.save(any())).thenReturn(savedLog)

        val response = workLogService.create(userId, request)

        assertThat(response.title).isEqualTo(request.title)
        assertThat(response.mood).isEqualTo(Mood.GOOD)
        verify(eventPublisher).publishWorkLogSaved(savedLog.id!!, userId, savedLog.logDate)
    }

    @Test
    fun `로그 목록 조회 시 페이지 응답을 반환한다`() {
        val logs = listOf(
            WorkLog(id = UUID.randomUUID(), user = testUser, title = "log1", content = "c1", logDate = LocalDate.now()),
            WorkLog(id = UUID.randomUUID(), user = testUser, title = "log2", content = "c2", logDate = LocalDate.now().minusDays(1)),
        )
        val pageable = PageRequest.of(0, 20)
        whenever(workLogRepository.findAllByUserOrderByLogDateDesc(testUser, pageable))
            .thenReturn(PageImpl(logs, pageable, 2))

        val result = workLogService.getList(userId, pageable)

        assertThat(result.content).hasSize(2)
        assertThat(result.totalElements).isEqualTo(2)
    }

    @Test
    fun `존재하지 않는 로그 조회 시 예외가 발생한다`() {
        val logId = UUID.randomUUID()
        whenever(workLogRepository.findByIdAndUser(logId, testUser)).thenReturn(null)

        assertThatThrownBy { workLogService.getOne(userId, logId) }
            .isInstanceOf(NoSuchElementException::class.java)
            .hasMessage("작업 로그를 찾을 수 없습니다")
    }

    @Test
    fun `로그 수정 시 내용이 변경된다`() {
        val logId = UUID.randomUUID()
        val existing = WorkLog(
            id = logId, user = testUser,
            title = "old", content = "old content", logDate = LocalDate.now(),
        )
        val request = WorkLogUpdateRequest(
            title = "new title", content = "new content",
            logDate = LocalDate.now(), mood = Mood.GREAT,
        )
        whenever(workLogRepository.findByIdAndUser(logId, testUser)).thenReturn(existing)

        val response = workLogService.update(userId, logId, request)

        assertThat(response.title).isEqualTo("new title")
        assertThat(response.mood).isEqualTo(Mood.GREAT)
    }

    @Test
    fun `다른 유저의 로그 삭제 시 예외가 발생한다`() {
        val logId = UUID.randomUUID()
        whenever(workLogRepository.findByIdAndUser(logId, testUser)).thenReturn(null)

        assertThatThrownBy { workLogService.delete(userId, logId) }
            .isInstanceOf(NoSuchElementException::class.java)

        verify(workLogRepository, never()).delete(any())
    }

    @Test
    fun `주간 통계 조회 시 해당 주의 데이터를 반환한다`() {
        val monday = LocalDate.of(2026, 3, 23)
        whenever(workLogRepository.findDailyStats(any(), any(), any())).thenReturn(emptyList())

        val result = workLogService.getWeeklyStats(userId, monday)

        assertThat(result.weekStart).isEqualTo(monday)
        assertThat(result.weekEnd).isEqualTo(monday.plusDays(6))
        assertThat(result.totalLogs).isEqualTo(0)
    }
}
