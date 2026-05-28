"""corpus ingestion and review v0.6 tables

Revision ID: 0004_corpus_ingestion_review
Revises: 0003_public_qwen_runtime
Create Date: 2026-05-28 00:00:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0004_corpus_ingestion_review"
down_revision = "0003_public_qwen_runtime"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "source_files",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("source_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("sources.id"), nullable=False),
        sa.Column("original_filename", sa.String(512), nullable=False),
        sa.Column("content_type", sa.String(128)),
        sa.Column("byte_size", sa.Integer, nullable=False, server_default="0"),
        sa.Column("checksum_sha256", sa.String(64), nullable=False),
        sa.Column("storage_uri", sa.String(1024), nullable=False),
        sa.Column("extraction_status", sa.String(64), nullable=False, server_default="PENDING"),
        sa.Column("extraction_report", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_source_files_source_id", "source_files", ["source_id"])
    op.create_index("ix_source_files_checksum_sha256", "source_files", ["checksum_sha256"])

    op.create_table(
        "source_review_events",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("source_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("sources.id"), nullable=False),
        sa.Column("reviewer_id", postgresql.UUID(as_uuid=False)),
        sa.Column("decision", sa.String(64), nullable=False),
        sa.Column("rights_status", sa.String(64)),
        sa.Column("ingestion_status", sa.String(64)),
        sa.Column("evidence", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("notes", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_source_review_events_source_id", "source_review_events", ["source_id"])

    op.create_table(
        "chunk_review_events",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("chunk_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("chunks.id"), nullable=False),
        sa.Column("reviewer_id", postgresql.UUID(as_uuid=False)),
        sa.Column("decision", sa.String(64), nullable=False),
        sa.Column("previous_status", sa.String(64)),
        sa.Column("new_status", sa.String(64), nullable=False),
        sa.Column("previous_text_hash", sa.String(64)),
        sa.Column("revised_text_hash", sa.String(64)),
        sa.Column("checklist", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("notes", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_chunk_review_events_chunk_id", "chunk_review_events", ["chunk_id"])

    op.create_table(
        "ingestion_runs",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("source_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("sources.id"), nullable=False),
        sa.Column("source_file_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("source_files.id")),
        sa.Column("status", sa.String(64), nullable=False, server_default="COMPLETED"),
        sa.Column("stage_report", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("chunks_created", sa.Integer, nullable=False, server_default="0"),
        sa.Column("indexed", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_ingestion_runs_source_id", "ingestion_runs", ["source_id"])


def downgrade() -> None:
    op.drop_index("ix_ingestion_runs_source_id", table_name="ingestion_runs")
    op.drop_table("ingestion_runs")
    op.drop_index("ix_chunk_review_events_chunk_id", table_name="chunk_review_events")
    op.drop_table("chunk_review_events")
    op.drop_index("ix_source_review_events_source_id", table_name="source_review_events")
    op.drop_table("source_review_events")
    op.drop_index("ix_source_files_checksum_sha256", table_name="source_files")
    op.drop_index("ix_source_files_source_id", table_name="source_files")
    op.drop_table("source_files")
