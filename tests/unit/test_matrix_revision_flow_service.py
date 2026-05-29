from __future__ import annotations

from copy import deepcopy

import pytest
from sqlalchemy.exc import IntegrityError

from backend.application.matrix_revision_flow_service import (
    ConfirmMatrixRevisionDraftCommand,
    CreateMatrixRevisionDraftCommand,
    MatrixRevisionFlowConflictError,
    MatrixRevisionFlowError,
    MatrixRevisionFlowNotFoundError,
    MatrixRevisionFlowService,
)
from backend.domain import (
    ConfirmedMatrixCell,
    ConfirmedMatrixGroup,
    ConfirmedMatrixRow,
    ConfirmedMatrixSnapshot,
    ConfirmedMatrixStatus,
    ConfirmedMatrixVersion,
    Project,
    ProjectMatrixDraftRecord,
    ProjectMatrixDraftStatus,
    ProjectStatus,
)


def test_create_revision_draft_copies_active_confirmed_without_sample_placeholder() -> None:
    service, stores = _service()
    before_active = deepcopy(stores.active_confirmed)
    draft = service.create_revision_draft(
        CreateMatrixRevisionDraftCommand(project_id="P1")
    )
    assert draft.record.project_id == "P1"
    assert draft.record.base_confirmed_matrix_id == "cmv-1"
    assert draft.record.source_import_id is None
    assert all(group.is_selected for group in draft.groups)
    assert len(draft.rows) == 2
    assert all(not row.is_sample_row for row in draft.rows)
    assert len(draft.cells) == 2
    assert stores.active_confirmed == before_active


def test_create_revision_draft_rejects_duplicate_base_lineage_draft() -> None:
    service, stores = _service()
    stores.draft_store.base_record = ProjectMatrixDraftRecord(
        project_matrix_draft_id="pmd-existing",
        project_id="P1",
        source_import_id=None,
        source_snapshot_id="sms-1",
        status=ProjectMatrixDraftStatus.DRAFT,
        created_at="2026-05-23T08:00:00+00:00",
        updated_at="2026-05-23T08:00:00+00:00",
        base_confirmed_matrix_id="cmv-1",
    )
    with pytest.raises(MatrixRevisionFlowConflictError, match="Revision draft already exists"):
        service.create_revision_draft(CreateMatrixRevisionDraftCommand(project_id="P1"))


def test_confirm_revision_draft_happy_path_supersedes_previous_active() -> None:
    service, stores = _service()
    revision_draft = service.create_revision_draft(
        CreateMatrixRevisionDraftCommand(project_id="P1")
    )
    stores.draft_store.snapshot_by_id[revision_draft.record.project_matrix_draft_id] = revision_draft
    confirmed = service.confirm_revision_draft(
        ConfirmMatrixRevisionDraftCommand(
            project_id="P1",
            project_matrix_draft_id=revision_draft.record.project_matrix_draft_id,
            confirmed_by="operator",
            superseded_reason="Update matrix groups",
        )
    )
    assert confirmed.version.confirmed_revision == 2
    assert confirmed.version.project_id == "P1"
    assert stores.confirmed_store.superseded_previous_id == "cmv-1"
    assert stores.confirmed_store.superseded_reason == "Update matrix groups"


def test_confirm_revision_draft_rejects_stale_base_lineage() -> None:
    service, stores = _service()
    revision_draft = service.create_revision_draft(
        CreateMatrixRevisionDraftCommand(project_id="P1")
    )
    stale = revision_draft.record
    revision_draft = revision_draft.__class__(
        record=ProjectMatrixDraftRecord(
            project_matrix_draft_id=stale.project_matrix_draft_id,
            project_id=stale.project_id,
            source_import_id=stale.source_import_id,
            source_snapshot_id=stale.source_snapshot_id,
            status=stale.status,
            created_at=stale.created_at,
            updated_at=stale.updated_at,
            base_confirmed_matrix_id="cmv-old",
        ),
        groups=revision_draft.groups,
        rows=revision_draft.rows,
        cells=revision_draft.cells,
    )
    stores.draft_store.snapshot_by_id[revision_draft.record.project_matrix_draft_id] = revision_draft
    with pytest.raises(MatrixRevisionFlowConflictError, match="stale"):
        service.confirm_revision_draft(
            ConfirmMatrixRevisionDraftCommand(
                project_id="P1",
                project_matrix_draft_id=revision_draft.record.project_matrix_draft_id,
                confirmed_by="operator",
            )
        )


