from __future__ import annotations
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from services.api.app.core.db import Base


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    language: Mapped[str | None] = mapped_column(String(32))
    tradition_scope: Mapped[list[str]] = mapped_column(JSONB, default=list)
    rights_status: Mapped[str] = mapped_column(String(64), nullable=False, default="UNKNOWN")
    ingestion_status: Mapped[str] = mapped_column(String(64), nullable=False, default="INGESTED")
    checksum_sha256: Mapped[str | None] = mapped_column(String(64), unique=True)
    source_metadata: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    uploaded_by: Mapped[str | None] = mapped_column(UUID(as_uuid=False))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)

    chunks: Mapped[list["Chunk"]] = relationship(back_populates="source", cascade="all, delete-orphan")


class Chunk(Base):
    __tablename__ = "chunks"
    __table_args__ = (UniqueConstraint("source_id", "chunk_order", name="uq_chunks_source_order"),)

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    source_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("sources.id"), nullable=False, index=True)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_order: Mapped[int] = mapped_column(Integer, nullable=False)
    citation_locator: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    quality_score: Mapped[float] = mapped_column(Float, default=0.0)
    review_status: Mapped[str] = mapped_column(String(64), default="REVIEW_PENDING")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    source: Mapped[Source] = relationship(back_populates="chunks")
    embedding: Mapped["Embedding"] = relationship(back_populates="chunk", cascade="all, delete-orphan")


class Embedding(Base):
    __tablename__ = "embeddings"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    chunk_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("chunks.id"), nullable=False, unique=True)
    embedding_model: Mapped[str] = mapped_column(String(128), nullable=False)
    vector_id: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    chunk: Mapped[Chunk] = relationship(back_populates="embedding")


class RagQuery(Base):
    __tablename__ = "rag_queries"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    model_name: Mapped[str] = mapped_column(String(128), nullable=False)
    citations: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, default=list)
    safety_report: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class ContentTemplate(Base):
    __tablename__ = "content_templates"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    content_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    language: Mapped[str] = mapped_column(String(32), default="hi")
    prompt_template: Mapped[str] = mapped_column(Text, nullable=False)
    output_schema: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    version: Mapped[str] = mapped_column(String(32), default="0.4.0")
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)


class ContentBatch(Base):
    __tablename__ = "content_batches"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    content_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    topic: Mapped[str] = mapped_column(String(512), nullable=False)
    language: Mapped[str] = mapped_column(String(32), default="hi")
    difficulty: Mapped[str] = mapped_column(String(32), default="intermediate")
    quantity: Mapped[int] = mapped_column(Integer, default=5)
    template_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("content_templates.id"))
    status: Mapped[str] = mapped_column(String(64), default="DRAFT", index=True)
    generation_config: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    metrics: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    created_by: Mapped[str | None] = mapped_column(UUID(as_uuid=False))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)


class ContentItem(Base):
    __tablename__ = "content_items"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    batch_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("content_batches.id"), index=True)
    template_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("content_templates.id"))
    item_index: Mapped[int] = mapped_column(Integer, default=0)
    title: Mapped[str | None] = mapped_column(String(512))
    content_type: Mapped[str] = mapped_column(String(64), nullable=False)
    topic: Mapped[str] = mapped_column(String(512), nullable=False)
    language: Mapped[str] = mapped_column(String(32), default="hi")
    body: Mapped[str] = mapped_column(Text, nullable=False)
    source_chunk_ids: Mapped[list[str]] = mapped_column(JSONB, default=list)
    quality_report: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    review_status: Mapped[str] = mapped_column(String(64), default="REVIEW_PENDING", index=True)
    export_status: Mapped[str] = mapped_column(String(64), default="NOT_EXPORTED")
    version: Mapped[int] = mapped_column(Integer, default=1)
    provenance: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)


