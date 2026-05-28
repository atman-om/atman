-- ATMAN v0.2.1 seed migration for ATMAN_REPO_v0_3
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_type TEXT NOT NULL,
    title TEXT NOT NULL,
    language TEXT NOT NULL,
    rights_status TEXT NOT NULL DEFAULT 'UNKNOWN',
    ingestion_status TEXT NOT NULL DEFAULT 'REGISTERED',
    checksum_sha256 TEXT UNIQUE,
    allowed_usage JSONB NOT NULL DEFAULT '{}'::jsonb,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    token_count INT,
    chunk_order INT NOT NULL,
    citation_locator JSONB NOT NULL,
    quality_score DOUBLE PRECISION,
    review_status TEXT NOT NULL DEFAULT 'DRAFT',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chunk_id UUID NOT NULL REFERENCES chunks(id) ON DELETE CASCADE,
    embedding_model TEXT NOT NULL,
    vector_id TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS provenance_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    artifact_type TEXT NOT NULL,
    artifact_id UUID,
    event_type TEXT NOT NULL,
    actor_type TEXT NOT NULL,
    actor_id TEXT NOT NULL,
    previous_state TEXT,
    next_state TEXT,
    reason TEXT,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_sources_status ON sources(ingestion_status, rights_status);
CREATE INDEX IF NOT EXISTS idx_chunks_source ON chunks(source_id, chunk_order);
CREATE INDEX IF NOT EXISTS idx_provenance_artifact ON provenance_events(artifact_type, artifact_id);
