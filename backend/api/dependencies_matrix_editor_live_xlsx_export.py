"""Bounded dependency composition for live Matrix XLSX export."""

from fastapi import Depends
from sqlalchemy.orm import Session

from backend.api.dependencies import get_session
from backend.application.matrix_editor_live_xlsx_export_service import (
    MatrixEditorLiveXlsxExportService,
)
from backend.application.matrix_editor_live_xlsx_publication_service import (
    ConfirmedMatrixLiveXlsxAuthorityMatcher,
    MatrixEditorLiveXlsxPublicationService,
)
from backend.application.project_lifecycle_write_guard import ProjectLifecycleWriteGuard
from backend.infrastructure.files.test_record_publication_gateway import (
    TestRecordPublicationGateway,
)
from backend.infrastructure.office.matrix_editor_live_xlsx_workbook_gateway import (
    MatrixEditorLiveXlsxWorkbookGateway,
)
from backend.infrastructure.storage.repositories import ProjectRepository
from backend.infrastructure.storage.repositories.confirmed_matrix_authority import (
    ConfirmedMatrixAuthorityRepository,
)
from backend.infrastructure.storage.repositories.official_workspace import (
    ProjectOfficialWorkspaceRepository,
)


def get_matrix_editor_live_xlsx_export_service() -> MatrixEditorLiveXlsxExportService:
    """Create the stateless in-memory export service."""
    return MatrixEditorLiveXlsxExportService(MatrixEditorLiveXlsxWorkbookGateway())


def get_matrix_editor_live_xlsx_publication_service(
    session: Session = Depends(get_session),
) -> MatrixEditorLiveXlsxPublicationService:
    """Create authority-aware formal Matrix publication."""
    return MatrixEditorLiveXlsxPublicationService(
        workspace_store=ProjectOfficialWorkspaceRepository(session),
        authority_matcher=ConfirmedMatrixLiveXlsxAuthorityMatcher(
            ConfirmedMatrixAuthorityRepository(session)
        ),
        export_service=get_matrix_editor_live_xlsx_export_service(),
        file_gateway=TestRecordPublicationGateway(resource_label="Matrix"),
        lifecycle_write_guard=ProjectLifecycleWriteGuard(ProjectRepository(session)),
    )