class ContentReviewEvent(Base):
    __tablename__ = "content_review_events"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    item_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("content_items.id"), nullable=False, index=True)
    reviewer_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False))
    decision: Mapped[str] = mapped_column(String(64), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text)
    checklist: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class ContentExport(Base):
    __tablename__ = "content_exports"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    batch_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("content_batches.id"), index=True)
    export_format: Mapped[str] = mapped_column(String(32), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    item_count: Mapped[int] = mapped_column(Integer, default=0)
    manifest: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class EvalRun(Base):
    __tablename__ = "eval_runs"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    model_version: Mapped[str] = mapped_column(String(128), nullable=False)
    benchmark_name: Mapped[str] = mapped_column(String(128), nullable=False)
    score: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    hard_failures: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, default=list)
    approved: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class ReleaseGate(Base):
    __tablename__ = "release_gates"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    artifact_type: Mapped[str] = mapped_column(String(64), nullable=False)
    artifact_version: Mapped[str] = mapped_column(String(128), nullable=False)
    allowed: Mapped[bool] = mapped_column(Boolean, default=False)
    metrics: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    hard_failures: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, default=list)
    required_approvals: Mapped[list[str]] = mapped_column(JSONB, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class WebSource(Base):
    __tablename__ = "web_sources"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    url: Mapped[str] = mapped_column(String(2048), nullable=False, unique=True)
    title: Mapped[str | None] = mapped_column(String(512))
    robots_status: Mapped[str] = mapped_column(String(64), default="UNKNOWN")
    tos_status: Mapped[str] = mapped_column(String(64), default="UNKNOWN")
    rights_status: Mapped[str] = mapped_column(String(64), default="UNKNOWN")
    content_hash: Mapped[str | None] = mapped_column(String(64))
    extracted_text: Mapped[str | None] = mapped_column(Text)
    quality_score: Mapped[float] = mapped_column(Float, default=0.0)
    provenance: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    actor_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False))
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    object_type: Mapped[str] = mapped_column(String(128), nullable=False)
    object_id: Mapped[str | None] = mapped_column(String(128))
    details: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


# --- v0.5 runtime invocation audit model ---
class RuntimeInvocation(Base):
    __tablename__ = "runtime_invocations"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    provider: Mapped[str] = mapped_column(String(128), nullable=False)
    model_name: Mapped[str] = mapped_column(String(128), nullable=False)
    request_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(64), default="COMPLETED")
    usage: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    warnings: Mapped[list[str]] = mapped_column(JSONB, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


# --- v0.6 corpus ingestion and review ledger models ---
class SourceFile(Base):
    __tablename__ = "source_files"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    source_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("sources.id"), nullable=False, index=True)
    original_filename: Mapped[str] = mapped_column(String(512), nullable=False)
    content_type: Mapped[str | None] = mapped_column(String(128))
    byte_size: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    checksum_sha256: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    storage_uri: Mapped[str] = mapped_column(String(1024), nullable=False)
    extraction_status: Mapped[str] = mapped_column(String(64), nullable=False, default="PENDING")
    extraction_report: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class SourceReviewEvent(Base):
    __tablename__ = "source_review_events"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    source_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("sources.id"), nullable=False, index=True)
    reviewer_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False))
    decision: Mapped[str] = mapped_column(String(64), nullable=False)
    rights_status: Mapped[str | None] = mapped_column(String(64))
    ingestion_status: Mapped[str | None] = mapped_column(String(64))
    evidence: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class ChunkReviewEvent(Base):
    __tablename__ = "chunk_review_events"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    chunk_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("chunks.id"), nullable=False, index=True)
    reviewer_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False))
    decision: Mapped[str] = mapped_column(String(64), nullable=False)
    previous_status: Mapped[str | None] = mapped_column(String(64))
    new_status: Mapped[str] = mapped_column(String(64), nullable=False)
    previous_text_hash: Mapped[str | None] = mapped_column(String(64))
    revised_text_hash: Mapped[str | None] = mapped_column(String(64))
    checklist: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class IngestionRun(Base):
    __tablename__ = "ingestion_runs"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    source_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("sources.id"), nullable=False, index=True)
    source_file_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("source_files.id"))
    status: Mapped[str] = mapped_column(String(64), nullable=False, default="COMPLETED")
    stage_report: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    chunks_created: Mapped[int] = mapped_column(Integer, default=0)
    indexed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

