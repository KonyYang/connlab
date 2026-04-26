"""FastAPI dependency wiring for ConnLab."""

from __future__ import annotations

from collections.abc import Generator
from functools import lru_cache

from fastapi import Depends
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from backend.application.folder_service import FolderService
from backend.application.intake_precheck_service import IntakePrecheckService
from backend.application.ltr_service import LtrService
from backend.application.project_service import ProjectService
from backend.infrastructure.storage.database import (
    create_database_engine,
    create_session_factory,
    init_db,
)
from backend.infrastructure.storage.repositories import (
    ApplicationFormRepository,
    FileAssetRepository,
    LtrRecordRepository,
    PrecheckResultRepository,
    ProjectFolderRecordRepository,
    ProjectRepository,
    SampleInfoRepository,
)
from backend.shared.config import Settings


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
    with get_session_factory()() as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise


def get_project_service(session: Session = Depends(get_session)) -> ProjectService:
    """Build a project service for API routes."""
    return ProjectService(ProjectRepository(session))


def get_settings() -> Settings:
    """Return application settings."""
    return Settings.load()


def get_intake_precheck_service(
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> IntakePrecheckService:
    """Build an intake/precheck service for API routes."""
    return IntakePrecheckService(
        project_repository=ProjectRepository(session),
        form_repository=ApplicationFormRepository(session),
        sample_repository=SampleInfoRepository(session),
        file_asset_repository=FileAssetRepository(session),
        precheck_repository=PrecheckResultRepository(session),
        settings=settings,
    )


def get_ltr_service(session: Session = Depends(get_session)) -> LtrService:
    """Build an LTR service for API routes."""
    return LtrService(
        project_repository=ProjectRepository(session),
        ltr_repository=LtrRecordRepository(session),
    )


def get_folder_service(session: Session = Depends(get_session)) -> FolderService:
    """Build a folder service for API routes."""
    return FolderService(
        project_repository=ProjectRepository(session),
        folder_repository=ProjectFolderRecordRepository(session),
        file_asset_repository=FileAssetRepository(session),
    )
