"""FastAPI dependency wiring for ConnLab."""

from __future__ import annotations

from collections.abc import Generator
from functools import lru_cache

from fastapi import Depends
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from backend.application.exception_workflow_service import ExceptionWorkflowService
from backend.application.evidence_placement_service import EvidencePlacementService
from backend.application.folder_service import FolderService
from backend.application.intake_precheck_service import IntakePrecheckService
from backend.application.ltr_local_commit_service import LtrLocalCommitService
from backend.application.ltr_renumber_preview_service import LtrRenumberPreviewService
from backend.application.ltr_registration_preview_service import (
    LtrRegistrationPreviewService,
)
from backend.application.ltr_readiness_service import LtrReadinessService
from backend.application.ltr_service import LtrService
from backend.application.lookup_service import LookupService
from backend.application.project_lifecycle_service import ProjectLifecycleService
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
from backend.infrastructure.storage.repositories.intake_package import (
    IntakeAssetRepository,
    IntakeCaseRepository,
    IntakeDraftRepository,
    IntakePackageRepository,
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


def get_exception_workflow_service(
    session: Session = Depends(get_session),
) -> ExceptionWorkflowService:
    """Build an exception workflow service for API routes."""
    return ExceptionWorkflowService(
        package_store=IntakePackageRepository(session),
        asset_store=IntakeAssetRepository(session),
        case_store=IntakeCaseRepository(session),
        draft_store=IntakeDraftRepository(session),
    )


def get_ltr_service(session: Session = Depends(get_session)) -> LtrService:
    """Build an LTR service for API routes."""
    project_repository = ProjectRepository(session)
    return LtrService(
        project_repository=project_repository,
        ltr_repository=LtrRecordRepository(session),
        lifecycle_guard=ProjectLifecycleService(project_repository),
    )


def get_lookup_service(session: Session = Depends(get_session)) -> LookupService:
    """Build a read-only lookup service for API routes."""
    return LookupService(
        project_repository=ProjectRepository(session),
        form_repository=ApplicationFormRepository(session),
        sample_repository=SampleInfoRepository(session),
        ltr_repository=LtrRecordRepository(session),
        file_asset_repository=FileAssetRepository(session),
    )


def get_ltr_readiness_service(
    session: Session = Depends(get_session),
) -> LtrReadinessService:
    """Build an LTR readiness service for API routes."""
    return LtrReadinessService(
        project_repository=ProjectRepository(session),
        form_repository=ApplicationFormRepository(session),
        sample_repository=SampleInfoRepository(session),
        file_asset_repository=FileAssetRepository(session),
    )


def get_ltr_registration_preview_service(
    session: Session = Depends(get_session),
) -> LtrRegistrationPreviewService:
    """Build an LTR registration preview service for API routes."""
    project_repository = ProjectRepository(session)
    readiness_service = LtrReadinessService(
        project_repository=project_repository,
        form_repository=ApplicationFormRepository(session),
        sample_repository=SampleInfoRepository(session),
        file_asset_repository=FileAssetRepository(session),
    )
    return LtrRegistrationPreviewService(
        ltr_repository=LtrRecordRepository(session),
        readiness_service=readiness_service,
        lifecycle_guard=ProjectLifecycleService(project_repository),
    )


def get_ltr_local_commit_service(
    session: Session = Depends(get_session),
) -> LtrLocalCommitService:
    """Build an LTR local commit service for API routes."""
    project_repository = ProjectRepository(session)
    readiness_service = LtrReadinessService(
        project_repository=project_repository,
        form_repository=ApplicationFormRepository(session),
        sample_repository=SampleInfoRepository(session),
        file_asset_repository=FileAssetRepository(session),
    )
    ltr_repository = LtrRecordRepository(session)
    lifecycle_guard = ProjectLifecycleService(project_repository)
    preview_service = LtrRegistrationPreviewService(
        ltr_repository=ltr_repository,
        readiness_service=readiness_service,
        lifecycle_guard=lifecycle_guard,
    )
    return LtrLocalCommitService(
        preview_service=preview_service,
        ltr_service=LtrService(
            project_repository=project_repository,
            ltr_repository=ltr_repository,
            lifecycle_guard=lifecycle_guard,
        ),
    )


def get_ltr_renumber_preview_service(
    session: Session = Depends(get_session),
) -> LtrRenumberPreviewService:
    """Build an LTR renumber preview service for API routes."""
    return LtrRenumberPreviewService(
        project_repository=ProjectRepository(session),
        ltr_repository=LtrRecordRepository(session),
        folder_repository=ProjectFolderRecordRepository(session),
        file_asset_repository=FileAssetRepository(session),
    )


def get_folder_service(session: Session = Depends(get_session)) -> FolderService:
    """Build a folder service for API routes."""
    project_repository = ProjectRepository(session)
    return FolderService(
        project_repository=project_repository,
        folder_repository=ProjectFolderRecordRepository(session),
        file_asset_repository=FileAssetRepository(session),
        lifecycle_guard=ProjectLifecycleService(project_repository),
    )


def get_evidence_placement_service(
    session: Session = Depends(get_session),
) -> EvidencePlacementService:
    """Build an evidence placement service for API routes."""
    project_repository = ProjectRepository(session)
    return EvidencePlacementService(
        project_repository=project_repository,
        folder_repository=ProjectFolderRecordRepository(session),
        file_asset_repository=FileAssetRepository(session),
        lifecycle_guard=ProjectLifecycleService(project_repository),
    )
