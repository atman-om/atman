"""v1.0.5 chatbot accounts publishing analytics

Revision ID: 0009_v105_chatbot_accounts_publishing_analytics
Revises: 0008_qwen_serving_canonical_corpus
Create Date: 2026-05-28
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0009_v105_chatbot_accounts_publishing_analytics"
down_revision = "0008_qwen_serving_canonical_corpus"
branch_labels = None
depends_on = None

JSON = postgresql.JSONB(astext_type=sa.Text())


def uuid_col(name: str = "id", *, primary_key: bool = False, nullable: bool = True) -> sa.Column:
    return sa.Column(name, postgresql.UUID(as_uuid=False), primary_key=primary_key, nullable=nullable)


def timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    ]


def upgrade() -> None:
    op.create_table(
        "app_users",
        uuid_col(primary_key=True),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("display_name", sa.String(length=256)),
        sa.Column("role", sa.String(length=64), nullable=False, server_default="viewer"),
        sa.Column("status", sa.String(length=64), nullable=False, server_default="ACTIVE"),
        sa.Column("preferences", JSON, nullable=False, server_default="{}"),
        *timestamps(),
        sa.UniqueConstraint("email", name="uq_app_users_email"),
    )
    op.create_index("ix_app_users_email", "app_users", ["email"])
    op.create_index("ix_app_users_role", "app_users", ["role"])
    op.create_index("ix_app_users_status", "app_users", ["status"])

    op.create_table(
        "chat_sessions",
        uuid_col(primary_key=True),
        uuid_col("user_id"),
        sa.Column("title", sa.String(length=512), nullable=False, server_default="New Atman Chat"),
        sa.Column("mode", sa.String(length=64), nullable=False, server_default="simple"),
        sa.Column("language", sa.String(length=32), nullable=False, server_default="hi"),
        sa.Column("citation_mode", sa.String(length=32), nullable=False, server_default="hidden"),
        sa.Column("status", sa.String(length=64), nullable=False, server_default="ACTIVE"),
        sa.Column("session_metadata", JSON, nullable=False, server_default="{}"),
        *timestamps(),
        sa.ForeignKeyConstraint(["user_id"], ["app_users.id"]),
    )
    op.create_index("ix_chat_sessions_user_id", "chat_sessions", ["user_id"])
    op.create_index("ix_chat_sessions_mode", "chat_sessions", ["mode"])
    op.create_index("ix_chat_sessions_status", "chat_sessions", ["status"])

    op.create_table(
        "chat_messages",
        uuid_col(primary_key=True),
        uuid_col("session_id", nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("model_name", sa.String(length=256)),
        sa.Column("provider", sa.String(length=128)),
        sa.Column("citation_mode", sa.String(length=32), nullable=False, server_default="hidden"),
        sa.Column("visible_citations", JSON, nullable=False, server_default="[]"),
        sa.Column("internal_evidence", JSON, nullable=False, server_default="[]"),
        sa.Column("safety_report", JSON, nullable=False, server_default="{}"),
        sa.Column("latency_ms", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("usage", JSON, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["chat_sessions.id"]),
    )
    op.create_index("ix_chat_messages_session_id", "chat_messages", ["session_id"])
    op.create_index("ix_chat_messages_role", "chat_messages", ["role"])

    op.create_table(
        "chat_retrieval_traces",
        uuid_col(primary_key=True),
        uuid_col("message_id", nullable=False),
        sa.Column("query", sa.Text(), nullable=False),
        sa.Column("retrieved_chunks", JSON, nullable=False, server_default="[]"),
        sa.Column("canonical_evidence", JSON, nullable=False, server_default="[]"),
        sa.Column("claim_checks", JSON, nullable=False, server_default="[]"),
        sa.Column("trace_report", JSON, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["message_id"], ["chat_messages.id"]),
    )
    op.create_index("ix_chat_retrieval_traces_message_id", "chat_retrieval_traces", ["message_id"])

    op.create_table(
        "chat_feedback",
        uuid_col(primary_key=True),
        uuid_col("message_id", nullable=False),
        uuid_col("user_id"),
        sa.Column("rating", sa.String(length=32), nullable=False, server_default="neutral"),
        sa.Column("reason", sa.Text()),
        sa.Column("correction", sa.Text()),
        sa.Column("feedback_metadata", JSON, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["message_id"], ["chat_messages.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["app_users.id"]),
    )
    op.create_index("ix_chat_feedback_message_id", "chat_feedback", ["message_id"])
    op.create_index("ix_chat_feedback_user_id", "chat_feedback", ["user_id"])
    op.create_index("ix_chat_feedback_rating", "chat_feedback", ["rating"])

    op.create_table(
        "model_usage_logs",
        uuid_col(primary_key=True),
        sa.Column("provider", sa.String(length=128), nullable=False),
        sa.Column("model_name", sa.String(length=256), nullable=False),
        sa.Column("feature", sa.String(length=128), nullable=False),
        uuid_col("user_id"),
        uuid_col("session_id"),
        sa.Column("input_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("output_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("estimated_cost", sa.Float(), nullable=False, server_default="0"),
        sa.Column("currency", sa.String(length=16), nullable=False, server_default="USD"),
        sa.Column("latency_ms", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=64), nullable=False, server_default="COMPLETED"),
        sa.Column("usage_metadata", JSON, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["app_users.id"]),
        sa.ForeignKeyConstraint(["session_id"], ["chat_sessions.id"]),
    )
    op.create_index("ix_model_usage_logs_provider", "model_usage_logs", ["provider"])
    op.create_index("ix_model_usage_logs_model_name", "model_usage_logs", ["model_name"])
    op.create_index("ix_model_usage_logs_feature", "model_usage_logs", ["feature"])

    op.create_table(
        "publishing_channels",
        uuid_col(primary_key=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("channel_type", sa.String(length=64), nullable=False, server_default="manual_export"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("config", JSON, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("name", name="uq_publishing_channels_name"),
    )
    op.create_index("ix_publishing_channels_name", "publishing_channels", ["name"])

    op.create_table(
        "content_publications",
        uuid_col(primary_key=True),
        uuid_col("content_item_id"),
        uuid_col("channel_id"),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=64), nullable=False, server_default="DRAFT"),
        sa.Column("scheduled_at", sa.DateTime(timezone=True)),
        sa.Column("published_at", sa.DateTime(timezone=True)),
        sa.Column("public_slug", sa.String(length=256)),
        sa.Column("export_uri", sa.String(length=1024)),
        sa.Column("publication_metadata", JSON, nullable=False, server_default="{}"),
        *timestamps(),
        sa.ForeignKeyConstraint(["content_item_id"], ["content_items.id"]),
        sa.ForeignKeyConstraint(["channel_id"], ["publishing_channels.id"]),
    )
    op.create_index("ix_content_publications_content_item_id", "content_publications", ["content_item_id"])
    op.create_index("ix_content_publications_channel_id", "content_publications", ["channel_id"])
    op.create_index("ix_content_publications_status", "content_publications", ["status"])
    op.create_index("ix_content_publications_public_slug", "content_publications", ["public_slug"])

    op.create_table(
        "product_events",
        uuid_col(primary_key=True),
        sa.Column("event_type", sa.String(length=128), nullable=False),
        uuid_col("actor_id"),
        sa.Column("object_type", sa.String(length=128)),
        sa.Column("object_id", sa.String(length=128)),
        sa.Column("event_metadata", JSON, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["actor_id"], ["app_users.id"]),
    )
    op.create_index("ix_product_events_event_type", "product_events", ["event_type"])
    op.create_index("ix_product_events_actor_id", "product_events", ["actor_id"])
    op.create_index("ix_product_events_object_type", "product_events", ["object_type"])
    op.create_index("ix_product_events_object_id", "product_events", ["object_id"])

    op.create_table(
        "acquisition_jobs",
        uuid_col(primary_key=True),
        sa.Column("source_uri", sa.String(length=2048), nullable=False),
        sa.Column("mode", sa.String(length=64), nullable=False, server_default="wide_discovery"),
        sa.Column("status", sa.String(length=64), nullable=False, server_default="QUEUED"),
        sa.Column("zone", sa.String(length=64), nullable=False, server_default="Z1_QUARANTINE"),
        sa.Column("discovered_title", sa.String(length=512)),
        sa.Column("quality_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("rights_signal", sa.String(length=64), nullable=False, server_default="UNKNOWN"),
        sa.Column("canonical_candidate", JSON, nullable=False, server_default="{}"),
        sa.Column("report", JSON, nullable=False, server_default="{}"),
        *timestamps(),
    )
    op.create_index("ix_acquisition_jobs_source_uri", "acquisition_jobs", ["source_uri"])
    op.create_index("ix_acquisition_jobs_status", "acquisition_jobs", ["status"])
    op.create_index("ix_acquisition_jobs_zone", "acquisition_jobs", ["zone"])

    op.create_table(
        "billing_ledger_entries",
        uuid_col(primary_key=True),
        uuid_col("user_id"),
        sa.Column("ledger_type", sa.String(length=64), nullable=False, server_default="model_usage"),
        sa.Column("amount", sa.Float(), nullable=False, server_default="0"),
        sa.Column("currency", sa.String(length=16), nullable=False, server_default="USD"),
        sa.Column("status", sa.String(length=64), nullable=False, server_default="RECORDED"),
        sa.Column("reference_type", sa.String(length=128)),
        sa.Column("reference_id", sa.String(length=128)),
        sa.Column("ledger_metadata", JSON, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["app_users.id"]),
    )
    op.create_index("ix_billing_ledger_entries_user_id", "billing_ledger_entries", ["user_id"])
    op.create_index("ix_billing_ledger_entries_ledger_type", "billing_ledger_entries", ["ledger_type"])
    op.create_index("ix_billing_ledger_entries_status", "billing_ledger_entries", ["status"])


def downgrade() -> None:
    for table in [
        "billing_ledger_entries",
        "acquisition_jobs",
        "product_events",
        "content_publications",
        "publishing_channels",
        "model_usage_logs",
        "chat_feedback",
        "chat_retrieval_traces",
        "chat_messages",
        "chat_sessions",
        "app_users",
    ]:
        op.drop_table(table)
