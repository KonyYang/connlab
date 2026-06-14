from __future__ import annotations

from datetime import date

import pytest

from backend.application.matrix_editor_session_service import (
    MatrixEditorSessionActiveChangedError,
    MatrixEditorSessionCell,
    MatrixEditorSessionConfirmCommand,
    MatrixEditorSessionError,
    MatrixEditorSessionGroup,
    MatrixEditorSessionRow,
    MatrixEditorSessionService,
    SOURCE_UNAVAILABLE_MESSAGE,
)
from backend.domain import (
    ConfirmedMatrixCell,
    ConfirmedMatrixGroup,
    ConfirmedMatrixRow,
    ConfirmedMatrixSnapshot,
    ConfirmedMatrixStatus,
    ConfirmedMatrixVersion,
    Project,
    ProjectMatrixDraftCell,
    ProjectMatrixDraftGroup,
    ProjectMatrixDraftRecord,
    ProjectMatrixDraftRow,
    ProjectMatrixDraftSnapshot,
    ProjectMatrixDraftStatus,
    ProjectStatus,
    SourceMatrixImportRecord,
    SourceMatrixImportStatus,
    SourceMatrixCellSnapshot,
    SourceMatrixGroupSnapshot,
    SourceMatrixRowSnapshot,
    SourceMatrixSnapshot,
)


def test_get_seed_when_source_snapshot_missing_returns_unavailable_message() -> None:
    active = _build_active_snapshot()
    service = _service(active=active, source_snapshot=None)
    seed = service.get_seed(project_id="P1")
    assert seed.active_confirmed_matrix_id == "cmv-1"
    assert seed.editor_draft is not None
    assert seed.source_status == "unavailable"
    assert seed.source_unavailable_message == SOURCE_UNAVAILABLE_MESSAGE
    assert seed.source_preview_payload is None


def test_get_seed_rebuilt_source_preview_payload_preserves_row_mcr() -> None:
    active = _build_active_snapshot()
    source_snapshot = SourceMatrixSnapshot(
        snapshot_id="sms-1",
        import_id="smi-1",
        project_id="P1",
        source_table_index=1,
        rows=(
            SourceMatrixRowSnapshot(
                row_snapshot_id="sr-1",
                row_order=1,
                source_row_index=3,
                test_item="Contact Resistance (Low Level)",
                source_section="6.1",
                method="EIA-364-23D",
                condition="20mV max, 100mA max",
                requirement="Initial <= 0.25 milliohms",
            ),
        ),
        groups=(
            SourceMatrixGroupSnapshot(
                group_snapshot_id="sg-1",
                group_order=1,
                group_key="g1",
                group_label="1",
                sample_quantity_expression="5",
            ),
        ),
        cells=(
            SourceMatrixCellSnapshot(
                cell_snapshot_id="sc-1",
                row_snapshot_id="sr-1",
                group_snapshot_id="sg-1",
                cell_value="1",
            ),
        ),
        created_at="2026-05-27T00:00:00Z",
    )
    service = _service(active=active, source_snapshot=source_snapshot)

    seed = service.get_seed(project_id="P1")

    assert seed.source_preview_payload is not None
    row = seed.source_preview_payload["rows"][0]
    assert row["method"] == "EIA-364-23D"
    assert row["condition"] == "20mV max, 100mA max"
    assert row["requirement"] == "Initial <= 0.25 milliohms"


def test_confirm_session_no_change_returns_http200_semantics() -> None:
    active = _build_active_snapshot()
    service = _service(active=active, source_snapshot=None)
    command = MatrixEditorSessionConfirmCommand(
        project_id="P1",
        expected_active_confirmed_matrix_id="cmv-1",
        expected_active_confirmed_revision=1,
        source_document_path=None,
        source_document_name=None,
        source_format=None,
        source_import_id=None,
        source_snapshot_id=None,
        confirmed_by="operator",
        groups=(
            MatrixEditorSessionGroup(
                draft_group_id="dg-1",
                source_group_snapshot_id="sg-1",
                group_order=1,
                group_key="g1",
                group_label="1",
                is_selected=True,
                sample_quantity_expression="5",
                sample_note=None,
            ),
        ),
        rows=(
            MatrixEditorSessionRow(
                draft_row_id="dr-1",
                source_row_snapshot_id="sr-1",
                row_order=1,
                test_item="Visual Examination",
                source_section="1.1",
                method="EIA-364-18B",
                condition="10x min magnification",
                requirement="No detrimental condition",
                is_sample_row=False,
            ),
        ),
        cells=(
            MatrixEditorSessionCell(
                draft_row_id="dr-1",
                draft_group_id="dg-1",
                cell_value="1",
            ),
        ),
    )
    result = service.confirm_session(command)
    assert result.publish_status == "no_change"
    assert result.message == "No Matrix changes to confirm."
    assert result.confirmed_snapshot is None


