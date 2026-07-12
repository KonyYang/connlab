"""No-write draft workbook preview from the current editable plan revision."""

from __future__ import annotations

from collections.abc import Callable

from backend.application.draft_measurement_plan_workbook_projection import (
    DraftMeasurementPlanWorkbookProjection,
    build_draft_measurement_plan_workbook_projection,
)


class DraftMeasurementPlanWorkbookPreviewError(ValueError):
    """Raised when a requested revision is not the current editable source."""


class DraftMeasurementPlanWorkbookPreviewService:
    """Build draft output only from the current persisted editable workspace."""

    def __init__(self, workspace_reader: Callable[[str], dict[str, object]]) -> None:
        self._workspace_reader = workspace_reader

    def preview(self, project_id: str, revision_id: str) -> DraftMeasurementPlanWorkbookProjection:
        workspace = self._workspace_reader(project_id)
        if workspace.get("editable_revision_id") != revision_id:
            raise DraftMeasurementPlanWorkbookPreviewError(
                "Editable measurement plan changed. Reload before previewing."
            )
        return build_draft_measurement_plan_workbook_projection(workspace)