def test_confirm_revision_draft_requires_base_confirmed_matrix_id() -> None:
    service, stores = _service()
    revision_draft = service.create_revision_draft(
        CreateMatrixRevisionDraftCommand(project_id="P1")
    )
    no_base = revision_draft.record
    revision_draft = revision_draft.__class__(
        record=ProjectMatrixDraftRecord(
            project_matrix_draft_id=no_base.project_matrix_draft_id,
            project_id=no_base.project_id,
            source_import_id=no_base.source_import_id,
            source_snapshot_id=no_base.source_snapshot_id,
            status=no_base.status,
            created_at=no_base.created_at,
            updated_at=no_base.updated_at,
            base_confirmed_matrix_id=None,
        ),
        groups=revision_draft.groups,
        rows=revision_draft.rows,
        cells=revision_draft.cells,
    )
    stores.draft_store.snapshot_by_id[revision_draft.record.project_matrix_draft_id] = revision_draft
    with pytest.raises(MatrixRevisionFlowError, match="base_confirmed_matrix_id"):
        service.confirm_revision_draft(
            ConfirmMatrixRevisionDraftCommand(
                project_id="P1",
                project_matrix_draft_id=revision_draft.record.project_matrix_draft_id,
                confirmed_by="operator",
            )
        )


def test_confirm_revision_draft_validates_selected_groups_and_sample_quantity() -> None:
    service, stores = _service()
    revision_draft = service.create_revision_draft(
        CreateMatrixRevisionDraftCommand(project_id="P1")
    )
    modified_groups = list(revision_draft.groups)
    modified_groups[0] = modified_groups[0].__class__(
        draft_group_id=modified_groups[0].draft_group_id,
        project_matrix_draft_id=modified_groups[0].project_matrix_draft_id,
        source_group_snapshot_id=modified_groups[0].source_group_snapshot_id,
        group_order=modified_groups[0].group_order,
        group_key=modified_groups[0].group_key,
        group_label=modified_groups[0].group_label,
        is_selected=False,
        sample_quantity_expression=modified_groups[0].sample_quantity_expression,
        sample_note=modified_groups[0].sample_note,
    )
    modified_groups[1] = modified_groups[1].__class__(
        draft_group_id=modified_groups[1].draft_group_id,
        project_matrix_draft_id=modified_groups[1].project_matrix_draft_id,
        source_group_snapshot_id=modified_groups[1].source_group_snapshot_id,
        group_order=modified_groups[1].group_order,
        group_key=modified_groups[1].group_key,
        group_label=modified_groups[1].group_label,
        is_selected=True,
        sample_quantity_expression=" ",
        sample_note=modified_groups[1].sample_note,
    )
    revision_draft = revision_draft.__class__(
        record=revision_draft.record,
        groups=tuple(modified_groups),
        rows=revision_draft.rows,
        cells=revision_draft.cells,
    )
    stores.draft_store.snapshot_by_id[revision_draft.record.project_matrix_draft_id] = revision_draft
    with pytest.raises(
        MatrixRevisionFlowError,
        match="Sample quantity is required for selected groups: G2.",
    ):
        service.confirm_revision_draft(
            ConfirmMatrixRevisionDraftCommand(
                project_id="P1",
                project_matrix_draft_id=revision_draft.record.project_matrix_draft_id,
                confirmed_by="operator",
            )
        )


def test_matrix_revision_service_maps_integrity_error_to_conflict() -> None:
    service, stores = _service()
    revision_draft = service.create_revision_draft(
        CreateMatrixRevisionDraftCommand(project_id="P1")
    )
    stores.draft_store.snapshot_by_id[revision_draft.record.project_matrix_draft_id] = revision_draft
    stores.confirmed_store.raise_integrity_error = True
    with pytest.raises(MatrixRevisionFlowConflictError, match="conflicts"):
        service.confirm_revision_draft(
            ConfirmMatrixRevisionDraftCommand(
                project_id="P1",
                project_matrix_draft_id=revision_draft.record.project_matrix_draft_id,
                confirmed_by="operator",
            )
        )


