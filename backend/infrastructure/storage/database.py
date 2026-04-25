"""SQLite database foundation for ConnLab."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from backend.shared.config import Settings


class Base(DeclarativeBase):
    """Base class for future SQLAlchemy ORM models."""


def build_sqlite_url(database_path: Path) -> str:
    """Build a SQLAlchemy SQLite URL from a filesystem path."""
    return f"sqlite:///{database_path.as_posix()}"


def create_database_engine(
    settings: Settings | None = None,
    **engine_options: Any,
) -> Engine:
    """Create a SQLAlchemy engine using the configured SQLite database path."""
    resolved_settings = settings or Settings.load()
    resolved_settings.database_path.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(
        build_sqlite_url(resolved_settings.database_path),
        future=True,
        **engine_options,
    )


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Create the application session factory for a SQLAlchemy engine."""
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def init_db(engine: Engine) -> None:
    """Create all registered SQLAlchemy tables for the supplied engine."""
    Base.metadata.create_all(bind=engine)
