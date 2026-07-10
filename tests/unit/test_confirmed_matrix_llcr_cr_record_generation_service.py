from __future__ import annotations

from pathlib import Path

import pytest

from backend.application.confirmed_matrix_llcr_cr_record_generation_service import (
    GenerateLlcrCrRecordWorkbookCommand,
    LlcrCrRecordWorkbookGenerationError,
    LlcrCrRecordWorkbookGenerationService,
)
from backend.application.confirmed_matrix_llcr_cr_record_preview_service import (
    LlcrCrRecordWorkbookPreviewService,
)
from backend.domain import (
    ConfirmedMatrixGroup,
    ConfirmedMatrixRow,
    ConfirmedMatrixSnapshot,
    ConfirmedMatrixStatus,
    ConfirmedMatrixStepQuantity,
    ConfirmedMatrixVersion,
    MatrixStepContactFamily,
    MatrixStepContactPlan,
)
from backend.infrastructure.files.llcr_cr_specialized_record_artifact_store import (
    LlcrCrSpecializedRecordArtifactStore,
)
from backend.infrastructure.office.llcr_cr_specialized_record_workbook_gateway import (
    LlcrCrSpecializedRecordWorkbookGateway,
)


def test_generation_writes_managed_xlsx_only_after_matching_preview_fingerprint(tmp_path: Path) -> None:
    service = _service(tmp_path)
    preview = service._preview_service.preview("project-1")

    result = service.generate(
        GenerateLlcrCrRecordWorkbookCommand(
            project_id="project-1", preview_fingerprint=preview.preview_fingerprint or ""
        )
    )

    assert result.file_name.endswith(".xlsx")
    assert result.output_path.is_file()
    assert result.output_path.parent == tmp_path / "generated_llcr_cr_record_files" / "project-1"


def test_generation_rejects_stale_fingerprint_without_writing(tmp_path: Path) -> None:
    service = _service(tmp_path)

    with pytest.raises(LlcrCrRecordWorkbookGenerationError, match="changed"):
        service.generate(
            GenerateLlcrCrRecordWorkbookCommand(
                project_id="project-1", preview_fingerprint="stale"
            )
        )

    assert not list(tmp_path.rglob("*.xlsx"))


def _service(tmp_path: Path) -> LlcrCrRecordWorkbookGenerationService:
    preview_service = LlcrCrRecordWorkbookPreviewService(
        confirmed_store=_ConfirmedStore(_snapshot())
    )
    return LlcrCrRecordWorkbookGenerationService(
        preview_service=preview_service,
        workbook_gateway=LlcrCrSpecializedRecordWorkbookGateway(),
        artifact_store=LlcrCrSpecializedRecordArtifactStore(
            tmp_path / "generated_llcr_cr_record_files"
        ),
    )


class _ConfirmedStore:
    def __init__(self, snapshot: ConfirmedMatrixSnapshot) -> None:
        self._snapshot = snapshot

    def get_active_by_project(self, project_id: str) -> ConfirmedMatrixSnapshot | None:
        return self._snapshot if project_id == self._snapshot.version.project_id else None


def _snapshot() -> ConfirmedMatrixSnapshot:
    version = ConfirmedMatrixVersion(
        confirmed_matrix_id="cmv-1",
        project_id="project-1",
        project_matrix_draft_id="draft-1",
        source_import_id="import-1",
        source_snapshot_id="source-1",
        confirmed_revision=4,
        is_active_authority=True,
        status=ConfirmedMatrixStatus.CONFIRMED,
        confirmed_by="operator",
        confirmed_at="2026-07-10T10:00:00+00:00",
    )
    group = ConfirmedMatrixGroup(
        confirmed_group_id="group-1",
        confirmed_matrix_id="cmv-1",
        draft_group_id="draft-group-1",
        source_group_snapshot_id=None,
        group_order=1,
        group_key="G1",
        group_label="Group 1",
        sample_quantity_expression="1",
    )
    row = ConfirmedMatrixRow(
        confirmed_row_id="row-1",
        confirmed_matrix_id="cmv-1",
        draft_row_id="draft-row-1",
        source_row_snapshot_id=None,
        row_order=1,
        test_item="LLCR",
    )
    plan = MatrixStepContactPlan(
        contact_kind="llcr",
        coverage_status="eligible",
        included=True,
        exclusion_reason=None,
        is_override=False,
        readings_per_sample="1",
        families=(
            MatrixStepContactFamily(
                family_id="signal",
                family_label="Signal",
                count_per_sample="1",
                record_label="Signal contact",
                record_prefix="SIG",
                included=True,
                is_custom=False,
            ),
        ),
    )
    quantity = ConfirmedMatrixStepQuantity(
        confirmed_step_quantity_id="quantity-1",
        confirmed_matrix_id="cmv-1",
        confirmed_group_id="group-1",
        confirmed_row_id="row-1",
        draft_group_id="draft-group-1",
        draft_row_id="draft-row-1",
        step_sequence=2,
        step_suffix_note=None,
        raw_token="2",
        test_points_per_sample=None,
        readings_per_point=None,
        contact_points_per_sample=None,
        source="matrix_contact_plan",
        review_required=False,
        review_reason=None,
        confirmed_at=version.confirmed_at,
        contact_plan=plan,
    )
    return ConfirmedMatrixSnapshot(
        version=version,
        groups=(group,),
        rows=(row,),
        step_quantities=(quantity,),
    )
