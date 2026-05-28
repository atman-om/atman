from services.api.app.core.config import Settings


def test_neon_url_is_normalized_for_asyncpg() -> None:
    settings = Settings(
        database_url=(
            "postgresql://user:pass@ep-example-pooler.ap-southeast-1.aws.neon.tech/neondb"
            "?sslmode=require&channel_binding=require"
        )
    )

    assert settings.sqlalchemy_database_url == (
        "postgresql+asyncpg://user:pass@ep-example-pooler.ap-southeast-1.aws.neon.tech/neondb"
    )
    assert settings.database_connect_args == {"ssl": True}


def test_neon_url_is_normalized_for_sync_migrations() -> None:
    settings = Settings(
        database_url=(
            "postgresql://user:pass@ep-example-pooler.ap-southeast-1.aws.neon.tech/neondb"
            "?sslmode=require&channel_binding=require"
        )
    )

    assert settings.sqlalchemy_sync_database_url == (
        "postgresql+psycopg://user:pass@ep-example-pooler.ap-southeast-1.aws.neon.tech/neondb"
        "?sslmode=require&channel_binding=require"
    )
