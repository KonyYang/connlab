from __future__ import annotations

import pytest

from backend.application.confirmed_matrix_test_record_preview_service import (
    BuildConfirmedMatrixTestRecordPreviewCommand,
    ConfirmedMatrixTestRecordPreviewError,
    ConfirmedMatrixTestRecordPreviewNotFoundError,
    ConfirmedMatrixTestRecordPreviewService,
)
from backend.domain import (
    ConfirmedMatrixCell,
    ConfirmedMatrixGroup,
    ConfirmedMatrixRow,
    ConfirmedMatrixSnapshot,
    ConfirmedMatrixStatus,
    ConfirmedMatrixVersion,
)


def test_confirmed_matrix_test_record_preview_happy_path_preserves_group_row_token_order() -> None:
    service = ConfirmedMatrixTestRecordPreviewService(confirmed_store=_ConfirmedStore(active=_snapshot()))

    preview = service.build_preview(BuildConfirmedMatrixTestRecordPreviewCommand(project_id="P1"))

    assert preview.project_id == "P1"
    assert preview.confirmed_matrix_id == "cmv-1"
    assert preview.preview_status == "ready"
    assert [group.group_key for group in preview.groups] == ["g1", "g2"]
    assert preview.groups[0].sample_quantity_expression == "5"
    assert [step.raw_token for step in preview.groups[0].steps] == ["1", "2", "5"]
    assert preview.groups[0].steps[0].section == "6.1"
    assert preview.groups[0].steps[0].method == "M1"


def test_confirmed_matrix_test_record_preview_not_found() -> None:
    service = ConfirmedMatrixTestRecordPreviewService(confirmed_store=_ConfirmedStore(active=None))
    with pytest.raises(ConfirmedMatrixTestRecordPreviewNotFoundError, match="not found"):
        service.build_preview(BuildConfirmedMatrixTestRecordPreviewCommand(project_id="P1"))


def test_confirmed_matrix_test_record_preview_empty_when_active_authority_has_no_steps() -> None:
    service = ConfirmedMatrixTestRecordPreviewService(
        confirmed_store=_ConfirmedStore(
            active=_snapshot(
                cells=(
                    ConfirmedMatrixCell(
                        confirmed_cell_id="cmc-1",
                        confirmed_matrix_id="cmv-1",
                        confirmed_row_id="cmr-1",
                        confirmed_group_id="cmg-1",
                        draft_row_id="pmdr-1",
                        draft_group_id="pmdg-1",
                        cell_value="A",
                    ),
                )
            )
        )
    )

    preview = service.build_preview(BuildConfirmedMatrixTestRecordPreviewCommand(project_id="P1"))
    assert preview.preview_status == "empty"
    assert preview.groups == ()


def test_confirmed_matrix_test_record_preview_uses_numeric_raw_token_for_suffixed_steps() -> None:
    service = ConfirmedMatrixTestRecordPreviewService(
        confirmed_store=_ConfirmedStore(
            active=_snapshot(
                cells=(
                    ConfirmedMatrixCell(
                        confirmed_cell_id="cmc-1",
                        confirmed_matrix_id="cmv-1",
                        confirmed_row_id="cmr-1",
                        confirmed_group_id="cmg-1",
                        draft_row_id="pmdr-1",
                        draft_group_id="pmdg-1",
                        cell_value="3(a)",
                    ),
                )
            )
        )
    )

    preview = service.build_preview(BuildConfirmedMatrixTestRecordPreviewCommand(project_id="P1"))

    step = preview.groups[0].steps[0]
    assert step.raw_token == "3"
    assert step.sequence == 3


