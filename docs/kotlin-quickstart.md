# Kotlin 문법 퀵스타트

> Phase 0 산출물 — Java 경험자 기준으로 Spring Boot 개발에 필요한 Kotlin 핵심 문법만 정리.
> "Java 이렇게 쓰던 것 → Kotlin에선 이렇게"

---

## 1. 변수 선언

```kotlin
// Java: final String name = "원용";
val name: String = "원용"   // 불변 (val = value)

// Java: String nickname = "dev";
var nickname = "dev"         // 가변 (var), 타입 추론

// Nullable
var email: String? = null    // ?를 붙여야 null 허용
```

---

## 2. 함수

```kotlin
// 기본
fun greet(name: String): String {
    return "Hello, $name"
}

// 단일 표현식 (한 줄)
fun greet(name: String) = "Hello, $name"

// 기본값
fun createUser(name: String, role: String = "developer") { ... }

// 확장 함수 (Java에 없음)
fun String.isValidEmail(): Boolean = this.contains("@")
"dev@example.com".isValidEmail()  // true
```

---

## 3. 클래스

```kotlin
// Data class — equals, hashCode, toString, copy 자동 생성
data class User(
    val id: String,
    val email: String,
    val nickname: String
)

// 복사 (불변 객체 수정)
val updated = user.copy(nickname = "새이름")

// 생성자 기본값
data class CreateUserRequest(
    val email: String,
    val password: String,
    val nickname: String = ""
)
```

---

## 4. Null 안전

```kotlin
val user: User? = findUser(id)

// 안전 호출 (?.)
val email = user?.email          // user가 null이면 null 반환

// Elvis 연산자 (?:)
val email = user?.email ?: "unknown"  // null이면 기본값

// Non-null 단언 (!!) — 확실할 때만
val email = user!!.email         // null이면 NPE 발생

// let (null이 아닐 때만 실행)
user?.let {
    println(it.email)
}
```

---

## 5. 컬렉션 & 람다

```kotlin
val logs = listOf("log1", "log2", "log3")  // 불변
val tags = mutableListOf("Kotlin", "Spring") // 가변

// map, filter, find
val titles = logs.map { it.uppercase() }
val kotlinLogs = logs.filter { it.contains("kotlin") }
val first = logs.find { it.startsWith("log") }

// forEach
logs.forEach { println(it) }

// groupBy
val grouped = logs.groupBy { it.length }
```

---

## 6. when (Java switch 대체)

```kotlin
val message = when (status) {
    "draft" -> "작성 중"
    "reviewed" -> "검토 완료"
    "published" -> "게시됨"
    else -> "알 수 없음"
}

// 범위
val grade = when (score) {
    in 90..100 -> "A"
    in 80..89 -> "B"
    else -> "F"
}
```

---

## 7. 코루틴 (Spring에서 비동기)

```kotlin
// build.gradle.kts
implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core")

// suspend 함수
suspend fun fetchUser(id: String): User {
    delay(100)  // 논블로킹 대기
    return userRepository.findById(id)
}

// Spring Controller에서
@GetMapping("/users/{id}")
suspend fun getUser(@PathVariable id: String): User {
    return userService.fetchUser(id)
}
```

---

## 8. Spring Boot에서 자주 쓰는 패턴

```kotlin
// Entity
@Entity
@Table(name = "work_logs")
class WorkLog(
    @Id
    val id: UUID = UUID.randomUUID(),

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id")
    val user: User,

    @Column(columnDefinition = "TEXT")
    val content: String,

    val loggedAt: LocalDate = LocalDate.now()
)

// Repository
interface WorkLogRepository : JpaRepository<WorkLog, UUID> {
    fun findByUserIdOrderByLoggedAtDesc(userId: UUID): List<WorkLog>
}

// Service
@Service
@Transactional
class WorkLogService(
    private val workLogRepository: WorkLogRepository
) {
    fun createLog(userId: UUID, request: CreateLogRequest): WorkLog {
        val log = WorkLog(
            user = userRepository.getReferenceById(userId),
            content = request.content,
            loggedAt = request.loggedAt
        )
        return workLogRepository.save(log)
    }
}

// Controller
@RestController
@RequestMapping("/api/v1/logs")
class WorkLogController(
    private val workLogService: WorkLogService
) {
    @PostMapping
    fun createLog(
        @AuthenticationPrincipal userId: UUID,
        @RequestBody @Valid request: CreateLogRequest
    ): ResponseEntity<WorkLogResponse> {
        val log = workLogService.createLog(userId, request)
        return ResponseEntity.status(201).body(log.toResponse())
    }
}
```

---

## 9. Java vs Kotlin 비교 요약

| Java | Kotlin |
|------|--------|
| `public class Foo {}` | `class Foo` (기본 public) |
| `private final String x;` | `val x: String` |
| Getter/Setter | 프로퍼티 직접 접근 |
| `null` 체크 매번 | `?`, `?.`, `?:` |
| `instanceof` | `is` |
| `for (String s : list)` | `for (s in list)` |
| Stream API | 컬렉션 확장 함수 |
| `Optional<T>` | `T?` |
| `void` | `Unit` (생략 가능) |

---

## 10. 학습 리소스

- [Kotlin 공식 문서](https://kotlinlang.org/docs/home.html)
- [Kotlin Koans (인터랙티브 연습)](https://play.kotlinlang.org/koans)
- [Spring Boot + Kotlin 가이드](https://spring.io/guides/tutorials/spring-boot-kotlin)
- [Kotlin Coroutines 공식 가이드](https://kotlinlang.org/docs/coroutines-overview.html)

> 추천 순서: Koans → Spring Boot Kotlin 가이드 → Coroutines
