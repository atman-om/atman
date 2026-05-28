"""eval hardening and source explorer v0.7 tables

Revision ID: 0005_eval_hardening_source_explorer
Revises: 0004_corpus_ingestion_review
Create Date: 2026-05-28 00:00:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0005_eval_hardening_source_explorer"
down_revision = "0004_corpus_ingestion_review"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "eval_cases",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("case_id", sa.String(128), nullable=False),
        sa.Column("benchmark_name", sa.String(128), nullable=False),
        sa.Column("category", sa.String(128), nullable=False),
        sa.Column("question", sa.Text, nullable=False),
        sa.Column("expected_behavior", sa.Text),
        sa.Column("required_citations", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("blocked_behaviors", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("severity", sa.String(64), nullable=False, server_default="soft_fail"),
        sa.Column("grader_config", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("source_file", sa.String(512)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("case_id", name="uq_eval_cases_case_id"),
    )
    op.create_index("ix_eval_cases_case_id", "eval_cases", ["case_id"])
    op.create_index("ix_eval_cases_benchmark_name", "eval_cases", ["benchmark_name"])
    op.create_index("ix_eval_cases_category", "eval_cases", ["category"])

    op.create_table(
        "eval_case_results",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("eval_run_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("eval_runs.id"), nullable=False),
        sa.Column("case_id", sa.String(128), nullable=False),
        sa.Column("category", sa.String(128), nullable=False),
        sa.Column("passed", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("severity", sa.String(64), nullable=False),
        sa.Column("score", sa.Float, nullable=False, server_default="0"),
        sa.Column("grader", sa.String(128), nullable=False, server_default="deterministic_v0_7"),
        sa.Column("findings", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("answer_preview", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_eval_case_results_eval_run_id", "eval_case_results", ["eval_run_id"])
    op.create_index("ix_eval_case_results_case_id", "eval_case_results", ["case_id"])
    op.create_index("ix_eval_case_results_category", "eval_case_results", ["category"])

    op.create_table(
        "citation_check_runs",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("answer_text", sa.Text, nullable=False),
        sa.Column("citations", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("alignment_score", sa.Float, nullable=False, server_default="0"),
        sa.Column("passed", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("findings", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "source_explorer_queries",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("query", sa.String(512)),
        sa.Column("filters", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("result_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("public", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("source_explorer_queries")
    op.drop_table("citation_check_runs")
    op.drop_index("ix_eval_case_results_category", table_name="eval_case_results")
    op.drop_index("ix_eval_case_results_case_id", table_name="eval_case_results")
    op.drop_index("ix_eval_case_results_eval_run_id", table_name="eval_case_results")
    op.drop_table("eval_case_results")
    op.drop_index("ix_eval_cases_category", table_name="eval_cases")
    op.drop_index("ix_eval_cases_benchmark_name", table_name="eval_cases")
    op.drop_index("ix_eval_cases_case_id", table_name="eval_cases")
    op.drop_table("eval_cases")