class EvalCase(Base):
    __tablename__ = "eval_cases"
    __table_args__ = (UniqueConstraint("case_id", name="uq_eval_cases_case_id"),)

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    case_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    benchmark_name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    expected_behavior: Mapped[str | None] = mapped_column(Text)
    required_citations: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, default=list)
    blocked_behaviors: Mapped[list[str]] = mapped_column(JSONB, default=list)
    severity: Mapped[str] = mapped_column(String(64), nullable=False, default="soft_fail")
    grader_config: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    source_file: Mapped[str | None] = mapped_column(String(512))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class EvalCaseResult(Base):
    __tablename__ = "eval_case_results"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    eval_run_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("eval_runs.id"), nullable=False, index=True)
    case_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    severity: Mapped[str] = mapped_column(String(64), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    grader: Mapped[str] = mapped_column(String(128), nullable=False, default="deterministic_v0_7")
    findings: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    answer_preview: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class CitationCheckRun(Base):
    __tablename__ = "citation_check_runs"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    answer_text: Mapped[str] = mapped_column(Text, nullable=False)
    citations: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, default=list)
    alignment_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    findings: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class SourceExplorerQuery(Base):
    __tablename__ = "source_explorer_queries"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    query: Mapped[str | None] = mapped_column(String(512))
    filters: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    result_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    public: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


# --- v0.8 web-to-corpus, OCR, quality, and provenance models ---
class CrawlJob(Base):
    __tablename__ = "crawl_jobs"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    url: Mapped[str] = mapped_column(String(2048), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(64), nullable=False, default="REGISTERED", index=True)
    robots_status: Mapped[str] = mapped_column(String(64), nullable=False, default="UNKNOWN")
    rights_status: Mapped[str] = mapped_column(String(64), nullable=False, default="UNKNOWN")
    fetch_requested: Mapped[bool] = mapped_column(Boolean, default=False)
    fetched_bytes: Mapped[int] = mapped_column(Integer, default=0)
    extracted_text_hash: Mapped[str | None] = mapped_column(String(64))
    quality_score: Mapped[float] = mapped_column(Float, default=0.0)
    error: Mapped[str | None] = mapped_column(Text)
    result: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)


class OCRJob(Base):
    __tablename__ = "ocr_jobs"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    filename: Mapped[str] = mapped_column(String(512), nullable=False)
    status: Mapped[str] = mapped_column(String(64), nullable=False, default="ANALYZED", index=True)
    engine: Mapped[str] = mapped_column(String(64), nullable=False, default="deterministic")
    page_count: Mapped[int] = mapped_column(Integer, default=0)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    text_hash: Mapped[str | None] = mapped_column(String(64))
    output_uri: Mapped[str | None] = mapped_column(String(1024))
    report: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class SourceQualityScore(Base):
    __tablename__ = "source_quality_scores"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    source_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("sources.id"), index=True)
    web_source_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("web_sources.id"), index=True)
    score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    components: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    verdict: Mapped[str] = mapped_column(String(64), nullable=False, default="REVIEW_REQUIRED")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class ProvenanceEvent(Base):
    __tablename__ = "provenance_events"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    object_type: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    object_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    actor_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False))
    evidence: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