def test_confirm_session_no_change_ignores_unselected_source_groups() -> None:
    active = _build_active_snapshot()
    service = _service(active=active, source_snapshot=None)
    command = MatrixEditorSessionConfirmCommand(
        project_id="P1",
        expected_active_confirmed_matrix_id="cmv-1",
        expected_active_confirmed_revision=1,
        source_document_path=None,
        source_document_name=None,
        source_format=None,
        source_import_id=None,
        source_snapshot_id=None,
        confirmed_by="operator",
        groups=(
            MatrixEditorSessionGroup(
                draft_group_id="dg-1",
                source_group_snapshot_id="sg-1",
                group_order=1,
                group_key="g1",
                group_label="1",
                is_selected=True,
                sample_quantity_expression="5",
                sample_note=None,
            ),
            MatrixEditorSessionGroup(
                draft_group_id="dg-2",
                source_group_snapshot_id="sg-2",
                group_order=2,
                group_key="g2",
                group_label="2",
                is_selected=False,
                sample_quantity_expression=None,
                sample_note=None,
            ),
        ),
        rows=(
            MatrixEditorSessionRow(
                draft_row_id="dr-1",
                source_row_snapshot_id="sr-1",
                row_order=1,
                test_item="Visual Examination",
                source_section="1.1",
                method="EIA-364-18B",
                condition="10x min magnification",
                requirement="No detrimental condition",
                is_sample_row=False,
            ),
        ),
        cells=(
            MatrixEditorSessionCell(
                draft_row_id="dr-1",
                draft_group_id="dg-1",
                cell_value="1",
            ),
            MatrixEditorSessionCell(
                draft_row_id="dr-1",
                draft_group_id="dg-2",
                cell_value="2",
            ),
        ),
    )
    result = service.confirm_session(command)
    assert result.publish_status == "no_change"
    assert result.message == "No Matrix changes to confirm."
    assert result.confirmed_snapshot is None


def test_confirm_session_treats_group_prefix_as_same_signature() -> None:
    active = _build_active_snapshot()
    service = _service(active=active, source_snapshot=None)
    command = MatrixEditorSessionConfirmCommand(
        project_id="P1",
        expected_active_confirmed_matrix_id="cmv-1",
        expected_active_confirmed_revision=1,
        source_document_path=None,
        source_document_name=None,
        source_format=None,
        source_import_id=None,
        source_snapshot_id=None,
        confirmed_by="operator",
        groups=(
            MatrixEditorSessionGroup(
                draft_group_id="dg-1",
                source_group_snapshot_id="sg-1",
                group_order=1,
                group_key="g1",
                group_label="Group 1",
                is_selected=True,
                sample_quantity_expression="5",
                sample_note=None,
            ),
        ),
        rows=(
            MatrixEditorSessionRow(
                draft_row_id="dr-1",
                source_row_snapshot_id="sr-1",
                row_order=1,
                test_item="Visual Examination",
                source_section="1.1",
                method="EIA-364-18B",
                condition="10x min magnification",
                requirement="No detrimental condition",
                is_sample_row=False,
            ),
        ),
        cells=(
            MatrixEditorSessionCell(
                draft_row_id="dr-1",
                draft_group_id="dg-1",
                cell_value="1",
            ),
        ),
    )
    result = service.confirm_session(command)
    assert result.publish_status == "no_change"
    assert result.message == "No Matrix changes to confirm."
    assert result.confirmed_snapshot is None


def test_confirm_session_when_active_id_changed_raises_conflict_message() -> None:
    active = _build_active_snapshot()
    service = _service(active=active, source_snapshot=None)
    command = MatrixEditorSessionConfirmCommand(
        project_id="P1",
        expected_active_confirmed_matrix_id="cmv-old",
        expected_active_confirmed_revision=1,
        source_document_path=None,
        source_document_name=None,
        source_format=None,
        source_import_id=None,
        source_snapshot_id=None,
        confirmed_by="operator",
        groups=(
            MatrixEditorSessionGroup(
                draft_group_id="dg-1",
                source_group_snapshot_id="sg-1",
                group_order=1,
                group_key="g1",
                group_label="1",
                is_selected=True,
                sample_quantity_expression="5",
                sample_note=None,
            ),
        ),
        rows=(
            MatrixEditorSessionRow(
                draft_row_id="dr-1",
                source_row_snapshot_id="sr-1",
                row_order=1,
                test_item="Visual Examination",
                source_section="1.1",
                method="EIA-364-18B",
                condition="10x min magnification",
                requirement="No detrimental condition",
                is_sample_row=False,
            ),
        ),
        cells=(
            MatrixEditorSessionCell(
                draft_row_id="dr-1",
                draft_group_id="dg-1",
                cell_value="2",
            ),
        ),
    )
    with pytest.raises(MatrixEditorSessionActiveChangedError) as exc:
        service.confirm_session(command)
    assert "Matrix was updated. Reload the latest Matrix to continue." in str(exc.value)


