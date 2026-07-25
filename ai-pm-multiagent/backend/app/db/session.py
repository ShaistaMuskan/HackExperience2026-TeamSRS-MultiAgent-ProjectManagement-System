"""
Async SQLAlchemy engine/session factory for the production schema (models.py).
Not used by the hackathon MVP runtime (see repository.py) - provided so the
post-hackathon migration path is a copy-paste away.

pip install sqlalchemy[asyncio] asyncpg   (Postgres)   or   aiosqlite (local/dev)
"""
from __future__ import annotations
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.config import get_settings


def build_session_factory() -> async_sessionmaker[AsyncSession]:
    settings = get_settings()
    engine = create_async_engine(settings.database_url, echo=False)
    return async_sessionmaker(engine, expire_on_commit=False)
