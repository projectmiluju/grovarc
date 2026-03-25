package dev.grovarc.api.interfaces.rest

import dev.grovarc.api.application.worklog.WorkLogService
import dev.grovarc.api.interfaces.dto.*
import jakarta.validation.Valid
import org.springframework.data.domain.PageRequest
import org.springframework.data.domain.Sort
import org.springframework.format.annotation.DateTimeFormat
import org.springframework.http.HttpStatus
import org.springframework.http.ResponseEntity
import org.springframework.security.core.annotation.AuthenticationPrincipal
import org.springframework.web.bind.annotation.*
import java.time.LocalDate
import java.util.UUID

@RestController
@RequestMapping("/api/v1/logs")
class WorkLogController(private val workLogService: WorkLogService) {

    @PostMapping
    fun create(
        @AuthenticationPrincipal userId: UUID,
        @Valid @RequestBody request: WorkLogCreateRequest,
    ): ResponseEntity<WorkLogResponse> =
        ResponseEntity.status(HttpStatus.CREATED).body(workLogService.create(userId, request))

    @GetMapping
    fun getList(
        @AuthenticationPrincipal userId: UUID,
        @RequestParam(defaultValue = "0") page: Int,
        @RequestParam(defaultValue = "20") size: Int,
    ): ResponseEntity<PageResponse<WorkLogResponse>> {
        val pageable = PageRequest.of(page, size, Sort.by("logDate").descending())
        return ResponseEntity.ok(workLogService.getList(userId, pageable))
    }

    @GetMapping("/{logId}")
    fun getOne(
        @AuthenticationPrincipal userId: UUID,
        @PathVariable logId: UUID,
    ): ResponseEntity<WorkLogResponse> =
        ResponseEntity.ok(workLogService.getOne(userId, logId))

    @PutMapping("/{logId}")
    fun update(
        @AuthenticationPrincipal userId: UUID,
        @PathVariable logId: UUID,
        @Valid @RequestBody request: WorkLogUpdateRequest,
    ): ResponseEntity<WorkLogResponse> =
        ResponseEntity.ok(workLogService.update(userId, logId, request))

    @DeleteMapping("/{logId}")
    fun delete(
        @AuthenticationPrincipal userId: UUID,
        @PathVariable logId: UUID,
    ): ResponseEntity<Unit> {
        workLogService.delete(userId, logId)
        return ResponseEntity.noContent().build()
    }

    @GetMapping("/stats/weekly")
    fun weeklyStats(
        @AuthenticationPrincipal userId: UUID,
        @RequestParam(required = false)
        @DateTimeFormat(iso = DateTimeFormat.ISO.DATE)
        date: LocalDate?,
    ): ResponseEntity<WeeklyStatsResponse> =
        ResponseEntity.ok(workLogService.getWeeklyStats(userId, date ?: LocalDate.now()))
}
