package dev.grovarc.api.domain.retrospective

import dev.grovarc.api.domain.user.User
import jakarta.persistence.*
import java.time.LocalDate
import java.time.LocalDateTime
import java.util.UUID

@Entity
@Table(name = "retrospectives")
class Retrospective(
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    val id: UUID? = null,

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    val user: User,

    @Column(nullable = false)
    var title: String,

    @Column(nullable = false, columnDefinition = "TEXT")
    var content: String,

    @Column(nullable = false)
    val periodFrom: LocalDate,

    @Column(nullable = false)
    val periodTo: LocalDate,

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    var status: RetrospectiveStatus = RetrospectiveStatus.DRAFT,

    @Column(nullable = false, updatable = false)
    val createdAt: LocalDateTime = LocalDateTime.now(),

    @Column(nullable = false)
    var updatedAt: LocalDateTime = LocalDateTime.now(),
) {
    fun update(title: String, content: String) {
        this.title = title
        this.content = content
        this.updatedAt = LocalDateTime.now()
    }

    fun publish() {
        this.status = RetrospectiveStatus.PUBLISHED
        this.updatedAt = LocalDateTime.now()
    }
}

enum class RetrospectiveStatus {
    DRAFT, PUBLISHED
}