# --- v0.9 Qwen training, ModelOps, serving, release, and production hardening models ---
class TrainingDataset(Base):
    __tablename__ = "training_datasets"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(256), nullable=False, unique=True)
    base_model: Mapped[str] = mapped_column(String(256), nullable=False)
    sample_count: Mapped[int] = mapped_column(Integer, default=0)
    artifact_uri: Mapped[str] = mapped_column(String(1024), nullable=False)
    manifest: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    status: Mapped[str] = mapped_column(String(64), default="BUILT", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class TrainingRun(Base):
    __tablename__ = "training_runs"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    dataset_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("training_datasets.id"), index=True)
    base_model: Mapped[str] = mapped_column(String(256), nullable=False)
    adapter_method: Mapped[str] = mapped_column(String(64), nullable=False, default="qlora")
    status: Mapped[str] = mapped_column(String(64), default="PLANNED", index=True)
    config: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    metrics: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    checkpoint_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)


class ModelCheckpoint(Base):
    __tablename__ = "model_checkpoints"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    run_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("training_runs.id"), index=True)
    model_name: Mapped[str] = mapped_column(String(256), nullable=False)
    base_model: Mapped[str] = mapped_column(String(256), nullable=False)
    adapter_uri: Mapped[str] = mapped_column(String(1024), nullable=False)
    checksum_sha256: Mapped[str | None] = mapped_column(String(64))
    eval_summary: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    release_status: Mapped[str] = mapped_column(String(64), default="UNRELEASED", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class ModelRelease(Base):
    __tablename__ = "model_releases"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    checkpoint_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("model_checkpoints.id"), nullable=False, index=True)
    release_name: Mapped[str] = mapped_column(String(256), nullable=False)
    environment: Mapped[str] = mapped_column(String(64), nullable=False, default="staging")
    allowed: Mapped[bool] = mapped_column(Boolean, default=False)
    gate_report: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    rollback_target: Mapped[str | None] = mapped_column(UUID(as_uuid=False))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class ServingProfile(Base):
    __tablename__ = "serving_profiles"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    model_name: Mapped[str] = mapped_column(String(256), nullable=False)
    runtime_mode: Mapped[str] = mapped_column(String(64), nullable=False, default="openai_compatible")
    endpoint_url: Mapped[str | None] = mapped_column(String(1024))
    config: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    active: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class BackupRun(Base):
    __tablename__ = "backup_runs"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    status: Mapped[str] = mapped_column(String(64), nullable=False, default="SIMULATED")
    backup_type: Mapped[str] = mapped_column(String(64), nullable=False, default="metadata")
    artifact_uri: Mapped[str | None] = mapped_column(String(1024))
    manifest: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class ProductionIncident(Base):
    __tablename__ = "production_incidents"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    severity: Mapped[str] = mapped_column(String(16), nullable=False, default="P3", index=True)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    status: Mapped[str] = mapped_column(String(64), nullable=False, default="OPEN", index=True)
    description: Mapped[str | None] = mapped_column(Text)
    evidence: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


# --- v1.0.1 canonical corpus DB and relaxed ingestion models ---
class CanonicalWork(Base):
    __tablename__ = "canonical_works"
    __table_args__ = (UniqueConstraint("work_key", name="uq_canonical_works_work_key"),)

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    work_key: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    title_sa: Mapped[str | None] = mapped_column(String(512))
    title_hi: Mapped[str | None] = mapped_column(String(512))
    title_en: Mapped[str | None] = mapped_column(String(512))
    category: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    tradition_scope: Mapped[list[str]] = mapped_column(JSONB, default=list)
    authority_level: Mapped[str] = mapped_column(String(64), nullable=False, default="PRIMARY")
    canonical_status: Mapped[str] = mapped_column(String(64), nullable=False, default="DRAFT", index=True)
    metadata_json: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)


