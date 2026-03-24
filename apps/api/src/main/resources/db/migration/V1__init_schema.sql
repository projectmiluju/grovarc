-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;

-- Users
CREATE TABLE users (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email       VARCHAR(255) NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL,
    nickname    VARCHAR(100) NOT NULL,
    role        VARCHAR(20)  NOT NULL DEFAULT 'USER',
    created_at  TIMESTAMP    NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- Tags
CREATE TABLE tags (
    id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id    UUID         NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name       VARCHAR(100) NOT NULL,
    color      VARCHAR(7),
    created_at TIMESTAMP    NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, name)
);

-- Work Logs
CREATE TABLE work_logs (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id     UUID         NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title       VARCHAR(255) NOT NULL,
    content     TEXT         NOT NULL,
    log_date    DATE         NOT NULL,
    mood        VARCHAR(20),
    created_at  TIMESTAMP    NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- Work Log ↔ Tag (N:M)
CREATE TABLE work_log_tags (
    work_log_id UUID NOT NULL REFERENCES work_logs(id) ON DELETE CASCADE,
    tag_id      UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (work_log_id, tag_id)
);

-- Retrospectives
CREATE TABLE retrospectives (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id     UUID         NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title       VARCHAR(255) NOT NULL,
    content     TEXT         NOT NULL,
    period_from DATE         NOT NULL,
    period_to   DATE         NOT NULL,
    status      VARCHAR(20)  NOT NULL DEFAULT 'DRAFT',
    created_at  TIMESTAMP    NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- Work log embedding (pgvector)
CREATE TABLE work_log_embeddings (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    work_log_id UUID NOT NULL REFERENCES work_logs(id) ON DELETE CASCADE UNIQUE,
    embedding   vector(1536),
    created_at  TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_work_logs_user_id    ON work_logs(user_id);
CREATE INDEX idx_work_logs_log_date   ON work_logs(log_date);
CREATE INDEX idx_tags_user_id         ON tags(user_id);
CREATE INDEX idx_retrospectives_user  ON retrospectives(user_id);
