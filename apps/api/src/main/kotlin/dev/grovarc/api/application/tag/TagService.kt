package dev.grovarc.api.application.tag

import dev.grovarc.api.domain.tag.Tag
import dev.grovarc.api.domain.tag.TagRepository
import dev.grovarc.api.domain.user.User
import dev.grovarc.api.domain.user.UserRepository
import dev.grovarc.api.interfaces.dto.TagCreateRequest
import dev.grovarc.api.interfaces.dto.TagDetailResponse
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.util.UUID

@Service
@Transactional
class TagService(
    private val tagRepository: TagRepository,
    private val userRepository: UserRepository,
) {

    @Transactional(readOnly = true)
    fun getAll(userId: UUID): List<TagDetailResponse> {
        val user = findUser(userId)
        return tagRepository.findAllByUser(user).map { TagDetailResponse.from(it) }
    }

    fun create(userId: UUID, request: TagCreateRequest): TagDetailResponse {
        val user = findUser(userId)

        if (tagRepository.existsByUserAndName(user, request.name)) {
            throw IllegalArgumentException("이미 존재하는 태그 이름입니다: ${request.name}")
        }

        val tag = tagRepository.save(
            Tag(user = user, name = request.name, color = request.color)
        )
        return TagDetailResponse.from(tag)
    }

    fun delete(userId: UUID, tagId: UUID) {
        val user = findUser(userId)
        val tag = tagRepository.findByIdAndUser(tagId, user)
            ?: throw NoSuchElementException("태그를 찾을 수 없습니다")
        tagRepository.delete(tag)
    }

    private fun findUser(userId: UUID): User =
        userRepository.findById(userId).orElseThrow { NoSuchElementException("유저를 찾을 수 없습니다") }
}
