from collections.abc import Mapping
from typing import Any, Protocol


class AsyncSqlRunner(Protocol):
    async def execute(self, statement: str, parameters: Mapping[str, Any] | None = None) -> Any:
        raise NotImplementedError


class SqlExecutionError(RuntimeError):
    pass


class PostgresSqlRunner:
    def __init__(self, engine: Any | None) -> None:
        self._engine = engine

    async def execute(self, statement: str, parameters: Mapping[str, Any] | None = None) -> Any:
        if self._engine is None:
            raise SqlExecutionError("PostgreSQL engine is not configured")
        if hasattr(self._engine, "execute"):
            return await self._engine.execute(statement, parameters or {})
        statement_obj = self._statement(statement)
        async with self._engine.begin() as connection:
            return await connection.execute(statement_obj, parameters or {})

    def _statement(self, statement: str) -> Any:
        try:
            from sqlalchemy import text
        except ImportError as exc:
            raise SqlExecutionError("SQLAlchemy is required for engine-backed execution") from exc
        return text(statement)
