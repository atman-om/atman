"""qwen serving and canonical corpus db

Revision ID: 0008_qwen_serving_canonical_corpus
Revises: 0007_qwen_training_modelops_prod
Create Date: 2026-05-28
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0008_qwen_serving_canonical_corpus"
down_revision = "0007_qwen_training_modelops_prod"
branch_labels = None
depends_on = None

JSON = postgresql.JSONB(astext_type=sa.Text())


def upgrade() -> None:
    op.create_table(
        "canonical_works",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("work_key", sa.String(length=128), nullable=False),
        sa.Column("title_sa", sa.String(length=512)),
        sa.Column("title_hi", sa.String(length=512)),
        sa.Column("title_en", sa.String(length=512)),
        sa.Column("category", sa.String(length=128), nullable=False),
        sa.Column("tradition_scope", JSON, nullable=False, server_default="[]"),
        sa.Column("authority_level", sa.String(length=64), nullable=False, server_default="PRIMARY"),
        sa.Column("canonical_status", sa.String(length=64), nullable=False, server_default="DRAFT"),
        sa.Column("metadata", JSON, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("work_key", name="uq_canonical_works_work_key"),
    )
    op.create_index("ix_canonical_works_work_key", "canonical_works", ["work_key"])
    op.create_index("ix_canonical_works_category", "canonical_works", ["category"])
    op.create_index("ix_canonical_works_canonical_status", "canonical_works", ["canonical_status"])

    op.create_table(
        "canonical_editions",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("work_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("canonical_works.id"), nullable=False),
        sa.Column("edition_key", sa.String(length=192), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("language", sa.String(length=32)),
        sa.Column("editor_or_translator", sa.String(length=512)),
        sa.Column("publisher", sa.String(length=512)),
        sa.Column("publication_year", sa.Integer()),
        sa.Column("rights_status", sa.String(length=64), nullable=False, server_default="UNKNOWN"),
        sa.Column("source_uri", sa.String(length=2048)),
        sa.Column("checksum_sha256", sa.String(length=64)),
        sa.Column("metadata", JSON, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_canonical_editions_work_id", "canonical_editions", ["work_id"])
    op.create_index("ix_canonical_editions_edition_key", "canonical_editions", ["edition_key"])
    op.create_index("ix_canonical_editions_checksum_sha256", "canonical_editions", ["checksum_sha256"])

    op.create_table(
        "canonical_passages",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("work_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("canonical_works.id"), nullable=False),
        sa.Column("edition_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("canonical_editions.id")),
        sa.Column("locator", sa.String(length=256), nullable=False),
        sa.Column("locator_sort_key", sa.String(length=256)),
        sa.Column("sanskrit_text", sa.Text()),
        sa.Column("normalized_text", sa.Text(), nullable=False),
        sa.Column("translation_hi", sa.Text()),
        sa.Column("translation_en", sa.Text()),
        sa.Column("chapter", sa.String(length=128)),
        sa.Column("verse", sa.String(length=128)),
        sa.Column("section", sa.String(length=128)),
        sa.Column("source_ids", JSON, nullable=False, server_default="[]"),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0"),
        sa.Column("review_status", sa.String(length=64), nullable=False, server_default="REVIEW_PENDING"),
        sa.Column("authority_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("metadata", JSON, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("work_id", "locator", name="uq_canonical_passage_locator"),
    )
    op.create_index("ix_canonical_passages_work_id", "canonical_passages", ["work_id"])
    op.create_index("ix_canonical_passages_edition_id", "canonical_passages", ["edition_id"])
    op.create_index("ix_canonical_passages_locator", "canonical_passages", ["locator"])
    op.create_index("ix_canonical_passages_locator_sort_key", "canonical_passages", ["locator_sort_key"])
    op.create_index("ix_canonical_passages_review_status", "canonical_passages", ["review_status"])

    op.create_table(
        "source_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("source_uri", sa.String(length=2048), nullable=False),
        sa.Column("source_kind", sa.String(length=64), nullable=False, server_default="web"),
        sa.Column("zone", sa.String(length=64), nullable=False, server_default="Z1_QUARANTINE"),
        sa.Column("title", sa.String(length=512)),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("raw_text_uri", sa.String(length=1024)),
        sa.Column("extracted_text_preview", sa.Text()),
        sa.Column("robots_status", sa.String(length=64), nullable=False, server_default="UNKNOWN"),
        sa.Column("rights_observation", sa.String(length=64), nullable=False, server_default="UNKNOWN"),
        sa.Column("quality_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("metadata", JSON, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_source_snapshots_source_uri", "source_snapshots", ["source_uri"])
    op.create_index("ix_source_snapshots_zone", "source_snapshots", ["zone"])
    op.create_index("ix_source_snapshots_content_hash", "source_snapshots", ["content_hash"])

    op.create_table(
        "claim_evidence",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("claim_text", sa.Text(), nullable=False),
        sa.Column("passage_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("canonical_passages.id")),
        sa.Column("support_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("evidence_grade", sa.String(length=8), nullable=False, server_default="F"),
        sa.Column("evidence_type", sa.String(length=64), nullable=False, server_default="deterministic_text_overlap"),
        sa.Column("report", JSON, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_claim_evidence_passage_id", "claim_evidence", ["passage_id"])
    op.create_index("ix_claim_evidence_evidence_grade", "claim_evidence", ["evidence_grade"])

    op.create_table(
        "corpus_promotion_events",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("object_type", sa.String(length=64), nullable=False),
        sa.Column("object_id", sa.String(length=128), nullable=False),
        sa.Column("from_zone", sa.String(length=64), nullable=False),
        sa.Column("to_zone", sa.String(length=64), nullable=False),
        sa.Column("decision", sa.String(length=64), nullable=False),
        sa.Column("reviewer_id", postgresql.UUID(as_uuid=False)),
        sa.Column("evidence", JSON, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_corpus_promotion_events_object_type", "corpus_promotion_events", ["object_type"])
    op.create_index("ix_corpus_promotion_events_object_id", "corpus_promotion_events", ["object_id"])


def downgrade() -> None:
    op.drop_table("corpus_promotion_events")
    op.drop_table("claim_evidence")
    op.drop_table("source_snapshots")
    op.drop_table("canonical_passages")
    op.drop_table("canonical_editions")
    op.drop_table("canonical_works")
