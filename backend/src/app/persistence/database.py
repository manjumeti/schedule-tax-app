"""Async SQLAlchemy 2.x engine/session setup.

Uses SQLite (aiosqlite) for local development/tests and PostgreSQL (asyncpg)
in staging/production, selected purely via `DATABASE_URL`.
"""
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import Settings, get_settings


class Database:
    """Owns the engine + sessionmaker lifecycle for the application."""

    def __init__(self, settings: Settings) -> None:
        connect_args = (
            {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
        )
        self.engine: AsyncEngine = create_async_engine(
            settings.database_url,
            echo=settings.database_echo,
            connect_args=connect_args,
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine, expire_on_commit=False, autoflush=False
        )

    async def create_all(self) -> None:
        from app.persistence.models import Base

        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def dispose(self) -> None:
        await self.engine.dispose()

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        async with self.session_factory() as session:
            yield session


_db: Database | None = None


def get_database() -> Database:
    global _db
    if _db is None:
        _db = Database(get_settings())
    return _db


async def get_db_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency yielding a request-scoped `AsyncSession`."""
    async with get_database().session() as session:
        yield session
