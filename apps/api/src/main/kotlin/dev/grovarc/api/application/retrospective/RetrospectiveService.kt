package dev.grovarc.api.application.retrospective

import dev.grovarc.api.domain.retrospective.RetrospectiveRepository
import dev.grovarc.api.domain.user.User
import dev.grovarc.api.domain.user.UserRepository
import dev.grovarc.api.interfaces.dto.PageResponse
import dev.grovarc.api.interfaces.dto.RetrospectiveResponse
import dev.grovarc.api.interfaces.dto.RetrospectiveUpdateRequest
import org.springframework.data.domain.Pageable
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.util.UUID

@Service
@Transactional
class RetrospectiveService(
    private val retrospectiveRepository: RetrospectiveRepository,
    private val userRepository: UserRepository,
) {

    @Transactional(readOnly = true)
    fun getList(userId: UUID, pageable: Pageable): PageResponse<RetrospectiveResponse> {
        val user = findUser(userId)
        val page = retrospectiveRepository.findAllByUserOrderByCreatedAtDesc(user, pageable)
        return PageResponse(
            content = page.content.map { RetrospectiveResponse.from(it) },
            page = page.number,
            size = page.size,
            totalElements = page.totalElements,
            totalPages = page.totalPages,
        )
    }

    @Transactional(readOnly = true)
    fun getOne(userId: UUID, retroId: UUID): RetrospectiveResponse {
        val user = findUser(userId)
        val retro = findRetro(retroId, user)
        return RetrospectiveResponse.from(retro)
    }

    fun update(userId: UUID, retroId: UUID, request: RetrospectiveUpdateRequest): RetrospectiveResponse {
        val user = findUser(userId)
        val retro = findRetro(retroId, user)
        retro.update(request.title, request.content)
        return RetrospectiveResponse.from(retro)
    }

    fun publish(userId: UUID, retroId: UUID): RetrospectiveResponse {
        val user = findUser(userId)
        val retro = findRetro(retroId, user)
        retro.publish()
        return RetrospectiveResponse.from(retro)
    }

    private fun findUser(userId: UUID): User =
        userRepository.findById(userId).orElseThrow { NoSuchElementException("유저를 찾을 수 없습니다") }

    private fun findRetro(retroId: UUID, user: User) =
        retrospectiveRepository.findByIdAndUser(retroId, user)
            ?: throw NoSuchElementException("회고를 찾을 수 없습니다")
}