def test_confirmed_matrix_test_record_preview_uses_empty_strings_for_missing_fields() -> None:
    service = ConfirmedMatrixTestRecordPreviewService(
        confirmed_store=_ConfirmedStore(
            active=_snapshot(
                rows=(
                    ConfirmedMatrixRow(
                        confirmed_row_id="cmr-1",
                        confirmed_matrix_id="cmv-1",
                        draft_row_id="pmdr-1",
                        source_row_snapshot_id="smr-1",
                        row_order=1,
                        test_item=" Visual ",
                        source_section=None,
                        method=None,
                        condition=" ",
                        requirement=None,
                    ),
                ),
                cells=(
                    ConfirmedMatrixCell(
                        confirmed_cell_id="cmc-1",
                        confirmed_matrix_id="cmv-1",
                        confirmed_row_id="cmr-1",
                        confirmed_group_id="cmg-1",
                        draft_row_id="pmdr-1",
                        draft_group_id="pmdg-1",
                        cell_value="1",
                    ),
                ),
            )
        )
    )

    preview = service.build_preview(BuildConfirmedMatrixTestRecordPreviewCommand(project_id="P1"))
    step = preview.groups[0].steps[0]
    assert step.test_item == "Visual"
    assert step.section == ""
    assert step.method == ""
    assert step.condition == ""
    assert step.requirement == ""


def test_confirmed_matrix_test_record_preview_rejects_invalid_cell_lineage() -> None:
    service = ConfirmedMatrixTestRecordPreviewService(
        confirmed_store=_ConfirmedStore(
            active=_snapshot(
                cells=(
                    ConfirmedMatrixCell(
                        confirmed_cell_id="cmc-1",
                        confirmed_matrix_id="cmv-1",
                        confirmed_row_id="missing-row",
                        confirmed_group_id="cmg-1",
                        draft_row_id="pmdr-1",
                        draft_group_id="pmdg-1",
                        cell_value="1",
                    ),
                )
            )
        )
    )

    with pytest.raises(ConfirmedMatrixTestRecordPreviewError, match="lineage is invalid"):
        service.build_preview(BuildConfirmedMatrixTestRecordPreviewCommand(project_id="P1"))


def test_preview_maps_llcr_multistep_requirement_with_sorted_step_order() -> None:
    service = ConfirmedMatrixTestRecordPreviewService(
        confirmed_store=_ConfirmedStore(
            active=_snapshot(
                rows=(
                    ConfirmedMatrixRow(
                        confirmed_row_id="cmr-llcr",
                        confirmed_matrix_id="cmv-1",
                        draft_row_id="pmdr-llcr",
                        source_row_snapshot_id="smr-llcr",
                        row_order=1,
                        test_item="Contact Resistance (Low Level)",
                        source_section="6.2",
                        method="M2",
                        condition="C2",
                        requirement="Initial ≤ 0.25 mΩ; R≤ 0.17 mΩ",
                    ),
                ),
                cells=(
                    ConfirmedMatrixCell(
                        confirmed_cell_id="cmc-llcr",
                        confirmed_matrix_id="cmv-1",
                        confirmed_row_id="cmr-llcr",
                        confirmed_group_id="cmg-1",
                        draft_row_id="pmdr-llcr",
                        draft_group_id="pmdg-1",
                        cell_value="5,2",
                    ),
                ),
            )
        )
    )

    preview = service.build_preview(BuildConfirmedMatrixTestRecordPreviewCommand(project_id="P1"))
    steps = preview.groups[0].steps
    assert [step.raw_token for step in steps] == ["2", "5"]
    assert steps[0].requirement == "≤ 0.25 mΩ"
    assert steps[1].requirement == "ΔR ≤ 0.17 mΩ"


def test_preview_maps_llcr_initial_only_without_delta_for_followup_steps() -> None:
    service = ConfirmedMatrixTestRecordPreviewService(
        confirmed_store=_ConfirmedStore(
            active=_snapshot(
                rows=(
                    ConfirmedMatrixRow(
                        confirmed_row_id="cmr-llcr",
                        confirmed_matrix_id="cmv-1",
                        draft_row_id="pmdr-llcr",
                        source_row_snapshot_id="smr-llcr",
                        row_order=1,
                        test_item="LLCR",
                        source_section="6.2",
                        method="M2",
                        condition="C2",
                        requirement="Initial ≤ 25 mΩ",
                    ),
                ),
                cells=(
                    ConfirmedMatrixCell(
                        confirmed_cell_id="cmc-llcr",
                        confirmed_matrix_id="cmv-1",
                        confirmed_row_id="cmr-llcr",
                        confirmed_group_id="cmg-1",
                        draft_row_id="pmdr-llcr",
                        draft_group_id="pmdg-1",
                        cell_value="1,2",
                    ),
                ),
            )
        )
    )

    preview = service.build_preview(BuildConfirmedMatrixTestRecordPreviewCommand(project_id="P1"))
    steps = preview.groups[0].steps
    assert steps[0].requirement == "≤ 25 mΩ"
    assert steps[1].requirement == "Initial ≤ 25 mΩ"


