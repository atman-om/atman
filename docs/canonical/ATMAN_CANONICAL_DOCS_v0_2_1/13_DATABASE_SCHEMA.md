---
project: Atman
pack: ATMAN_CANONICAL_DOCS_v0_2
version: 0.2
status: execution-grade canonical baseline
created_at: 2026-05-28T13:00:36+05:30
timezone: Asia/Kolkata
canonical_rule: Any implementation, repo, model, dataset, or release gate must conform to this document pack or record an ADR.
---

# 13 — Database Schema

## 1. Objective

This document defines the canonical persistence layer. Engineers may not create divergent schemas without an ADR.

## 2. Required stores

| Store | Purpose |
|---|---|
| PostgreSQL | transactional metadata, source/review state, release gates |
| Qdrant | vector embeddings |
| Neo4j or Postgres graph tables | TattvaNet ontology graph |
| Redis | queue/cache/rate limits |
| S3/MinIO | raw files, exports, checkpoints, evidence artifacts |

## 3. PostgreSQL conventions

- Primary keys: UUID.
- Timestamps: `TIMESTAMPTZ`.
- Soft-deletion: `deleted_at` when audit retention is needed.
- JSONB allowed for flexible metadata but not for core state fields.
- Every state transition must be auditable.

## 4. Enumerations

```sql
CREATE TYPE zone_enum AS ENUM ('Z0_DISCOVERY', 'Z1_SANDBOX', 'Z2_PRODUCTION');
CREATE TYPE rights_status_enum AS ENUM (
  'UNKNOWN', 'PUBLIC_DOMAIN_VERIFIED', 'LICENSED_VERIFIED',
  'OPEN_LICENSE_VERIFIED', 'USER_OWNED', 'REFERENCE_ONLY',
  'NO_TRAINING_ALLOWED', 'NO_STORAGE_ALLOWED', 'REJECTED'
);
CREATE TYPE review_status_enum AS ENUM (
  'pending', 'needs_cleanup', 'approved', 'rejected', 'deprecated'
);
```

## 5. Core tables

### users

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  display_name TEXT,
  status TEXT NOT NULL DEFAULT 'active',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### roles

```sql
CREATE TABLE roles (
  id UUID PRIMARY KEY,
  name TEXT UNIQUE NOT NULL,
  description TEXT
);
```

### user_roles

```sql
CREATE TABLE user_roles (
  user_id UUID REFERENCES users(id),
  role_id UUID REFERENCES roles(id),
  PRIMARY KEY (user_id, role_id)
);
```

### sources

