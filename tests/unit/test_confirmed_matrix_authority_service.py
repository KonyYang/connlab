from __future__ import annotations

from copy import deepcopy

import pytest
from sqlalchemy.exc import IntegrityError

from backend.application.confirmed_matrix_authority_service import (
    ConfirmProjectMatrixDraftCommand,
    ConfirmedMatrixAuthorityConflictError,
    ConfirmedMatrixAuthorityError,
    ConfirmedMatrixAuthorityNotFoundError,
    ConfirmedMatrixAuthorityService,
)
from backend.domain import (
    ConfirmedMatrixStatus,
    Project,
    ProjectMatrixDraftCell,
    ProjectMatrixDraftGroup,
    ProjectMatrixDraftRecord,
    ProjectMatrixDraftRow,
    ProjectMatrixDraftSnapshot,
    ProjectMatrixDraftStatus,
    ProjectMatrixDraftStepQuantity,
    ProjectStatus,
)


def test_confirmed_matrix_authority_service_happy_path_copies_scope_and_lineage() -> None:
    service, stores = _service()
    before = deepcopy(stores.draft_snapshot)

    confirmed = service.confirm_draft(
        ConfirmProjectMatrixDraftCommand(
            project_id="P1",
            project_matrix_draft_id="pmd-1",
            confirmed_by="operator",
        )
    )

    assert confirmed.version.project_id == "P1"
    assert confirmed.version.project_matrix_draft_id == "pmd-1"
    assert confirmed.version.source_import_id == "smi-1"
    assert confirmed.version.source_snapshot_id == "sms-1"
    assert confirmed.version.confirmed_revision == 1
    assert confirmed.version.is_active_authority is True
    assert confirmed.version.status == ConfirmedMatrixStatus.CONFIRMED
    assert confirmed.version.confirmed_by == "operator"
    assert [group.group_key for group in confirmed.groups] == ["g1", "g2"]
    assert [group.group_order for group in confirmed.groups] == [1, 2]
    assert all(group.sample_quantity_expression for group in confirmed.groups)
    assert len(confirmed.rows) == 2
    assert [row.row_order for row in confirmed.rows] == [1, 2]
    assert confirmed.rows[0].method == "M1"
    assert confirmed.rows[0].condition == "C1"
    assert confirmed.rows[0].requirement == "R1"
    assert confirmed.rows[0].day_expression == "0.5x"
    assert confirmed.version.pre_test_buffer_days == "1"
    assert confirmed.version.post_test_buffer_days == "1"
    assert confirmed.version.sample_received_date == "2026-06-01"
    assert confirmed.version.planned_test_start_date == "2026-06-02"
    assert confirmed.version.planned_test_complete_date == "2026-06-04"
    assert confirmed.version.estimated_completion_date == "2026-06-05"
    assert len(confirmed.cells) == 2
    assert sorted(cell.cell_value for cell in confirmed.cells) == ["1", "2"]
    assert stores.draft_snapshot == before


def test_confirmed_matrix_authority_service_copies_step_quantities_to_authority() -> None:
    service, _ = _service(
        step_quantities=(
            ProjectMatrixDraftStepQuantity(
                draft_step_quantity_id="pmdsq-1",
                project_matrix_draft_id="pmd-1",
                draft_group_id="pmdg-1",
                draft_row_id="pmdr-1",
                step_sequence=1,
                step_suffix_note=None,
                raw_token="1",
                test_points_per_sample="3",
                readings_per_point="2",
                contact_points_per_sample="4",
                source="matrix_step_override",
                review_required=False,
                review_reason=None,
                updated_at="2026-07-08T09:00:00+00:00",
            ),
        ),
    )

    confirmed = service.confirm_draft(
        ConfirmProjectMatrixDraftCommand(
            project_id="P1",
            project_matrix_draft_id="pmd-1",
            confirmed_by="operator",
        )
    )

    copied = [
        item
        for item in confirmed.step_quantities
        if item.draft_group_id == "pmdg-1" and item.draft_row_id == "pmdr-1"
    ]
    assert len(copied) == 1
    assert copied[0].test_points_per_sample == "3"
    assert copied[0].readings_per_point == "2"
    assert copied[0].contact_points_per_sample == "4"
    assert copied[0].source == "matrix_step_override"
    assert copied[0].review_required is False


