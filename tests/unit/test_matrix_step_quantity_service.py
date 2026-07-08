from __future__ import annotations

import pytest

from backend.application.matrix_step_quantity_service import (
    MatrixStepQuantitySaveCommand,
    MatrixStepQuantitySaveItem,
    MatrixStepQuantityService,
    MatrixStepQuantityValidationError,
)
from backend.application.project_basic_information_service import (
    ProjectBasicInformationRecord,
)
from backend.domain import (
    ProjectMatrixDraftCell,
    ProjectMatrixDraftGroup,
    ProjectMatrixDraftRecord,
    ProjectMatrixDraftRow,
    ProjectMatrixDraftSnapshot,
    ProjectMatrixDraftStatus,
)


def test_step_quantities_import_confirmed_basic_information_defaults_before_draft() -> None:
    draft_store = _DraftStore(_draft_snapshot())
    basic_information_store = _BasicInformationStore(
        confirmed=_basic_information_record(
            "confirmed",
            {
                "test_points_per_sample": "3",
                "readings_per_point": "2",
                "contact_points_per_sample": "4",
            },
        ),
        draft=_basic_information_record(
            "draft",
            {
                "test_points_per_sample": "9",
                "readings_per_point": "9",
                "contact_points_per_sample": "9",
            },
        ),
    )
    service = MatrixStepQuantityService(
        draft_store=draft_store,
        basic_information_store=basic_information_store,
        clock=lambda: "2026-07-08T09:00:00+00:00",
        id_factory=lambda: "qty-id",
    )

    response = service.get_draft(
        project_id="P1",
        project_matrix_draft_id="draft-1",
    )

    assert len(response.items) == 1
    item = response.items[0]
    assert item.test_points_per_sample == "3"
    assert item.readings_per_point == "2"
    assert item.contact_points_per_sample == "4"
    assert item.total_readings == "6"
    assert item.source == "basic_information_confirmed"
    assert item.review_required is False


def test_step_quantity_override_persists_as_matrix_step_authority() -> None:
    draft_store = _DraftStore(_draft_snapshot())
    service = MatrixStepQuantityService(
        draft_store=draft_store,
        basic_information_store=_BasicInformationStore(),
        clock=lambda: "2026-07-08T09:00:00+00:00",
        id_factory=lambda: "qty-id",
    )

    response = service.save_draft(
        MatrixStepQuantitySaveCommand(
            project_id="P1",
            project_matrix_draft_id="draft-1",
            items=(
                MatrixStepQuantitySaveItem(
                    draft_group_id="group-1",
                    draft_row_id="row-1",
                    step_sequence=1,
                    step_suffix_note=None,
                    raw_token="1",
                    test_points_per_sample="5",
                    readings_per_point="4",
                    contact_points_per_sample="2",
                    source="matrix_step_override",
                    review_required=False,
                    review_reason=None,
                ),
            ),
        )
    )

    assert len(draft_store.saved_quantities) == 1
    saved = draft_store.saved_quantities[0]
    assert saved.test_points_per_sample == "5"
    assert saved.readings_per_point == "4"
    assert saved.contact_points_per_sample == "2"
    assert saved.source == "matrix_step_override"
    assert response.items[0].total_readings == "20"


def test_step_quantity_save_rejects_negative_numeric_values() -> None:
    service = MatrixStepQuantityService(
        draft_store=_DraftStore(_draft_snapshot()),
        basic_information_store=_BasicInformationStore(),
        clock=lambda: "2026-07-08T09:00:00+00:00",
        id_factory=lambda: "qty-id",
    )

    with pytest.raises(MatrixStepQuantityValidationError, match="Test points / sample"):
        service.save_draft(
            MatrixStepQuantitySaveCommand(
                project_id="P1",
                project_matrix_draft_id="draft-1",
                items=(
                    MatrixStepQuantitySaveItem(
                        draft_group_id="group-1",
                        draft_row_id="row-1",
                        step_sequence=1,
                        step_suffix_note=None,
                        raw_token="1",
                        test_points_per_sample="-1",
                        readings_per_point="4",
                        contact_points_per_sample="2",
                        source="matrix_step_override",
                        review_required=False,
                        review_reason=None,
                    ),
                ),
            )
        )


