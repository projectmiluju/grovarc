package dev.grovarc.api.domain.worklog

import dev.grovarc.api.domain.user.User
import org.springframework.data.domain.Page
import org.springframework.data.domain.Pageable
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Query
import org.springframework.data.repository.query.Param
import java.time.LocalDate
import java.util.UUID

interface WorkLogRepository : JpaRepository<WorkLog, UUID> {
    fun findByIdAndUser(id: UUID, user: User): WorkLog?
    fun findAllByUserOrderByLogDateDesc(user: User, pageable: Pageable): Page<WorkLog>

    @Query("""
        SELECT w FROM WorkLog w
        WHERE w.user = :user
          AND w.logDate BETWEEN :from AND :to
        ORDER BY w.logDate DESC
    """)
    fun findByUserAndDateRange(
        @Param("user") user: User,
        @Param("from") from: LocalDate,
        @Param("to") to: LocalDate,
    ): List<WorkLog>

    @Query("""
        SELECT w.logDate, COUNT(w), AVG(CASE w.mood
            WHEN 'GREAT' THEN 5 WHEN 'GOOD' THEN 4 WHEN 'NEUTRAL' THEN 3
            WHEN 'BAD' THEN 2 WHEN 'TERRIBLE' THEN 1 ELSE NULL END)
        FROM WorkLog w
        WHERE w.user = :user AND w.logDate BETWEEN :from AND :to
        GROUP BY w.logDate
        ORDER BY w.logDate
    """)
    fun findDailyStats(
        @Param("user") user: User,
        @Param("from") from: LocalDate,
        @Param("to") to: LocalDate,
    ): List<Array<Any>>
}