def test_confirmed_matrix_authority_service_marks_missing_step_quantity_review_required() -> None:
    service, _ = _service()

    confirmed = service.confirm_draft(
        ConfirmProjectMatrixDraftCommand(
            project_id="P1",
            project_matrix_draft_id="pmd-1",
            confirmed_by="operator",
        )
    )

    assert confirmed.step_quantities
    assert all(item.review_required for item in confirmed.step_quantities)
    assert {item.review_reason for item in confirmed.step_quantities} == {
        "Quantity setup not confirmed."
    }


def test_confirmed_matrix_authority_service_rejects_no_selected_groups() -> None:
    service, _ = _service(selected_flags=(False, False, False))
    with pytest.raises(ConfirmedMatrixAuthorityError, match="At least one selected group"):
        service.confirm_draft(
            ConfirmProjectMatrixDraftCommand(
                project_id="P1",
                project_matrix_draft_id="pmd-1",
                confirmed_by="operator",
            )
        )


def test_confirmed_matrix_authority_service_rejects_blank_selected_group_key_or_label() -> None:
    service, _ = _service(group_key_override=" ", group_label_override="Label")
    with pytest.raises(ConfirmedMatrixAuthorityError, match="group_key and group_label"):
        service.confirm_draft(
            ConfirmProjectMatrixDraftCommand(
                project_id="P1",
                project_matrix_draft_id="pmd-1",
                confirmed_by="operator",
            )
        )

    service2, _ = _service(group_key_override="g1", group_label_override=" ")
    with pytest.raises(ConfirmedMatrixAuthorityError, match="group_key and group_label"):
        service2.confirm_draft(
            ConfirmProjectMatrixDraftCommand(
                project_id="P1",
                project_matrix_draft_id="pmd-1",
                confirmed_by="operator",
            )
        )


def test_confirmed_matrix_authority_service_rejects_blank_selected_group_sample_quantity() -> None:
    service, _ = _service(sample_quantity_override=" ")
    with pytest.raises(ConfirmedMatrixAuthorityError, match="sample quantity expression"):
        service.confirm_draft(
            ConfirmProjectMatrixDraftCommand(
                project_id="P1",
                project_matrix_draft_id="pmd-1",
                confirmed_by="operator",
            )
        )


def test_confirmed_matrix_authority_service_rejects_existing_active_authority() -> None:
    service, stores = _service()
    stores.confirmed_store.active_exists = True
    with pytest.raises(ConfirmedMatrixAuthorityConflictError, match="active confirmed matrix"):
        service.confirm_draft(
            ConfirmProjectMatrixDraftCommand(
                project_id="P1",
                project_matrix_draft_id="pmd-1",
                confirmed_by="operator",
            )
        )


def test_confirmed_matrix_authority_service_maps_db_uniqueness_error_to_conflict() -> None:
    service, stores = _service()
    stores.confirmed_store.raise_integrity_error = True
    with pytest.raises(ConfirmedMatrixAuthorityConflictError, match="active confirmed matrix"):
        service.confirm_draft(
            ConfirmProjectMatrixDraftCommand(
                project_id="P1",
                project_matrix_draft_id="pmd-1",
                confirmed_by="operator",
            )
        )


