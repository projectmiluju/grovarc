# ---- builder ----
FROM gradle:8.7-jdk21 AS builder
WORKDIR /app
COPY build.gradle.kts settings.gradle.kts gradle.properties* ./
COPY gradle ./gradle

# 의존성 캐시 레이어
RUN gradle dependencies --no-daemon || true

COPY src ./src
RUN gradle bootJar --no-daemon -x test

# ---- runner ----
FROM eclipse-temurin:21-jre-alpine AS runner
WORKDIR /app

RUN addgroup --system --gid 1001 spring && \
    adduser --system --uid 1001 --ingroup spring spring

COPY --from=builder --chown=spring:spring /app/build/libs/*.jar app.jar

USER spring
EXPOSE 8080

ENTRYPOINT ["java", "-jar", "-Dspring.profiles.active=prod", "app.jar"]
