"""initial Atman v0.3 schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-05-28 00:00:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sources",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("source_type", sa.String(64), nullable=False),
        sa.Column("title", sa.String(512), nullable=False),
        sa.Column("language", sa.String(32)),
        sa.Column("tradition_scope", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("rights_status", sa.String(64), nullable=False, server_default="UNKNOWN"),
        sa.Column("ingestion_status", sa.String(64), nullable=False, server_default="INGESTED"),
        sa.Column("checksum_sha256", sa.String(64), unique=True),
        sa.Column("source_metadata", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("uploaded_by", postgresql.UUID(as_uuid=False)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "chunks",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("source_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("sources.id"), nullable=False),
        sa.Column("chunk_text", sa.Text, nullable=False),
        sa.Column("token_count", sa.Integer, nullable=False),
        sa.Column("chunk_order", sa.Integer, nullable=False),
        sa.Column("citation_locator", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("quality_score", sa.Float, nullable=False, server_default="0"),
        sa.Column("review_status", sa.String(64), nullable=False, server_default="REVIEW_PENDING"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("source_id", "chunk_order", name="uq_chunks_source_order"),
    )
    op.create_index("ix_chunks_source_id", "chunks", ["source_id"])
    op.create_table(
        "embeddings",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("chunk_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("chunks.id"), nullable=False, unique=True),
        sa.Column("embedding_model", sa.String(128), nullable=False),
        sa.Column("vector_id", sa.String(128), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "rag_queries",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("question", sa.Text, nullable=False),
        sa.Column("answer", sa.Text, nullable=False),
        sa.Column("model_name", sa.String(128), nullable=False),
        sa.Column("citations", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("safety_report", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("latency_ms", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "content_items",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("content_type", sa.String(64), nullable=False),
        sa.Column("topic", sa.String(512), nullable=False),
        sa.Column("language", sa.String(32), nullable=False, server_default="hi"),
        sa.Column("body", sa.Text, nullable=False),
        sa.Column("source_chunk_ids", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("quality_report", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("review_status", sa.String(64), nullable=False, server_default="REVIEW_PENDING"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "eval_runs",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("model_version", sa.String(128), nullable=False),
        sa.Column("benchmark_name", sa.String(128), nullable=False),
        sa.Column("score", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("hard_failures", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("approved", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "release_gates",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("artifact_type", sa.String(64), nullable=False),
        sa.Column("artifact_version", sa.String(128), nullable=False),
        sa.Column("allowed", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("metrics", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("hard_failures", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("required_approvals", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "web_sources",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("url", sa.String(2048), nullable=False, unique=True),
        sa.Column("title", sa.String(512)),
        sa.Column("robots_status", sa.String(64), nullable=False, server_default="UNKNOWN"),
        sa.Column("tos_status", sa.String(64), nullable=False, server_default="UNKNOWN"),
        sa.Column("rights_status", sa.String(64), nullable=False, server_default="UNKNOWN"),
        sa.Column("content_hash", sa.String(64)),
        sa.Column("extracted_text", sa.Text),
        sa.Column("quality_score", sa.Float, nullable=False, server_default="0"),
        sa.Column("provenance", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("actor_id", postgresql.UUID(as_uuid=False)),
        sa.Column("action", sa.String(128), nullable=False),
        sa.Column("object_type", sa.String(128), nullable=False),
        sa.Column("object_id", sa.String(128)),
        sa.Column("details", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    for table in [
        "audit_logs", "web_sources", "release_gates", "eval_runs", "content_items",
        "rag_queries", "embeddings", "chunks", "sources",
    ]:
        op.drop_table(table)