def test_confirmed_matrix_authority_service_rejects_missing_project_or_draft() -> None:
    service, _ = _service(project_exists=False)
    with pytest.raises(ConfirmedMatrixAuthorityNotFoundError, match="Project not found"):
        service.confirm_draft(
            ConfirmProjectMatrixDraftCommand(
                project_id="P1",
                project_matrix_draft_id="pmd-1",
                confirmed_by="operator",
            )
        )

    service2, stores2 = _service()
    stores2.draft_store.snapshot = None
    with pytest.raises(ConfirmedMatrixAuthorityNotFoundError, match="Project matrix draft not found"):
        service2.confirm_draft(
            ConfirmProjectMatrixDraftCommand(
                project_id="P1",
                project_matrix_draft_id="pmd-1",
                confirmed_by="operator",
            )
        )


def test_confirmed_matrix_authority_service_requires_confirmed_by() -> None:
    service, _ = _service()
    with pytest.raises(ConfirmedMatrixAuthorityError, match="confirmed_by is required"):
        service.confirm_draft(
            ConfirmProjectMatrixDraftCommand(
                project_id="P1",
                project_matrix_draft_id="pmd-1",
                confirmed_by=" ",
            )
        )


class _ProjectStore:
    def __init__(self, *, exists: bool) -> None:
        self._project = (
            Project(
                project_id="P1",
                project_no="DL-2026-05-001",
                product_name="Connector",
                requestor="Alice",
                status=ProjectStatus.LTR_REGISTERED,
            )
            if exists
            else None
        )

    def get(self, project_id: str) -> Project | None:
        if self._project and self._project.project_id == project_id:
            return self._project
        return None


class _DraftStore:
    def __init__(self, snapshot: ProjectMatrixDraftSnapshot | None) -> None:
        self.snapshot = snapshot

    def get(self, project_matrix_draft_id: str) -> ProjectMatrixDraftSnapshot | None:
        if self.snapshot and self.snapshot.record.project_matrix_draft_id == project_matrix_draft_id:
            return self.snapshot
        return None


class _ConfirmedStore:
    def __init__(self) -> None:
        self.active_exists = False
        self.raise_integrity_error = False
        self.created_snapshots = []

    def get_active_by_project(self, project_id: str):
        if self.active_exists:
            return self.created_snapshots[0] if self.created_snapshots else object()
        return None

    def create_snapshot(self, snapshot):
        if self.raise_integrity_error:
            raise IntegrityError("insert", {}, Exception("unique conflict"))
        self.created_snapshots.append(snapshot)
        return snapshot


class _Stores:
    def __init__(
        self,
        *,
        draft_snapshot: ProjectMatrixDraftSnapshot,
        draft_store: _DraftStore,
        confirmed_store: _ConfirmedStore,
    ) -> None:
        self.draft_snapshot = draft_snapshot
        self.draft_store = draft_store
        self.confirmed_store = confirmed_store