class _ConfirmedStore:
    def __init__(self, active: ConfirmedMatrixSnapshot | None) -> None:
        self.active = active

    def get_active_by_project(self, project_id: str) -> ConfirmedMatrixSnapshot | None:
        if self.active and self.active.version.project_id == project_id:
            return self.active
        return None


def _snapshot(
    *,
    rows: tuple[ConfirmedMatrixRow, ...] | None = None,
    cells: tuple[ConfirmedMatrixCell, ...] | None = None,
) -> ConfirmedMatrixSnapshot:
    return ConfirmedMatrixSnapshot(
        version=ConfirmedMatrixVersion(
            confirmed_matrix_id="cmv-1",
            project_id="P1",
            project_matrix_draft_id="pmd-1",
            source_import_id="smi-1",
            source_snapshot_id="sms-1",
            confirmed_revision=1,
            is_active_authority=True,
            status=ConfirmedMatrixStatus.CONFIRMED,
            confirmed_by="operator",
            confirmed_at="2026-05-23T09:00:00+00:00",
        ),
        groups=(
            ConfirmedMatrixGroup(
                confirmed_group_id="cmg-1",
                confirmed_matrix_id="cmv-1",
                draft_group_id="pmdg-1",
                source_group_snapshot_id="smg-1",
                group_order=1,
                group_key="g1",
                group_label="1",
                sample_quantity_expression="5",
            ),
            ConfirmedMatrixGroup(
                confirmed_group_id="cmg-2",
                confirmed_matrix_id="cmv-1",
                draft_group_id="pmdg-2",
                source_group_snapshot_id="smg-2",
                group_order=2,
                group_key="g2",
                group_label="2",
                sample_quantity_expression="6",
            ),
        ),
        rows=rows
        if rows is not None
        else (
            ConfirmedMatrixRow(
                confirmed_row_id="cmr-1",
                confirmed_matrix_id="cmv-1",
                draft_row_id="pmdr-1",
                source_row_snapshot_id="smr-1",
                row_order=1,
                test_item="Visual",
                source_section="6.1",
                method="M1",
                condition="C1",
                requirement="R1",
            ),
            ConfirmedMatrixRow(
                confirmed_row_id="cmr-2",
                confirmed_matrix_id="cmv-1",
                draft_row_id="pmdr-2",
                source_row_snapshot_id="smr-2",
                row_order=2,
                test_item="LLCR",
                source_section="6.2",
                method="M2",
                condition="C2",
                requirement="R2",
            ),
        ),
        cells=cells
        if cells is not None
        else (
            ConfirmedMatrixCell(
                confirmed_cell_id="cmc-1",
                confirmed_matrix_id="cmv-1",
                confirmed_row_id="cmr-1",
                confirmed_group_id="cmg-1",
                draft_row_id="pmdr-1",
                draft_group_id="pmdg-1",
                cell_value="1,2(a)",
            ),
            ConfirmedMatrixCell(
                confirmed_cell_id="cmc-2",
                confirmed_matrix_id="cmv-1",
                confirmed_row_id="cmr-2",
                confirmed_group_id="cmg-1",
                draft_row_id="pmdr-2",
                draft_group_id="pmdg-1",
                cell_value="5",
            ),
            ConfirmedMatrixCell(
                confirmed_cell_id="cmc-3",
                confirmed_matrix_id="cmv-1",
                confirmed_row_id="cmr-1",
                confirmed_group_id="cmg-2",
                draft_row_id="pmdr-1",
                draft_group_id="pmdg-2",
                cell_value="3",
            ),
        ),
    )
