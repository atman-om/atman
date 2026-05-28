"""v2.0 Dharma Knowledge OS and parallel Model Lab

Revision ID: 0010_v2_knowledge_os_model_lab
Revises: 0009_v105_chatbot_accounts_publishing_analytics
Create Date: 2026-05-28
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0010_v2_knowledge_os_model_lab"
down_revision = "0009_v105_chatbot_accounts_publishing_analytics"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "learning_paths",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("slug", sa.String(length=160), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("language", sa.String(length=32), nullable=False, server_default="hi"),
        sa.Column("difficulty", sa.String(length=64), nullable=False, server_default="beginner"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("canonical_work_keys", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("modules", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("status", sa.String(length=64), nullable=False, server_default="DRAFT"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("slug", name="uq_learning_paths_slug"),
    )
    op.create_index("ix_learning_paths_slug", "learning_paths", ["slug"])
    op.create_index("ix_learning_paths_status", "learning_paths", ["status"])
    op.create_table(
        "saved_answers",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("app_users.id"), nullable=True),
        sa.Column("message_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("chat_messages.id"), nullable=True),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("answer_text", sa.Text(), nullable=False),
        sa.Column("tags", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("source_summary", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_saved_answers_user_id", "saved_answers", ["user_id"])
    op.create_table(
        "lesson_progress",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("app_users.id"), nullable=False),
        sa.Column("learning_path_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("learning_paths.id"), nullable=False),
        sa.Column("lesson_key", sa.String(length=256), nullable=False),
        sa.Column("status", sa.String(length=64), nullable=False, server_default="NOT_STARTED"),
        sa.Column("score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("progress_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("user_id", "learning_path_id", "lesson_key", name="uq_lesson_progress_user_path_lesson"),
    )
    op.create_table(
        "model_lab_experiments",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("name", sa.String(length=256), nullable=False),
        sa.Column("base_model", sa.String(length=256), nullable=False, server_default="Qwen/Qwen3-14B"),
        sa.Column("objective", sa.String(length=128), nullable=False, server_default="instruction_tuning"),
        sa.Column("status", sa.String(length=64), nullable=False, server_default="PLANNED"),
        sa.Column("dataset_plan", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("training_config", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("eval_plan", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("gate_report", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("owner_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("app_users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_model_lab_experiments_status", "model_lab_experiments", ["status"])
    op.create_table(
        "failure_cases",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("source_type", sa.String(length=128), nullable=False, server_default="chat_feedback"),
        sa.Column("source_id", sa.String(length=128), nullable=True),
        sa.Column("severity", sa.String(length=64), nullable=False, server_default="medium"),
        sa.Column("category", sa.String(length=128), nullable=False, server_default="unsupported_claim"),
        sa.Column("question", sa.Text(), nullable=True),
        sa.Column("bad_answer", sa.Text(), nullable=True),
        sa.Column("corrected_answer", sa.Text(), nullable=True),
        sa.Column("evidence", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("dataset_status", sa.String(length=64), nullable=False, server_default="CANDIDATE"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "claim_evidence_reviews",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("claim_text", sa.Text(), nullable=False),
        sa.Column("support_grade", sa.String(length=8), nullable=False, server_default="D"),
        sa.Column("verdict", sa.String(length=64), nullable=False, server_default="REVIEW_REQUIRED"),
        sa.Column("evidence", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("reviewer_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("claim_evidence_reviews")
    op.drop_table("failure_cases")
    op.drop_table("model_lab_experiments")
    op.drop_table("lesson_progress")
    op.drop_table("saved_answers")
    op.drop_table("learning_paths")
