"""Bounded dependency composition for live Matrix XLSX export."""

from backend.application.matrix_editor_live_xlsx_export_service import (
    MatrixEditorLiveXlsxExportService,
)
from backend.infrastructure.office.matrix_editor_live_xlsx_workbook_gateway import (
    MatrixEditorLiveXlsxWorkbookGateway,
)


def get_matrix_editor_live_xlsx_export_service() -> MatrixEditorLiveXlsxExportService:
    """Create the stateless in-memory export service."""
    return MatrixEditorLiveXlsxExportService(MatrixEditorLiveXlsxWorkbookGateway())