```sql
CREATE TABLE sources (
  id UUID PRIMARY KEY,
  source_type TEXT NOT NULL,
  title TEXT NOT NULL,
  language TEXT,
  script TEXT,
  tradition_scope TEXT[] NOT NULL DEFAULT '{}',
  zone zone_enum NOT NULL DEFAULT 'Z0_DISCOVERY',
  rights_status rights_status_enum NOT NULL DEFAULT 'UNKNOWN',
  ingestion_status TEXT NOT NULL DEFAULT 'INGESTED',
  review_status review_status_enum NOT NULL DEFAULT 'pending',
  checksum_sha256 TEXT UNIQUE,
  uploaded_by UUID REFERENCES users(id),
  metadata JSONB NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### source_files

```sql
CREATE TABLE source_files (
  id UUID PRIMARY KEY,
  source_id UUID NOT NULL REFERENCES sources(id),
  object_uri TEXT NOT NULL,
  mime_type TEXT,
  size_bytes BIGINT,
  checksum_sha256 TEXT NOT NULL,
  scan_status TEXT NOT NULL DEFAULT 'pending',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### source_rights_reviews

```sql
CREATE TABLE source_rights_reviews (
  id UUID PRIMARY KEY,
  source_id UUID NOT NULL REFERENCES sources(id),
  reviewer_id UUID REFERENCES users(id),
  previous_status rights_status_enum,
  new_status rights_status_enum NOT NULL,
  evidence_uri TEXT,
  allowed_usage JSONB NOT NULL DEFAULT '{}',
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### chunks

```sql
CREATE TABLE chunks (
  id UUID PRIMARY KEY,
  source_id UUID NOT NULL REFERENCES sources(id),
  chunk_text TEXT NOT NULL,
  normalized_text TEXT,
  language TEXT,
  script TEXT,
  token_count INT,
  chunk_order INT NOT NULL,
  citation_locator JSONB NOT NULL DEFAULT '{}',
  quality_score DOUBLE PRECISION,
  zone zone_enum NOT NULL DEFAULT 'Z0_DISCOVERY',
  rights_status rights_status_enum NOT NULL DEFAULT 'UNKNOWN',
  review_status review_status_enum NOT NULL DEFAULT 'pending',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### embeddings

```sql
CREATE TABLE embeddings (
  id UUID PRIMARY KEY,
  chunk_id UUID NOT NULL REFERENCES chunks(id),
  embedding_model TEXT NOT NULL,
  vector_db TEXT NOT NULL DEFAULT 'qdrant',
  collection_name TEXT NOT NULL,
  vector_id TEXT NOT NULL,
  dimensions INT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (embedding_model, collection_name, vector_id)
);
```

### ontology_entities

```sql
CREATE TABLE ontology_entities (
  id UUID PRIMARY KEY,
  entity_type TEXT NOT NULL,
  canonical_label TEXT NOT NULL,
  display_label_hi TEXT,
  display_label_sa TEXT,
  display_label_en TEXT,
  aliases JSONB NOT NULL DEFAULT '[]',
  transliteration TEXT,
  description TEXT,
  confidence DOUBLE PRECISION NOT NULL DEFAULT 0,
  review_status review_status_enum NOT NULL DEFAULT 'pending',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### ontology_edges

```sql
CREATE TABLE ontology_edges (
  id UUID PRIMARY KEY,
  source_entity_id UUID NOT NULL REFERENCES ontology_entities(id),
  target_entity_id UUID NOT NULL REFERENCES ontology_entities(id),
  relation_type TEXT NOT NULL,
  evidence_chunk_ids UUID[] NOT NULL DEFAULT '{}',
  tradition_scope TEXT[] NOT NULL DEFAULT '{}',
  confidence DOUBLE PRECISION NOT NULL DEFAULT 0,
  review_status review_status_enum NOT NULL DEFAULT 'pending',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### rag_queries

```sql
CREATE TABLE rag_queries (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  query_text TEXT NOT NULL,
  language TEXT,
  mode TEXT,
  retrieved_chunk_ids UUID[] NOT NULL DEFAULT '{}',
  selected_chunk_ids UUID[] NOT NULL DEFAULT '{}',
  coverage TEXT NOT NULL,
  latency_ms INT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### ask_sessions

```sql
CREATE TABLE ask_sessions (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  question TEXT NOT NULL,
  answer TEXT,
  confidence TEXT,
  contract JSONB NOT NULL DEFAULT '{}',
  risk_flags JSONB NOT NULL DEFAULT '[]',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### answer_citations

```sql
CREATE TABLE answer_citations (
  id UUID PRIMARY KEY,
  ask_session_id UUID NOT NULL REFERENCES ask_sessions(id),
  source_id UUID NOT NULL REFERENCES sources(id),
  chunk_id UUID NOT NULL REFERENCES chunks(id),
  citation_text TEXT NOT NULL,
  score DOUBLE PRECISION,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### training_datasets

```sql
CREATE TABLE training_datasets (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  version TEXT NOT NULL,
  intended_use TEXT NOT NULL,
  source_snapshot JSONB NOT NULL DEFAULT '{}',
  dataset_hash TEXT UNIQUE NOT NULL,
  storage_uri TEXT NOT NULL,
  approved BOOLEAN NOT NULL DEFAULT false,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (name, version)
);
```

### model_checkpoints

```sql
CREATE TABLE model_checkpoints (
  id UUID PRIMARY KEY,
  model_name TEXT NOT NULL,
  version TEXT NOT NULL,
  base_model TEXT NOT NULL,
  dataset_id UUID REFERENCES training_datasets(id),
  training_config JSONB NOT NULL DEFAULT '{}',
  checkpoint_uri TEXT NOT NULL,
  checkpoint_hash TEXT UNIQUE NOT NULL,
  status TEXT NOT NULL DEFAULT 'registered',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (model_name, version)
);
```

### eval_runs

```sql
CREATE TABLE eval_runs (
  id UUID PRIMARY KEY,
  target_type TEXT NOT NULL,
  target_id UUID,
  benchmark_name TEXT NOT NULL,
  benchmark_version TEXT NOT NULL,
  score JSONB NOT NULL DEFAULT '{}',
  hard_failures JSONB NOT NULL DEFAULT '[]',
  approved BOOLEAN NOT NULL DEFAULT false,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### release_gates

```sql
CREATE TABLE release_gates (
  id UUID PRIMARY KEY,
  artifact_type TEXT NOT NULL,
  artifact_id UUID,
  artifact_version TEXT NOT NULL,
  allowed BOOLEAN NOT NULL DEFAULT false,
  hard_failures JSONB NOT NULL DEFAULT '[]',
  soft_warnings JSONB NOT NULL DEFAULT '[]',
  required_approvals JSONB NOT NULL DEFAULT '[]',
  metrics JSONB NOT NULL DEFAULT '{}',
  decided_by UUID REFERENCES users(id),
  decided_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### feedback_reports

```sql
CREATE TABLE feedback_reports (
  id UUID PRIMARY KEY,
  ask_session_id UUID REFERENCES ask_sessions(id),
  user_id UUID REFERENCES users(id),
  rating INT,
  category TEXT,
  comment TEXT,
  status TEXT NOT NULL DEFAULT 'open',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### audit_logs

```sql
CREATE TABLE audit_logs (
  id UUID PRIMARY KEY,
  actor_id UUID REFERENCES users(id),
  event_type TEXT NOT NULL,
  object_type TEXT NOT NULL,
  object_id UUID,
  before_state JSONB,
  after_state JSONB,
  request_id UUID,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

## 6. Required indexes

```sql
CREATE INDEX idx_sources_zone_status ON sources(zone, rights_status, review_status);
CREATE INDEX idx_chunks_source_order ON chunks(source_id, chunk_order);
CREATE INDEX idx_chunks_zone_quality ON chunks(zone, review_status, quality_score);
CREATE INDEX idx_eval_runs_target ON eval_runs(target_type, target_id);
CREATE INDEX idx_audit_logs_object ON audit_logs(object_type, object_id);
```

## 7. Migration rule

Every schema change must include:

```text
forward migration
rollback migration
data backfill plan when needed
integration test
ADR when semantic behavior changes
```
