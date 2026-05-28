"""web-to-corpus and OCR v0.8 tables

Revision ID: 0006_web_to_corpus_ocr
Revises: 0005_eval_hardening_source_explorer
Create Date: 2026-05-28 00:00:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0006_web_to_corpus_ocr"
down_revision = "0005_eval_hardening_source_explorer"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "crawl_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("url", sa.String(2048), nullable=False),
        sa.Column("status", sa.String(64), nullable=False, server_default="REGISTERED"),
        sa.Column("robots_status", sa.String(64), nullable=False, server_default="UNKNOWN"),
        sa.Column("rights_status", sa.String(64), nullable=False, server_default="UNKNOWN"),
        sa.Column("fetch_requested", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("fetched_bytes", sa.Integer, nullable=False, server_default="0"),
        sa.Column("extracted_text_hash", sa.String(64)),
        sa.Column("quality_score", sa.Float, nullable=False, server_default="0"),
        sa.Column("error", sa.Text),
        sa.Column("result", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_crawl_jobs_url", "crawl_jobs", ["url"])
    op.create_index("ix_crawl_jobs_status", "crawl_jobs", ["status"])

    op.create_table(
        "ocr_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("filename", sa.String(512), nullable=False),
        sa.Column("status", sa.String(64), nullable=False, server_default="ANALYZED"),
        sa.Column("engine", sa.String(64), nullable=False, server_default="deterministic"),
        sa.Column("page_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("confidence", sa.Float, nullable=False, server_default="0"),
        sa.Column("text_hash", sa.String(64)),
        sa.Column("output_uri", sa.String(1024)),
        sa.Column("report", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_ocr_jobs_status", "ocr_jobs", ["status"])

    op.create_table(
        "source_quality_scores",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("source_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("sources.id")),
        sa.Column("web_source_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("web_sources.id")),
        sa.Column("score", sa.Float, nullable=False, server_default="0"),
        sa.Column("components", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("verdict", sa.String(64), nullable=False, server_default="REVIEW_REQUIRED"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_source_quality_scores_source_id", "source_quality_scores", ["source_id"])
    op.create_index("ix_source_quality_scores_web_source_id", "source_quality_scores", ["web_source_id"])

    op.create_table(
        "provenance_events",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("object_type", sa.String(128), nullable=False),
        sa.Column("object_id", sa.String(128), nullable=False),
        sa.Column("event_type", sa.String(128), nullable=False),
        sa.Column("actor_id", postgresql.UUID(as_uuid=False)),
        sa.Column("evidence", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_provenance_events_object_type", "provenance_events", ["object_type"])
    op.create_index("ix_provenance_events_object_id", "provenance_events", ["object_id"])
    op.create_index("ix_provenance_events_event_type", "provenance_events", ["event_type"])


def downgrade() -> None:
    op.drop_table("provenance_events")
    op.drop_table("source_quality_scores")
    op.drop_table("ocr_jobs")
    op.drop_table("crawl_jobs")
