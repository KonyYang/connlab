"""FastAPI dependency wiring for ConnLab."""

from __future__ import annotations

from collections.abc import Generator
from functools import lru_cache

from fastapi import Depends
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from backend.application.project_service import ProjectService
from backend.infrastructure.storage.database import (
    create_database_engine,
    create_session_factory,
    init_db,
)
from backend.infrastructure.storage.repositories import ProjectRepository


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    """Return the application database engine."""
    engine = create_database_engine()
    init_db(engine)
    return engine


@lru_cache(maxsize=1)
def get_session_factory() -> sessionmaker[Session]:
    """Return the application session factory."""
    return create_session_factory(get_engine())


def get_session() -> Generator[Session, None, None]:
    """Yield a database session for one request."""
    with get_session_factory() as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise


def get_project_service(session: Session = Depends(get_session)) -> ProjectService:
    """Build a project service for API routes."""
    return ProjectService(ProjectRepository(session))
