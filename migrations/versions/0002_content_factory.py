"""content factory v0.4 tables

Revision ID: 0002_content_factory
Revises: 0001_initial_schema
Create Date: 2026-05-28 00:00:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002_content_factory"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "content_templates",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False, unique=True),
        sa.Column("content_type", sa.String(64), nullable=False),
        sa.Column("language", sa.String(32), nullable=False, server_default="hi"),
        sa.Column("prompt_template", sa.Text, nullable=False),
        sa.Column("output_schema", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("version", sa.String(32), nullable=False, server_default="0.4.0"),
        sa.Column("active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_content_templates_content_type", "content_templates", ["content_type"])
    op.create_table(
        "content_batches",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("content_type", sa.String(64), nullable=False),
        sa.Column("topic", sa.String(512), nullable=False),
        sa.Column("language", sa.String(32), nullable=False, server_default="hi"),
        sa.Column("difficulty", sa.String(32), nullable=False, server_default="intermediate"),
        sa.Column("quantity", sa.Integer, nullable=False, server_default="5"),
        sa.Column("template_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("content_templates.id")),
        sa.Column("status", sa.String(64), nullable=False, server_default="DRAFT"),
        sa.Column("generation_config", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("metrics", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("created_by", postgresql.UUID(as_uuid=False)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_content_batches_content_type", "content_batches", ["content_type"])
    op.create_index("ix_content_batches_status", "content_batches", ["status"])
    is_sqlite = op.get_bind().dialect.name == "sqlite"
    op.add_column(
        "content_items",
        sa.Column("batch_id", postgresql.UUID(as_uuid=False) if not is_sqlite else sa.String(36), *([] if is_sqlite else [sa.ForeignKey("content_batches.id")])),
    )
    op.add_column(
        "content_items",
        sa.Column("template_id", postgresql.UUID(as_uuid=False) if not is_sqlite else sa.String(36), *([] if is_sqlite else [sa.ForeignKey("content_templates.id")])),
    )
    op.add_column("content_items", sa.Column("item_index", sa.Integer, nullable=False, server_default="0"))
    op.add_column("content_items", sa.Column("title", sa.String(512)))
    op.add_column("content_items", sa.Column("export_status", sa.String(64), nullable=False, server_default="NOT_EXPORTED"))
    op.add_column("content_items", sa.Column("version", sa.Integer, nullable=False, server_default="1"))
    op.add_column("content_items", sa.Column("provenance", postgresql.JSONB, nullable=False, server_default="{}"))
    op.add_column("content_items", sa.Column("updated_at", sa.DateTime(timezone=True)))
    op.create_index("ix_content_items_batch_id", "content_items", ["batch_id"])
    op.create_index("ix_content_items_review_status", "content_items", ["review_status"])
    op.create_table(
        "content_review_events",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("item_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("content_items.id"), nullable=False),
        sa.Column("reviewer_id", postgresql.UUID(as_uuid=False)),
        sa.Column("decision", sa.String(64), nullable=False),
        sa.Column("reason", sa.Text),
        sa.Column("checklist", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_content_review_events_item_id", "content_review_events", ["item_id"])
    op.create_table(
        "content_exports",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("batch_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("content_batches.id")),
        sa.Column("export_format", sa.String(32), nullable=False),
        sa.Column("file_path", sa.String(1024), nullable=False),
        sa.Column("item_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("manifest", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_content_exports_batch_id", "content_exports", ["batch_id"])


def downgrade() -> None:
    op.drop_index("ix_content_exports_batch_id", table_name="content_exports")
    op.drop_table("content_exports")
    op.drop_index("ix_content_review_events_item_id", table_name="content_review_events")
    op.drop_table("content_review_events")
    op.drop_index("ix_content_items_review_status", table_name="content_items")
    op.drop_index("ix_content_items_batch_id", table_name="content_items")
    for col in ["updated_at", "provenance", "version", "export_status", "title", "item_index", "template_id", "batch_id"]:
        op.drop_column("content_items", col)
    op.drop_index("ix_content_batches_status", table_name="content_batches")
    op.drop_index("ix_content_batches_content_type", table_name="content_batches")
    op.drop_table("content_batches")
    op.drop_index("ix_content_templates_content_type", table_name="content_templates")
    op.drop_table("content_templates")
