from __future__ import annotations

import pytest

from backend.application.confirmed_matrix_runtime_projection_service import (
    BuildConfirmedMatrixRuntimeProjectionCommand,
    ConfirmedMatrixRuntimeProjectionError,
    ConfirmedMatrixRuntimeProjectionNotFoundError,
    ConfirmedMatrixRuntimeProjectionService,
)
from backend.application.runtime_projection_read_only_service import (
    RuntimeProjectionReadOnlyService,
)
from backend.domain import (
    ConfirmedMatrixCell,
    ConfirmedMatrixGroup,
    ConfirmedMatrixRow,
    ConfirmedMatrixSnapshot,
    ConfirmedMatrixStatus,
    ConfirmedMatrixVersion,
)


def test_confirmed_matrix_runtime_projection_happy_path_and_selected_token() -> None:
    store = _ConfirmedStore(active=_snapshot())
    service = ConfirmedMatrixRuntimeProjectionService(
        confirmed_store=store,
        runtime_projection_service=RuntimeProjectionReadOnlyService(),
    )

    first = service.build_snapshot(
        BuildConfirmedMatrixRuntimeProjectionCommand(project_id="P1")
    )
    assert first.project_reference == "P1"
    assert first.matrix_reference == "cmv-1:r2"
    assert first.matrix_overview.group_count == 2
    assert first.parser_warnings == ()

    selected = first.matrix_overview.groups[0].tokens[0].token_reference
    second = service.build_snapshot(
        BuildConfirmedMatrixRuntimeProjectionCommand(
            project_id="P1",
            selected_token_reference=selected,
        )
    )
    assert second.step_workspace is not None
    assert second.step_workspace.found is True
    assert second.step_workspace.selected_token_reference == selected


def test_confirmed_matrix_runtime_projection_not_found() -> None:
    service = ConfirmedMatrixRuntimeProjectionService(
        confirmed_store=_ConfirmedStore(active=None),
        runtime_projection_service=RuntimeProjectionReadOnlyService(),
    )
    with pytest.raises(ConfirmedMatrixRuntimeProjectionNotFoundError, match="not found"):
        service.build_snapshot(
            BuildConfirmedMatrixRuntimeProjectionCommand(project_id="P1")
        )


def test_confirmed_matrix_runtime_projection_rejects_invalid_cell_lineage() -> None:
    invalid = _snapshot(
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
    service = ConfirmedMatrixRuntimeProjectionService(
        confirmed_store=_ConfirmedStore(active=invalid),
        runtime_projection_service=RuntimeProjectionReadOnlyService(),
    )
    with pytest.raises(ConfirmedMatrixRuntimeProjectionError, match="lineage is invalid"):
        service.build_snapshot(
            BuildConfirmedMatrixRuntimeProjectionCommand(project_id="P1")
        )


def test_confirmed_matrix_runtime_projection_sparse_mapping_omits_missing_cells() -> None:
    sparse = _snapshot(
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
        )
    )
    service = ConfirmedMatrixRuntimeProjectionService(
        confirmed_store=_ConfirmedStore(active=sparse),
        runtime_projection_service=RuntimeProjectionReadOnlyService(),
    )
    snapshot = service.build_snapshot(
        BuildConfirmedMatrixRuntimeProjectionCommand(project_id="P1")
    )
    assert snapshot.runtime_projection_summary.total_tokens == 1
    assert "Missing step token value." not in snapshot.parser_warnings


def test_confirmed_matrix_runtime_projection_splits_full_width_comma_tokens() -> None:
    service = ConfirmedMatrixRuntimeProjectionService(
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
                        cell_value="8，10",
                    ),
                )
            )
        ),
        runtime_projection_service=RuntimeProjectionReadOnlyService(),
    )

    snapshot = service.build_snapshot(
        BuildConfirmedMatrixRuntimeProjectionCommand(project_id="P1")
    )

    tokens = snapshot.matrix_overview.groups[0].tokens
    assert [token.raw_token for token in tokens] == ["8", "10"]
    assert [token.sequence_number for token in tokens] == [8, 10]


def test_confirmed_matrix_runtime_projection_uses_numeric_raw_token_for_suffixed_steps() -> None:
    service = ConfirmedMatrixRuntimeProjectionService(
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
        ),
        runtime_projection_service=RuntimeProjectionReadOnlyService(),
    )

    snapshot = service.build_snapshot(
        BuildConfirmedMatrixRuntimeProjectionCommand(project_id="P1")
    )

    token = snapshot.matrix_overview.groups[0].tokens[0]
    assert token.raw_token == "3"
    assert token.sequence_number == 3
    assert token.suffix_note == "(a)"


class _ConfirmedStore:
    def __init__(self, active: ConfirmedMatrixSnapshot | None) -> None:
        self.active = active

    def get_active_by_project(self, project_id: str) -> ConfirmedMatrixSnapshot | None:
        if self.active and self.active.version.project_id == project_id:
            return self.active
        return None


def _snapshot(
    *,
    cells: tuple[ConfirmedMatrixCell, ...] | None = None,
) -> ConfirmedMatrixSnapshot:
    return ConfirmedMatrixSnapshot(
        version=ConfirmedMatrixVersion(
            confirmed_matrix_id="cmv-1",
            project_id="P1",
            project_matrix_draft_id="pmd-1",
            source_import_id="smi-1",
            source_snapshot_id="sms-1",
            confirmed_revision=2,
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
        rows=(
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
                cell_value="1",
            ),
            ConfirmedMatrixCell(
                confirmed_cell_id="cmc-2",
                confirmed_matrix_id="cmv-1",
                confirmed_row_id="cmr-2",
                confirmed_group_id="cmg-1",
                draft_row_id="pmdr-2",
                draft_group_id="pmdg-1",
                cell_value="2(a)",
            ),
            ConfirmedMatrixCell(
                confirmed_cell_id="cmc-3",
                confirmed_matrix_id="cmv-1",
                confirmed_row_id="cmr-2",
                confirmed_group_id="cmg-2",
                draft_row_id="pmdr-2",
                draft_group_id="pmdg-2",
                cell_value="3",
            ),
        ),
    )