def test_matrix_revision_service_not_found_cases() -> None:
    service, _ = _service(project_exists=False)
    with pytest.raises(MatrixRevisionFlowNotFoundError, match="Project not found"):
        service.create_revision_draft(CreateMatrixRevisionDraftCommand(project_id="P1"))

    service2, stores2 = _service()
    stores2.confirmed_store.active = None
    with pytest.raises(MatrixRevisionFlowNotFoundError, match="Active confirmed matrix not found"):
        service2.create_revision_draft(CreateMatrixRevisionDraftCommand(project_id="P1"))


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
    def __init__(self) -> None:
        self.created = []
        self.snapshot_by_id = {}
        self.base_record = None

    def create_snapshot(self, snapshot):
        self.created.append(snapshot)
        self.snapshot_by_id[snapshot.record.project_matrix_draft_id] = snapshot
        return snapshot

    def get(self, project_matrix_draft_id: str):
        return self.snapshot_by_id.get(project_matrix_draft_id)

    def get_by_project_and_base_confirmed_matrix(
        self,
        project_id: str,
        base_confirmed_matrix_id: str,
    ):
        record = self.base_record
        if (
            record
            and record.project_id == project_id
            and record.base_confirmed_matrix_id == base_confirmed_matrix_id
        ):
            return record
        return None


class _ConfirmedStore:
    def __init__(self, active: ConfirmedMatrixSnapshot | None) -> None:
        self.active = active
        self.superseded_previous_id = None
        self.superseded_reason = None
        self.raise_integrity_error = False

    def get_active_by_project(self, project_id: str):
        if self.active and self.active.version.project_id == project_id:
            return self.active
        return None

    def supersede_active_and_create_snapshot(
        self,
        *,
        previous_active_confirmed_matrix_id: str,
        snapshot: ConfirmedMatrixSnapshot,
        superseded_reason: str | None = None,
    ):
        if self.raise_integrity_error:
            raise IntegrityError("insert", {}, Exception("unique conflict"))
        self.superseded_previous_id = previous_active_confirmed_matrix_id
        self.superseded_reason = superseded_reason
        self.active = snapshot
        return snapshot


class _Stores:
    def __init__(self, *, active_confirmed, draft_store, confirmed_store) -> None:
        self.active_confirmed = active_confirmed
        self.draft_store = draft_store
        self.confirmed_store = confirmed_store


def _service(
    *,
    project_exists: bool = True,
) -> tuple[MatrixRevisionFlowService, _Stores]:
    active_confirmed = ConfirmedMatrixSnapshot(
        version=ConfirmedMatrixVersion(
            confirmed_matrix_id="cmv-1",
            project_id="P1",
            project_matrix_draft_id="pmd-base",
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
                group_label="G1",
                sample_quantity_expression="5",
            ),
            ConfirmedMatrixGroup(
                confirmed_group_id="cmg-2",
                confirmed_matrix_id="cmv-1",
                draft_group_id="pmdg-2",
                source_group_snapshot_id="smg-2",
                group_order=2,
                group_key="g2",
                group_label="G2",
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
            ConfirmedMatrixCell(
                confirmed_cell_id="cmc-2",
                confirmed_matrix_id="cmv-1",
                confirmed_row_id="cmr-2",
                confirmed_group_id="cmg-2",
                draft_row_id="pmdr-2",
                draft_group_id="pmdg-2",
                cell_value="2",
            ),
        ),
    )
    draft_store = _DraftStore()
    confirmed_store = _ConfirmedStore(active_confirmed)
    stores = _Stores(
        active_confirmed=active_confirmed,
        draft_store=draft_store,
        confirmed_store=confirmed_store,
    )
    service = MatrixRevisionFlowService(
        project_store=_ProjectStore(exists=project_exists),
        draft_store=draft_store,
        confirmed_store=confirmed_store,
    )
    return service, stores
