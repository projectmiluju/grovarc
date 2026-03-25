package dev.grovarc.api.application.tag

import dev.grovarc.api.domain.tag.Tag
import dev.grovarc.api.domain.tag.TagRepository
import dev.grovarc.api.domain.user.User
import dev.grovarc.api.domain.user.UserRepository
import dev.grovarc.api.interfaces.dto.TagCreateRequest
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
import java.util.Optional
import java.util.UUID

@ExtendWith(MockitoExtension::class)
class TagServiceTest {

    @Mock lateinit var tagRepository: TagRepository
    @Mock lateinit var userRepository: UserRepository

    private lateinit var tagService: TagService
    private lateinit var testUser: User
    private val userId = UUID.randomUUID()

    @BeforeEach
    fun setUp() {
        tagService = TagService(tagRepository, userRepository)
        testUser = User(id = userId, email = "test@grovarc.dev", password = "hashed", nickname = "tester")
        whenever(userRepository.findById(userId)).thenReturn(Optional.of(testUser))
    }

    @Test
    fun `태그 목록 조회 시 유저의 태그를 반환한다`() {
        val tags = listOf(
            Tag(id = UUID.randomUUID(), user = testUser, name = "Kotlin", color = "#7F52FF"),
            Tag(id = UUID.randomUUID(), user = testUser, name = "Spring", color = "#6DB33F"),
        )
        whenever(tagRepository.findAllByUser(testUser)).thenReturn(tags)

        val result = tagService.getAll(userId)

        assertThat(result).hasSize(2)
        assertThat(result.map { it.name }).containsExactly("Kotlin", "Spring")
    }

    @Test
    fun `태그 생성 성공 시 생성된 태그를 반환한다`() {
        val request = TagCreateRequest(name = "Kotlin", color = "#7F52FF")
        val saved = Tag(id = UUID.randomUUID(), user = testUser, name = request.name, color = request.color)

        whenever(tagRepository.existsByUserAndName(testUser, request.name)).thenReturn(false)
        whenever(tagRepository.save(any())).thenReturn(saved)

        val result = tagService.create(userId, request)

        assertThat(result.name).isEqualTo("Kotlin")
        assertThat(result.color).isEqualTo("#7F52FF")
    }

    @Test
    fun `중복된 태그 이름으로 생성 시 예외가 발생한다`() {
        val request = TagCreateRequest(name = "Kotlin")
        whenever(tagRepository.existsByUserAndName(testUser, request.name)).thenReturn(true)

        assertThatThrownBy { tagService.create(userId, request) }
            .isInstanceOf(IllegalArgumentException::class.java)
            .hasMessageContaining("이미 존재하는 태그 이름입니다")

        verify(tagRepository, never()).save(any())
    }

    @Test
    fun `태그 삭제 성공 시 삭제가 호출된다`() {
        val tagId = UUID.randomUUID()
        val tag = Tag(id = tagId, user = testUser, name = "Kotlin")
        whenever(tagRepository.findByIdAndUser(tagId, testUser)).thenReturn(tag)

        tagService.delete(userId, tagId)

        verify(tagRepository).delete(tag)
    }

    @Test
    fun `존재하지 않는 태그 삭제 시 예외가 발생한다`() {
        val tagId = UUID.randomUUID()
        whenever(tagRepository.findByIdAndUser(tagId, testUser)).thenReturn(null)

        assertThatThrownBy { tagService.delete(userId, tagId) }
            .isInstanceOf(NoSuchElementException::class.java)
            .hasMessage("태그를 찾을 수 없습니다")

        verify(tagRepository, never()).delete(any())
    }
}
