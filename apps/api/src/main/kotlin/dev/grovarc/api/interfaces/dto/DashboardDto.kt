package dev.grovarc.api.interfaces.dto

import java.time.LocalDate

data class DashboardResponse(
    val totalLogs: Long,
    val currentStreak: Int,
    val longestStreak: Int,
    val thisWeekLogs: Int,
    val thisMonthLogs: Int,
    val recentLogs: List<WorkLogSummary>,
    val recentRetrospectives: List<RetrospectiveSummary>,
)

data class WorkLogSummary(
    val id: String,
    val title: String,
    val logDate: LocalDate,
    val mood: String?,
    val tagCount: Int,
)

data class RetrospectiveSummary(
    val id: String,
    val title: String,
    val periodFrom: LocalDate,
    val periodTo: LocalDate,
    val status: String,
)
