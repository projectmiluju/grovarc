package dev.grovarc.api.application.retrospective

import dev.grovarc.api.domain.retrospective.Retrospective
import dev.grovarc.api.domain.retrospective.RetrospectiveRepository
import dev.grovarc.api.domain.retrospective.RetrospectiveStatus
import dev.grovarc.api.domain.user.User
import dev.grovarc.api.domain.user.UserRepository
import dev.grovarc.api.interfaces.dto.RetrospectiveUpdateRequest
import org.assertj.core.api.Assertions.assertThat
import org.assertj.core.api.Assertions.assertThatThrownBy
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.extension.ExtendWith
import org.mockito.Mock
import org.mockito.junit.jupiter.MockitoExtension
import org.mockito.kotlin.whenever
import org.springframework.data.domain.PageImpl
import org.springframework.data.domain.PageRequest
import java.time.LocalDate
import java.util.Optional
import java.util.UUID

@ExtendWith(MockitoExtension::class)
class RetrospectiveServiceTest {

    @Mock lateinit var retrospectiveRepository: RetrospectiveRepository
    @Mock lateinit var userRepository: UserRepository

    private lateinit var retrospectiveService: RetrospectiveService
    private lateinit var testUser: User
    private val userId = UUID.randomUUID()

    @BeforeEach
    fun setUp() {
        retrospectiveService = RetrospectiveService(retrospectiveRepository, userRepository)
        testUser = User(id = userId, email = "test@grovarc.dev", password = "hashed", nickname = "tester")
        whenever(userRepository.findById(userId)).thenReturn(Optional.of(testUser))
    }

    private fun makeRetro(id: UUID = UUID.randomUUID()) = Retrospective(
        id = id,
        user = testUser,
        title = "3월 4주차 회고",
        content = "이번 주는 Spring Boot 세팅을 완료했다.",
        periodFrom = LocalDate.of(2026, 3, 23),
        periodTo = LocalDate.of(2026, 3, 29),
    )

    @Test
    fun `회고 목록 조회 시 페이지 응답을 반환한다`() {
        val retros = listOf(makeRetro(), makeRetro())
        val pageable = PageRequest.of(0, 10)
        whenever(retrospectiveRepository.findAllByUserOrderByCreatedAtDesc(testUser, pageable))
            .thenReturn(PageImpl(retros, pageable, 2))

        val result = retrospectiveService.getList(userId, pageable)

        assertThat(result.content).hasSize(2)
        assertThat(result.totalElements).isEqualTo(2)
    }

    @Test
    fun `회고 단건 조회 성공 시 응답을 반환한다`() {
        val retro = makeRetro()
        whenever(retrospectiveRepository.findByIdAndUser(retro.id!!, testUser)).thenReturn(retro)

        val result = retrospectiveService.getOne(userId, retro.id!!)

        assertThat(result.title).isEqualTo(retro.title)
        assertThat(result.status).isEqualTo(RetrospectiveStatus.DRAFT)
    }

    @Test
    fun `존재하지 않는 회고 조회 시 예외가 발생한다`() {
        val retroId = UUID.randomUUID()
        whenever(retrospectiveRepository.findByIdAndUser(retroId, testUser)).thenReturn(null)

        assertThatThrownBy { retrospectiveService.getOne(userId, retroId) }
            .isInstanceOf(NoSuchElementException::class.java)
            .hasMessage("회고를 찾을 수 없습니다")
    }

    @Test
    fun `회고 수정 시 제목과 내용이 변경된다`() {
        val retro = makeRetro()
        whenever(retrospectiveRepository.findByIdAndUser(retro.id!!, testUser)).thenReturn(retro)
        val request = RetrospectiveUpdateRequest(title = "수정된 제목", content = "수정된 내용")

        val result = retrospectiveService.update(userId, retro.id!!, request)

        assertThat(result.title).isEqualTo("수정된 제목")
        assertThat(result.content).isEqualTo("수정된 내용")
    }

    @Test
    fun `회고 발행 시 상태가 PUBLISHED로 변경된다`() {
        val retro = makeRetro()
        whenever(retrospectiveRepository.findByIdAndUser(retro.id!!, testUser)).thenReturn(retro)

        val result = retrospectiveService.publish(userId, retro.id!!)

        assertThat(result.status).isEqualTo(RetrospectiveStatus.PUBLISHED)
    }
}