class CanonicalEdition(Base):
    __tablename__ = "canonical_editions"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    work_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("canonical_works.id"), nullable=False, index=True)
    edition_key: Mapped[str] = mapped_column(String(192), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    language: Mapped[str | None] = mapped_column(String(32))
    editor_or_translator: Mapped[str | None] = mapped_column(String(512))
    publisher: Mapped[str | None] = mapped_column(String(512))
    publication_year: Mapped[int | None] = mapped_column(Integer)
    rights_status: Mapped[str] = mapped_column(String(64), nullable=False, default="UNKNOWN")
    source_uri: Mapped[str | None] = mapped_column(String(2048))
    checksum_sha256: Mapped[str | None] = mapped_column(String(64), index=True)
    metadata_json: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class CanonicalPassage(Base):
    __tablename__ = "canonical_passages"
    __table_args__ = (UniqueConstraint("work_id", "locator", name="uq_canonical_passage_locator"),)

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    work_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("canonical_works.id"), nullable=False, index=True)
    edition_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("canonical_editions.id"), index=True)
    locator: Mapped[str] = mapped_column(String(256), nullable=False, index=True)
    locator_sort_key: Mapped[str | None] = mapped_column(String(256), index=True)
    sanskrit_text: Mapped[str | None] = mapped_column(Text)
    normalized_text: Mapped[str] = mapped_column(Text, nullable=False)
    translation_hi: Mapped[str | None] = mapped_column(Text)
    translation_en: Mapped[str | None] = mapped_column(Text)
    chapter: Mapped[str | None] = mapped_column(String(128))
    verse: Mapped[str | None] = mapped_column(String(128))
    section: Mapped[str | None] = mapped_column(String(128))
    source_ids: Mapped[list[str]] = mapped_column(JSONB, default=list)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    review_status: Mapped[str] = mapped_column(String(64), nullable=False, default="REVIEW_PENDING", index=True)
    authority_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    metadata_json: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)


class SourceSnapshot(Base):
    __tablename__ = "source_snapshots"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    source_uri: Mapped[str] = mapped_column(String(2048), nullable=False, index=True)
    source_kind: Mapped[str] = mapped_column(String(64), nullable=False, default="web")
    zone: Mapped[str] = mapped_column(String(64), nullable=False, default="Z1_QUARANTINE", index=True)
    title: Mapped[str | None] = mapped_column(String(512))
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    raw_text_uri: Mapped[str | None] = mapped_column(String(1024))
    extracted_text_preview: Mapped[str | None] = mapped_column(Text)
    robots_status: Mapped[str] = mapped_column(String(64), nullable=False, default="UNKNOWN")
    rights_observation: Mapped[str] = mapped_column(String(64), nullable=False, default="UNKNOWN")
    quality_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    metadata_json: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class ClaimEvidence(Base):
    __tablename__ = "claim_evidence"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    claim_text: Mapped[str] = mapped_column(Text, nullable=False)
    passage_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("canonical_passages.id"), index=True)
    support_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    evidence_grade: Mapped[str] = mapped_column(String(8), nullable=False, default="F", index=True)
    evidence_type: Mapped[str] = mapped_column(String(64), nullable=False, default="deterministic_text_overlap")
    report: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class CorpusPromotionEvent(Base):
    __tablename__ = "corpus_promotion_events"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    object_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    object_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    from_zone: Mapped[str] = mapped_column(String(64), nullable=False)
    to_zone: Mapped[str] = mapped_column(String(64), nullable=False)
    decision: Mapped[str] = mapped_column(String(64), nullable=False)
    reviewer_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False))
    evidence: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

