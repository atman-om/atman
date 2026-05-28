"""Qwen training, ModelOps, serving, and production hardening v0.9/v1.0 tables

Revision ID: 0007_qwen_training_modelops_prod
Revises: 0006_web_to_corpus_ocr
Create Date: 2026-05-28 00:00:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0007_qwen_training_modelops_prod"
down_revision = "0006_web_to_corpus_ocr"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "training_datasets",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("name", sa.String(256), nullable=False, unique=True),
        sa.Column("base_model", sa.String(256), nullable=False),
        sa.Column("sample_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("artifact_uri", sa.String(1024), nullable=False),
        sa.Column("manifest", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("status", sa.String(64), nullable=False, server_default="BUILT"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_training_datasets_status", "training_datasets", ["status"])

    op.create_table(
        "training_runs",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("dataset_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("training_datasets.id")),
        sa.Column("base_model", sa.String(256), nullable=False),
        sa.Column("adapter_method", sa.String(64), nullable=False, server_default="qlora"),
        sa.Column("status", sa.String(64), nullable=False, server_default="PLANNED"),
        sa.Column("config", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("metrics", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("checkpoint_id", postgresql.UUID(as_uuid=False)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_training_runs_dataset_id", "training_runs", ["dataset_id"])
    op.create_index("ix_training_runs_status", "training_runs", ["status"])
    op.create_index("ix_training_runs_checkpoint_id", "training_runs", ["checkpoint_id"])

    op.create_table(
        "model_checkpoints",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("run_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("training_runs.id")),
        sa.Column("model_name", sa.String(256), nullable=False),
        sa.Column("base_model", sa.String(256), nullable=False),
        sa.Column("adapter_uri", sa.String(1024), nullable=False),
        sa.Column("checksum_sha256", sa.String(64)),
        sa.Column("eval_summary", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("release_status", sa.String(64), nullable=False, server_default="UNRELEASED"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_model_checkpoints_run_id", "model_checkpoints", ["run_id"])
    op.create_index("ix_model_checkpoints_release_status", "model_checkpoints", ["release_status"])

    op.create_table(
        "model_releases",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("checkpoint_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("model_checkpoints.id"), nullable=False),
        sa.Column("release_name", sa.String(256), nullable=False),
        sa.Column("environment", sa.String(64), nullable=False, server_default="staging"),
        sa.Column("allowed", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("gate_report", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("rollback_target", postgresql.UUID(as_uuid=False)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_model_releases_checkpoint_id", "model_releases", ["checkpoint_id"])

    op.create_table(
        "serving_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False, unique=True),
        sa.Column("model_name", sa.String(256), nullable=False),
        sa.Column("runtime_mode", sa.String(64), nullable=False, server_default="openai_compatible"),
        sa.Column("endpoint_url", sa.String(1024)),
        sa.Column("config", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("active", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "backup_runs",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("status", sa.String(64), nullable=False, server_default="SIMULATED"),
        sa.Column("backup_type", sa.String(64), nullable=False, server_default="metadata"),
        sa.Column("artifact_uri", sa.String(1024)),
        sa.Column("manifest", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "production_incidents",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("severity", sa.String(16), nullable=False, server_default="P3"),
        sa.Column("title", sa.String(256), nullable=False),
        sa.Column("status", sa.String(64), nullable=False, server_default="OPEN"),
        sa.Column("description", sa.Text),
        sa.Column("evidence", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_production_incidents_severity", "production_incidents", ["severity"])
    op.create_index("ix_production_incidents_status", "production_incidents", ["status"])


def downgrade() -> None:
    op.drop_table("production_incidents")
    op.drop_table("backup_runs")
    op.drop_table("serving_profiles")
    op.drop_table("model_releases")
    op.drop_table("model_checkpoints")
    op.drop_table("training_runs")
    op.drop_table("training_datasets")
