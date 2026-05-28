"""public app and qwen runtime audit

Revision ID: 0003_public_qwen_runtime
Revises: 0002_content_factory
Create Date: 2026-05-28
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0003_public_qwen_runtime"
down_revision = "0002_content_factory"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "runtime_invocations",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("provider", sa.String(length=128), nullable=False),
        sa.Column("model_name", sa.String(length=128), nullable=False),
        sa.Column("request_hash", sa.String(length=64), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=64), nullable=False, server_default="COMPLETED"),
        sa.Column("usage", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("warnings", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_runtime_invocations_request_hash", "runtime_invocations", ["request_hash"])


def downgrade() -> None:
    op.drop_index("ix_runtime_invocations_request_hash", table_name="runtime_invocations")
    op.drop_table("runtime_invocations")
