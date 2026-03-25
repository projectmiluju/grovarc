package dev.grovarc.api.domain.worklog

import dev.grovarc.api.domain.tag.Tag
import dev.grovarc.api.domain.user.User
import jakarta.persistence.*
import java.time.LocalDate
import java.time.LocalDateTime
import java.util.UUID

@Entity
@Table(name = "work_logs")
class WorkLog(
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
    var logDate: LocalDate,

    @Enumerated(EnumType.STRING)
    @Column
    var mood: Mood? = null,

    @ManyToMany(fetch = FetchType.LAZY)
    @JoinTable(
        name = "work_log_tags",
        joinColumns = [JoinColumn(name = "work_log_id")],
        inverseJoinColumns = [JoinColumn(name = "tag_id")],
    )
    val tags: MutableSet<Tag> = mutableSetOf(),

    @Column(nullable = false, updatable = false)
    val createdAt: LocalDateTime = LocalDateTime.now(),

    @Column(nullable = false)
    var updatedAt: LocalDateTime = LocalDateTime.now(),
) {
    fun update(title: String, content: String, logDate: LocalDate, mood: Mood?) {
        this.title = title
        this.content = content
        this.logDate = logDate
        this.mood = mood
        this.updatedAt = LocalDateTime.now()
    }

    fun replaceTags(newTags: Set<Tag>) {
        tags.clear()
        tags.addAll(newTags)
    }
}

enum class Mood {
    GREAT, GOOD, NEUTRAL, BAD, TERRIBLE
}