# --- v1.0.5 remote-Qwen chatbot product, accounts, publishing, analytics, and billing models ---
class AppUser(Base):
    __tablename__ = "app_users"
    __table_args__ = (UniqueConstraint("email", name="uq_app_users_email"),)

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    email: Mapped[str] = mapped_column(String(320), nullable=False, index=True)
    display_name: Mapped[str | None] = mapped_column(String(256))
    role: Mapped[str] = mapped_column(String(64), nullable=False, default="viewer", index=True)
    status: Mapped[str] = mapped_column(String(64), nullable=False, default="ACTIVE", index=True)
    preferences: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("app_users.id"), index=True)
    title: Mapped[str] = mapped_column(String(512), nullable=False, default="New Atman Chat")
    mode: Mapped[str] = mapped_column(String(64), nullable=False, default="simple", index=True)
    language: Mapped[str] = mapped_column(String(32), nullable=False, default="hi")
    citation_mode: Mapped[str] = mapped_column(String(32), nullable=False, default="hidden")
    status: Mapped[str] = mapped_column(String(64), nullable=False, default="ACTIVE", index=True)
    session_metadata: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    session_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("chat_sessions.id"), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    model_name: Mapped[str | None] = mapped_column(String(256))
    provider: Mapped[str | None] = mapped_column(String(128))
    citation_mode: Mapped[str] = mapped_column(String(32), nullable=False, default="hidden")
    visible_citations: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, default=list)
    internal_evidence: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, default=list)
    safety_report: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    usage: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class ChatRetrievalTrace(Base):
    __tablename__ = "chat_retrieval_traces"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    message_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("chat_messages.id"), nullable=False, index=True)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    retrieved_chunks: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, default=list)
    canonical_evidence: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, default=list)
    claim_checks: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, default=list)
    trace_report: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class ChatFeedback(Base):
    __tablename__ = "chat_feedback"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    message_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("chat_messages.id"), nullable=False, index=True)
    user_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("app_users.id"), index=True)
    rating: Mapped[str] = mapped_column(String(32), nullable=False, default="neutral", index=True)
    reason: Mapped[str | None] = mapped_column(Text)
    correction: Mapped[str | None] = mapped_column(Text)
    feedback_metadata: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class ModelUsageLog(Base):
    __tablename__ = "model_usage_logs"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    provider: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    model_name: Mapped[str] = mapped_column(String(256), nullable=False, index=True)
    feature: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    user_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("app_users.id"), index=True)
    session_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("chat_sessions.id"), index=True)
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    estimated_cost: Mapped[float] = mapped_column(Float, default=0.0)
    currency: Mapped[str] = mapped_column(String(16), default="USD")
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(64), default="COMPLETED", index=True)
    usage_metadata: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class PublishingChannel(Base):
    __tablename__ = "publishing_channels"
    __table_args__ = (UniqueConstraint("name", name="uq_publishing_channels_name"),)

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    channel_type: Mapped[str] = mapped_column(String(64), nullable=False, default="manual_export")
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    config: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class ContentPublication(Base):
    __tablename__ = "content_publications"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    content_item_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("content_items.id"), index=True)
    channel_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("publishing_channels.id"), index=True)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(64), nullable=False, default="DRAFT", index=True)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    public_slug: Mapped[str | None] = mapped_column(String(256), index=True)
    export_uri: Mapped[str | None] = mapped_column(String(1024))
    publication_metadata: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)


class ProductEvent(Base):
    __tablename__ = "product_events"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    event_type: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    actor_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("app_users.id"), index=True)
    object_type: Mapped[str | None] = mapped_column(String(128), index=True)
    object_id: Mapped[str | None] = mapped_column(String(128), index=True)
    event_metadata: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class AcquisitionJob(Base):
    __tablename__ = "acquisition_jobs"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    source_uri: Mapped[str] = mapped_column(String(2048), nullable=False, index=True)
    mode: Mapped[str] = mapped_column(String(64), nullable=False, default="wide_discovery")
    status: Mapped[str] = mapped_column(String(64), nullable=False, default="QUEUED", index=True)
    zone: Mapped[str] = mapped_column(String(64), nullable=False, default="Z1_QUARANTINE", index=True)
    discovered_title: Mapped[str | None] = mapped_column(String(512))
    quality_score: Mapped[float] = mapped_column(Float, default=0.0)
    rights_signal: Mapped[str] = mapped_column(String(64), default="UNKNOWN")
    canonical_candidate: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    report: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)


