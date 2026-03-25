package dev.grovarc.api.domain.retrospective

import dev.grovarc.api.domain.user.User
import org.springframework.data.domain.Page
import org.springframework.data.domain.Pageable
import org.springframework.data.jpa.repository.JpaRepository
import java.util.UUID

interface RetrospectiveRepository : JpaRepository<Retrospective, UUID> {
    fun findByIdAndUser(id: UUID, user: User): Retrospective?
    fun findAllByUserOrderByCreatedAtDesc(user: User, pageable: Pageable): Page<Retrospective>
}