def test_confirm_session_rejects_selected_group_sample_without_digit() -> None:
    active = _build_active_snapshot(sample_quantity_expression="")
    service = _service(active=active, source_snapshot=None)
    command = MatrixEditorSessionConfirmCommand(
        project_id="P1",
        expected_active_confirmed_matrix_id="cmv-1",
        expected_active_confirmed_revision=1,
        source_document_path=None,
        source_document_name=None,
        source_format=None,
        source_import_id="smi-1",
        source_snapshot_id="sms-1",
        confirmed_by="operator",
        groups=(
            MatrixEditorSessionGroup(
                draft_group_id="dg-1",
                source_group_snapshot_id="sg-1",
                group_order=1,
                group_key="g1",
                group_label="1",
                is_selected=True,
                sample_quantity_expression="sample only",
                sample_note=None,
            ),
        ),
        rows=(
            MatrixEditorSessionRow(
                draft_row_id="dr-1",
                source_row_snapshot_id="sr-1",
                row_order=1,
                test_item="Visual Examination",
                source_section="1.1",
                method="EIA-364-18B",
                condition="10x min magnification",
                requirement="No detrimental condition",
                is_sample_row=False,
            ),
        ),
        cells=(
            MatrixEditorSessionCell(
                draft_row_id="dr-1",
                draft_group_id="dg-1",
                cell_value="1",
            ),
        ),
    )
    with pytest.raises(MatrixEditorSessionError) as exc:
        service.confirm_session(command)
    assert "Sample quantity is required for selected groups: 1." in str(exc.value)


class _ProjectStore:
    def get(self, project_id: str):
        if project_id != "P1":
            return None
        return Project(
            project_id="P1",
            project_no="DL-2026-05-001",
            product_name="Connector",
            requestor="Alice",
            status=ProjectStatus.LTR_REGISTERED,
            created_on=date(2026, 5, 22),
        )


class _ConfirmedStore:
    def __init__(self, active: ConfirmedMatrixSnapshot | None) -> None:
        self._active = active

    def get_active_by_project(self, project_id: str):
        return self._active if project_id == "P1" else None

    def list_by_project(self, project_id: str):
        return (self._active,) if project_id == "P1" and self._active is not None else ()

    def supersede_active_and_create_snapshot(self, *, previous_active_confirmed_matrix_id: str, snapshot, superseded_reason=None):
        self._active = snapshot
        return snapshot


class _SourceStore:
    def __init__(self, *, source_snapshot) -> None:
        self._snapshot = source_snapshot
        self._import = SourceMatrixImportRecord(
            import_id="smi-1",
            project_id="P1",
            draft_id="ptpd-1",
            source_document_path="C:/spec.docx",
            source_document_name="spec.docx",
            source_format=".docx",
            source_asset_id=None,
            source_case_id=None,
            source_draft_id=None,
            import_status=SourceMatrixImportStatus.IMPORTED,
            source_spec_number=None,
            source_spec_revision=None,
            parse_time="2026-05-27T00:00:00Z",
            parser_version="parser-v1",
            payload_schema_version="1.0",
            warnings=(),
            blockers=(),
            selected_group_keys_at_import=("g1",),
            task261_commit_fingerprint=None,
            created_at="2026-05-27T00:00:00Z",
        )

    def get_import(self, import_id: str):
        return self._import if import_id == "smi-1" else None

    def get_snapshot(self, snapshot_id: str):
        return self._snapshot if snapshot_id == "sms-1" else None


class _DraftStore:
    def get(self, project_matrix_draft_id: str):
        return None

    def list_by_project(self, project_id: str):
        return ()

    def delete(self, project_matrix_draft_id: str):
        return None

    def get_by_project_and_base_confirmed_matrix(self, project_id: str, base_confirmed_matrix_id: str):
        return None

    def get_by_project_and_source_import(self, project_id: str, source_import_id: str):
        return None


class _DraftPersistenceService:
    def update_draft(self, command):
        raise AssertionError("update_draft should not be called in no-change tests")


class _MatrixImportCommitService:
    def commit(self, command):
        raise AssertionError("commit should not be called in no-change tests")


class _MatrixRevisionFlowService:
    def create_revision_draft(self, command):
        raise AssertionError("create_revision_draft should not be called in no-change tests")

    def confirm_revision_draft(self, command):
        raise AssertionError("confirm_revision_draft should not be called in no-change tests")