class BillingLedgerEntry(Base):
    __tablename__ = "billing_ledger_entries"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("app_users.id"), index=True)
    ledger_type: Mapped[str] = mapped_column(String(64), nullable=False, default="model_usage", index=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    currency: Mapped[str] = mapped_column(String(16), nullable=False, default="USD")
    status: Mapped[str] = mapped_column(String(64), nullable=False, default="RECORDED", index=True)
    reference_type: Mapped[str | None] = mapped_column(String(128))
    reference_id: Mapped[str | None] = mapped_column(String(128))
    ledger_metadata: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

# --- v2.0 Dharma Knowledge OS + parallel Model Lab models ---
class LearningPath(Base):
    __tablename__ = "learning_paths"
    __table_args__ = (UniqueConstraint("slug", name="uq_learning_paths_slug"),)

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    slug: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    language: Mapped[str] = mapped_column(String(32), nullable=False, default="hi")
    difficulty: Mapped[str] = mapped_column(String(64), nullable=False, default="beginner")
    description: Mapped[str | None] = mapped_column(Text)
    canonical_work_keys: Mapped[list[str]] = mapped_column(JSONB, default=list)
    modules: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, default=list)
    status: Mapped[str] = mapped_column(String(64), nullable=False, default="DRAFT", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)


class SavedAnswer(Base):
    __tablename__ = "saved_answers"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("app_users.id"), index=True)
    message_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("chat_messages.id"), index=True)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    answer_text: Mapped[str] = mapped_column(Text, nullable=False)
    tags: Mapped[list[str]] = mapped_column(JSONB, default=list)
    source_summary: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class LessonProgress(Base):
    __tablename__ = "lesson_progress"
    __table_args__ = (UniqueConstraint("user_id", "learning_path_id", "lesson_key", name="uq_lesson_progress_user_path_lesson"),)

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("app_users.id"), nullable=False, index=True)
    learning_path_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("learning_paths.id"), nullable=False, index=True)
    lesson_key: Mapped[str] = mapped_column(String(256), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(64), nullable=False, default="NOT_STARTED", index=True)
    score: Mapped[float] = mapped_column(Float, default=0.0)
    progress_metadata: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)


class ModelLabExperiment(Base):
    __tablename__ = "model_lab_experiments"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(256), nullable=False, index=True)
    base_model: Mapped[str] = mapped_column(String(256), nullable=False, default="Qwen/Qwen3-14B")
    objective: Mapped[str] = mapped_column(String(128), nullable=False, default="instruction_tuning")
    status: Mapped[str] = mapped_column(String(64), nullable=False, default="PLANNED", index=True)
    dataset_plan: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    training_config: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    eval_plan: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    gate_report: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    owner_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("app_users.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)


class FailureCase(Base):
    __tablename__ = "failure_cases"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    source_type: Mapped[str] = mapped_column(String(128), nullable=False, default="chat_feedback", index=True)
    source_id: Mapped[str | None] = mapped_column(String(128), index=True)
    severity: Mapped[str] = mapped_column(String(64), nullable=False, default="medium", index=True)
    category: Mapped[str] = mapped_column(String(128), nullable=False, default="unsupported_claim", index=True)
    question: Mapped[str | None] = mapped_column(Text)
    bad_answer: Mapped[str | None] = mapped_column(Text)
    corrected_answer: Mapped[str | None] = mapped_column(Text)
    evidence: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    dataset_status: Mapped[str] = mapped_column(String(64), nullable=False, default="CANDIDATE", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class ClaimEvidenceReview(Base):
    __tablename__ = "claim_evidence_reviews"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    claim_text: Mapped[str] = mapped_column(Text, nullable=False)
    support_grade: Mapped[str] = mapped_column(String(8), nullable=False, default="D", index=True)
    verdict: Mapped[str] = mapped_column(String(64), nullable=False, default="REVIEW_REQUIRED", index=True)
    evidence: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, default=list)
    reviewer_notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
