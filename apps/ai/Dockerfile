# ---- builder ----
FROM python:3.12-slim AS builder
WORKDIR /app

RUN pip install uv
COPY pyproject.toml ./
RUN uv pip install --system --no-cache .

# ---- runner ----
FROM python:3.12-slim AS runner
WORKDIR /app

RUN addgroup --system --gid 1001 fastapi && \
    adduser --system --uid 1001 --gid 1001 fastapi

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --chown=fastapi:fastapi . .

USER fastapi
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