def test_step_quantity_save_rejects_duplicate_no_suffix_payload_identities() -> None:
    service = MatrixStepQuantityService(
        draft_store=_DraftStore(_draft_snapshot()),
        basic_information_store=_BasicInformationStore(),
        clock=lambda: "2026-07-08T09:00:00+00:00",
        id_factory=lambda: "qty-id",
    )
    duplicate_item = MatrixStepQuantitySaveItem(
        draft_group_id="group-1",
        draft_row_id="row-1",
        step_sequence=1,
        step_suffix_note=None,
        raw_token="1",
        test_points_per_sample="5",
        readings_per_point="4",
        contact_points_per_sample="2",
        source="matrix_step_override",
        review_required=False,
        review_reason=None,
    )

    with pytest.raises(MatrixStepQuantityValidationError, match="Duplicate Step quantity"):
        service.save_draft(
            MatrixStepQuantitySaveCommand(
                project_id="P1",
                project_matrix_draft_id="draft-1",
                items=(duplicate_item, duplicate_item),
            )
        )


class _DraftStore:
    def __init__(self, snapshot: ProjectMatrixDraftSnapshot) -> None:
        self._snapshot = snapshot
        self.saved_quantities = []

    def get(self, project_matrix_draft_id: str) -> ProjectMatrixDraftSnapshot | None:
        if project_matrix_draft_id != self._snapshot.record.project_matrix_draft_id:
            return None
        return self._snapshot

    def replace_step_quantities(self, project_matrix_draft_id: str, quantities):
        self.saved_quantities = list(quantities)
        self._snapshot = ProjectMatrixDraftSnapshot(
            record=self._snapshot.record,
            groups=self._snapshot.groups,
            rows=self._snapshot.rows,
            cells=self._snapshot.cells,
            step_quantities=tuple(quantities),
        )
        return tuple(quantities)


class _BasicInformationStore:
    def __init__(
        self,
        *,
        confirmed: ProjectBasicInformationRecord | None = None,
        draft: ProjectBasicInformationRecord | None = None,
    ) -> None:
        self._confirmed = confirmed
        self._draft = draft

    def get_latest_confirmed(self, project_id: str) -> ProjectBasicInformationRecord | None:
        return self._confirmed if project_id == "P1" else None

    def get_latest_draft(self, project_id: str) -> ProjectBasicInformationRecord | None:
        return self._draft if project_id == "P1" else None


def _draft_snapshot() -> ProjectMatrixDraftSnapshot:
    return ProjectMatrixDraftSnapshot(
        record=ProjectMatrixDraftRecord(
            project_matrix_draft_id="draft-1",
            project_id="P1",
            source_import_id="import-1",
            source_snapshot_id="snapshot-1",
            status=ProjectMatrixDraftStatus.DRAFT,
            created_at="2026-07-08T08:00:00+00:00",
            updated_at="2026-07-08T08:00:00+00:00",
        ),
        groups=(
            ProjectMatrixDraftGroup(
                draft_group_id="group-1",
                project_matrix_draft_id="draft-1",
                source_group_snapshot_id=None,
                group_order=1,
                group_key="g1",
                group_label="1",
                is_selected=True,
                sample_quantity_expression="5",
            ),
        ),
        rows=(
            ProjectMatrixDraftRow(
                draft_row_id="row-1",
                project_matrix_draft_id="draft-1",
                source_row_snapshot_id=None,
                row_order=1,
                test_item="LLCR",
                source_section="1.1",
                method="EIA-364",
                condition="Low level",
                requirement="Meet spec",
            ),
        ),
        cells=(
            ProjectMatrixDraftCell(
                draft_cell_id="cell-1",
                project_matrix_draft_id="draft-1",
                draft_row_id="row-1",
                draft_group_id="group-1",
                cell_value="1",
            ),
        ),
    )


def _basic_information_record(
    status: str,
    values: dict[str, str],
) -> ProjectBasicInformationRecord:
    return ProjectBasicInformationRecord(
        record_id=f"bi-{status}",
        project_id="P1",
        status=status,
        version=1 if status == "confirmed" else 0,
        values=values,
        source_signature="{}",
        created_at="2026-07-08T07:00:00+00:00",
        updated_at="2026-07-08T07:00:00+00:00",
    )
