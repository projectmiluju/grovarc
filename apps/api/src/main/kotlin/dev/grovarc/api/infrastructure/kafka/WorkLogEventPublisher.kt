package dev.grovarc.api.infrastructure.kafka

import com.fasterxml.jackson.databind.ObjectMapper
import org.slf4j.LoggerFactory
import org.springframework.kafka.core.KafkaTemplate
import org.springframework.stereotype.Component
import java.time.LocalDate
import java.util.UUID

@Component
class WorkLogEventPublisher(
    private val kafkaTemplate: KafkaTemplate<String, String>,
    private val objectMapper: ObjectMapper,
) {
    private val log = LoggerFactory.getLogger(javaClass)

    companion object {
        const val TOPIC_WORK_LOG_SAVED = "work-log.saved"
    }

    fun publishWorkLogSaved(workLogId: UUID, userId: UUID, logDate: LocalDate) {
        val payload = objectMapper.writeValueAsString(
            WorkLogSavedEvent(
                workLogId = workLogId.toString(),
                userId = userId.toString(),
                logDate = logDate.toString(),
            )
        )
        kafkaTemplate.send(TOPIC_WORK_LOG_SAVED, userId.toString(), payload)
            .whenComplete { _, ex ->
                if (ex != null) {
                    log.error("Kafka 이벤트 발행 실패 workLogId={}: {}", workLogId, ex.message)
                } else {
                    log.debug("Kafka 이벤트 발행 완료 workLogId={}", workLogId)
                }
            }
    }
}

data class WorkLogSavedEvent(
    val workLogId: String,
    val userId: String,
    val logDate: String,
)
