package dev.grovarc.api.domain.tag

import dev.grovarc.api.domain.user.User
import org.springframework.data.jpa.repository.JpaRepository
import java.util.UUID

interface TagRepository : JpaRepository<Tag, UUID> {
    fun findAllByUser(user: User): List<Tag>
    fun findByIdAndUser(id: UUID, user: User): Tag?
    fun existsByUserAndName(user: User, name: String): Boolean
}