class _RecordingMatrixRevisionFlowService:
    def __init__(self) -> None:
        self.confirm_revision_called = False

    def create_revision_draft(self, command):
        return ProjectMatrixDraftSnapshot(
            record=ProjectMatrixDraftRecord(
                project_matrix_draft_id="pmd-rev",
                project_id="P1",
                source_import_id=None,
                source_snapshot_id="sms-1",
                status=ProjectMatrixDraftStatus.DRAFT,
                created_at="2026-05-27T00:00:00Z",
                updated_at="2026-05-27T00:00:00Z",
                base_confirmed_matrix_id="cmv-1",
            ),
            groups=(),
            rows=(),
            cells=(),
        )

    def confirm_revision_draft(self, command):
        self.confirm_revision_called = True
        raise AssertionError("Matrix Editor session confirm should not use legacy revision validation.")


class _RecordingDraftPersistenceService:
    def __init__(self) -> None:
        self.updated = False

    def update_draft(self, command):
        self.updated = True
        return ProjectMatrixDraftSnapshot(
            record=ProjectMatrixDraftRecord(
                project_matrix_draft_id=command.project_matrix_draft_id,
                project_id=command.project_id,
                source_import_id=None,
                source_snapshot_id="sms-1",
                status=ProjectMatrixDraftStatus.DRAFT,
                created_at="2026-05-27T00:00:00Z",
                updated_at="2026-05-27T00:00:01Z",
                base_confirmed_matrix_id="cmv-1",
            ),
            groups=tuple(
                ProjectMatrixDraftGroup(
                    draft_group_id=group.draft_group_id,
                    project_matrix_draft_id=command.project_matrix_draft_id,
                    source_group_snapshot_id=group.source_group_snapshot_id,
                    group_order=group.group_order,
                    group_key=group.group_key,
                    group_label=group.group_label,
                    is_selected=group.is_selected,
                    sample_quantity_expression=group.sample_quantity_expression,
                    sample_note=group.sample_note,
                )
                for group in command.groups
            ),
            rows=tuple(
                ProjectMatrixDraftRow(
                    draft_row_id=row.draft_row_id,
                    project_matrix_draft_id=command.project_matrix_draft_id,
                    source_row_snapshot_id=row.source_row_snapshot_id,
                    row_order=row.row_order,
                    test_item=row.test_item,
                    source_section=row.source_section,
                    method=row.method,
                    condition=row.condition,
                    requirement=row.requirement,
                    is_sample_row=row.is_sample_row,
                )
                for row in command.rows
            ),
            cells=tuple(
                ProjectMatrixDraftCell(
                    draft_cell_id=f"cell-{index}",
                    project_matrix_draft_id=command.project_matrix_draft_id,
                    draft_row_id=cell.draft_row_id,
                    draft_group_id=cell.draft_group_id,
                    cell_value=cell.cell_value,
                )
                for index, cell in enumerate(command.cells, start=1)
            ),
        )


class _ConfirmedAuthorityService:
    def confirm_draft(self, command):
        raise AssertionError("confirm_draft should not be called in no-change tests")


def _service(*, active: ConfirmedMatrixSnapshot | None, source_snapshot):
    return MatrixEditorSessionService(
        project_store=_ProjectStore(),
        confirmed_store=_ConfirmedStore(active),
        source_store=_SourceStore(source_snapshot=source_snapshot),
        draft_store=_DraftStore(),
        draft_persistence_service=_DraftPersistenceService(),
        matrix_import_commit_service=_MatrixImportCommitService(),
        matrix_revision_flow_service=_MatrixRevisionFlowService(),
        confirmed_matrix_authority_service=_ConfirmedAuthorityService(),
    )


def _build_active_snapshot(sample_quantity_expression: str = "5") -> ConfirmedMatrixSnapshot:
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
            confirmed_at="2026-05-27T00:00:00Z",
        ),
        groups=(
            ConfirmedMatrixGroup(
                confirmed_group_id="cg-1",
                confirmed_matrix_id="cmv-1",
                draft_group_id="dg-1",
                source_group_snapshot_id="sg-1",
                group_order=1,
                group_key="g1",
                group_label="1",
                sample_quantity_expression=sample_quantity_expression,
                sample_note=None,
            ),
        ),
        rows=(
            ConfirmedMatrixRow(
                confirmed_row_id="cr-1",
                confirmed_matrix_id="cmv-1",
                draft_row_id="dr-1",
                source_row_snapshot_id="sr-1",
                row_order=1,
                test_item="Visual Examination",
                source_section="1.1",
                method="EIA-364-18B",
                condition="10x min magnification",
                requirement="No detrimental condition",
            ),
        ),
        cells=(
            ConfirmedMatrixCell(
                confirmed_cell_id="cc-1",
                confirmed_matrix_id="cmv-1",
                confirmed_row_id="cr-1",
                confirmed_group_id="cg-1",
                draft_row_id="dr-1",
                draft_group_id="dg-1",
                cell_value="1",
            ),
        ),
    )