def _service(
    *,
    project_exists: bool = True,
    selected_flags: tuple[bool, bool, bool] = (True, True, False),
    group_key_override: str | None = None,
    group_label_override: str | None = None,
    sample_quantity_override: str | None = None,
    step_quantities: tuple[ProjectMatrixDraftStepQuantity, ...] = (),
) -> tuple[ConfirmedMatrixAuthorityService, _Stores]:
    groups = (
        ProjectMatrixDraftGroup(
            draft_group_id="pmdg-1",
            project_matrix_draft_id="pmd-1",
            source_group_snapshot_id="smg-1",
            group_order=1,
            group_key=group_key_override if group_key_override is not None else "g1",
            group_label=group_label_override if group_label_override is not None else "G1",
            is_selected=selected_flags[0],
            sample_quantity_expression=(
                sample_quantity_override if sample_quantity_override is not None else "5"
            ),
        ),
        ProjectMatrixDraftGroup(
            draft_group_id="pmdg-2",
            project_matrix_draft_id="pmd-1",
            source_group_snapshot_id="smg-2",
            group_order=2,
            group_key="g2",
            group_label="G2",
            is_selected=selected_flags[1],
            sample_quantity_expression="6",
        ),
        ProjectMatrixDraftGroup(
            draft_group_id="pmdg-3",
            project_matrix_draft_id="pmd-1",
            source_group_snapshot_id="smg-3",
            group_order=3,
            group_key="g3",
            group_label="G3",
            is_selected=selected_flags[2],
            sample_quantity_expression="7",
        ),
    )
    rows = (
        ProjectMatrixDraftRow(
            draft_row_id="pmdr-1",
            project_matrix_draft_id="pmd-1",
            source_row_snapshot_id="smr-1",
            row_order=1,
            test_item="Visual",
            source_section="6.1",
            method="M1",
            condition="C1",
            requirement="R1",
            day_expression="0.5x",
            is_sample_row=False,
        ),
        ProjectMatrixDraftRow(
            draft_row_id="pmdr-2",
            project_matrix_draft_id="pmd-1",
            source_row_snapshot_id="smr-2",
            row_order=2,
            test_item="LLCR",
            source_section="6.2",
            method="M2",
            condition="C2",
            requirement="R2",
            day_expression="1",
            is_sample_row=False,
        ),
        ProjectMatrixDraftRow(
            draft_row_id="pmdr-3",
            project_matrix_draft_id="pmd-1",
            source_row_snapshot_id="smr-3",
            row_order=3,
            test_item="Samples Quantity (PCS)",
            is_sample_row=True,
        ),
    )
    cells = (
        ProjectMatrixDraftCell(
            draft_cell_id="pmdc-1",
            project_matrix_draft_id="pmd-1",
            draft_row_id="pmdr-1",
            draft_group_id="pmdg-1",
            cell_value="1",
        ),
        ProjectMatrixDraftCell(
            draft_cell_id="pmdc-2",
            project_matrix_draft_id="pmd-1",
            draft_row_id="pmdr-1",
            draft_group_id="pmdg-2",
            cell_value=" ",
        ),
        ProjectMatrixDraftCell(
            draft_cell_id="pmdc-3",
            project_matrix_draft_id="pmd-1",
            draft_row_id="pmdr-2",
            draft_group_id="pmdg-2",
            cell_value="2",
        ),
        ProjectMatrixDraftCell(
            draft_cell_id="pmdc-4",
            project_matrix_draft_id="pmd-1",
            draft_row_id="pmdr-2",
            draft_group_id="pmdg-3",
            cell_value="9",
        ),
        ProjectMatrixDraftCell(
            draft_cell_id="pmdc-5",
            project_matrix_draft_id="pmd-1",
            draft_row_id="pmdr-3",
            draft_group_id="pmdg-1",
            cell_value="5",
        ),
    )
    snapshot = ProjectMatrixDraftSnapshot(
        record=ProjectMatrixDraftRecord(
            project_matrix_draft_id="pmd-1",
            project_id="P1",
            source_import_id="smi-1",
            source_snapshot_id="sms-1",
            status=ProjectMatrixDraftStatus.DRAFT,
            created_at="2026-05-23T08:00:00+00:00",
            updated_at="2026-05-23T08:00:00+00:00",
            pre_test_buffer_days="1",
            post_test_buffer_days="1",
            sample_received_date="2026-06-01",
            planned_test_start_date="2026-06-02",
            planned_test_complete_date="2026-06-04",
            estimated_completion_date="2026-06-05",
        ),
        groups=groups,
        rows=rows,
        cells=cells,
        step_quantities=step_quantities,
    )
    draft_store = _DraftStore(snapshot=snapshot)
    confirmed_store = _ConfirmedStore()
    stores = _Stores(
        draft_snapshot=snapshot,
        draft_store=draft_store,
        confirmed_store=confirmed_store,
    )
    service = ConfirmedMatrixAuthorityService(
        project_store=_ProjectStore(exists=project_exists),
        draft_store=draft_store,
        confirmed_store=confirmed_store,
    )
    return service, stores
