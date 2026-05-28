from __future__ import annotations
from logging.config import fileConfig

from alembic.ddl.impl import DefaultImpl
from alembic import context
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.compiler import compiles
from sqlalchemy import Column, MetaData, PrimaryKeyConstraint, String, Table, engine_from_config, inspect, pool, text

from services.api.app.core.config import get_settings
from services.api.app.core.db import Base
from services.api.app import models  # noqa: F401

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _version_table_impl(
    self,
    *,
    version_table: str,
    version_table_schema: str | None,
    version_table_pk: bool,
    **kw,
) -> Table:
    table = Table(
        version_table,
        MetaData(),
        Column("version_num", String(255), nullable=False),
        schema=version_table_schema,
    )
    if version_table_pk:
        table.append_constraint(PrimaryKeyConstraint("version_num", name=f"{version_table}_pkc"))
    return table


DefaultImpl.version_table_impl = _version_table_impl


@compiles(JSONB, "sqlite")
def _compile_jsonb_sqlite(element, compiler, **kw) -> str:
    return "JSON"


@compiles(UUID, "sqlite")
def _compile_uuid_sqlite(element, compiler, **kw) -> str:
    return "VARCHAR(36)"


def get_url() -> str:
    return get_settings().sqlalchemy_sync_database_url


def run_migrations_offline() -> None:
    context.configure(url=get_url(), target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(configuration, prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.begin() as connection:
        if connection.dialect.name == "postgresql" and inspect(connection).has_table("alembic_version"):
            connection.execute(text("ALTER TABLE alembic_version ALTER COLUMN version_num TYPE VARCHAR(255)"))
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
