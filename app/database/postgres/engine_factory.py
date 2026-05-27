from typing import Any


def create_postgres_engine(dsn: str, pool_size: int = 5) -> Any:
    try:
        from sqlalchemy.ext.asyncio import create_async_engine
    except ImportError as exc:
        raise RuntimeError("Install sqlalchemy and asyncpg to enable PostgreSQL adapters") from exc
    return create_async_engine(dsn, pool_size=pool_size, pool_pre_ping=True)

