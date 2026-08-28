from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from backend.application.matrix_editor_live_xlsx_export_service import (
    MatrixEditorLiveXlsxExportCell,
    MatrixEditorLiveXlsxExportGroup,
    MatrixEditorLiveXlsxExportRequest,
    MatrixEditorLiveXlsxExportRow,
)
from backend.application.matrix_editor_live_xlsx_publication_service import (
    ConfirmedMatrixLiveXlsxAuthorityMatcher,
    ExecuteMatrixEditorLiveXlsxPublicationCommand,
    MatrixEditorLiveXlsxPublicationBlockedError,
    MatrixEditorLiveXlsxPublicationConflictError,
    MatrixEditorLiveXlsxPublicationService,
    PreviewMatrixEditorLiveXlsxPublicationCommand,
)
from backend.infrastructure.files.test_record_publication_gateway import (
    TestRecordPublicationGateway as PublicationGateway,
)
from backend.application.project_lifecycle_write_guard import LifecycleWriteOperation


def test_preview_keeps_download_mode_before_project_folder_exists() -> None:
    service = MatrixEditorLiveXlsxPublicationService(
        workspace_store=_WorkspaceStore(None),
        authority_matcher=_AuthorityMatcher(matches=True),
        export_service=_ExportService(),
        file_gateway=_FileGateway(),
    )

    preview = service.preview(
        PreviewMatrixEditorLiveXlsxPublicationCommand("P1", _request())
    )

    assert preview.mode == "download"
    assert preview.status == "ready"


def test_authority_matcher_ignores_draft_ids_and_matches_confirmed_projection() -> None:
    matcher = ConfirmedMatrixLiveXlsxAuthorityMatcher(_ConfirmedStore(_snapshot()))

    assert matcher.matches_active_authority("P1", _request())


def test_authority_matcher_rejects_changed_matrix_content() -> None:
    matcher = ConfirmedMatrixLiveXlsxAuthorityMatcher(_ConfirmedStore(_snapshot()))
    current = _request()
    changed_row = MatrixEditorLiveXlsxExportRow(
        current.rows[0].row_id,
        current.rows[0].test_item,
        current.rows[0].section,
        current.rows[0].test_method,
        current.rows[0].condition,
        "Changed requirement",
        current.rows[0].cells,
    )
    assert not matcher.matches_active_authority(
        "P1",
        MatrixEditorLiveXlsxExportRequest(
            current.source,
            current.project_reference,
            current.groups,
            (changed_row,),
        ),
    )


def test_preview_downloads_draft_when_current_matrix_is_not_confirmed(
    tmp_path: Path,
) -> None:
    service = MatrixEditorLiveXlsxPublicationService(
        workspace_store=_WorkspaceStore(_workspace(tmp_path)),
        authority_matcher=_AuthorityMatcher(matches=False),
        export_service=_ExportService(),
        file_gateway=_FileGateway(),
    )

    preview = service.preview(
        PreviewMatrixEditorLiveXlsxPublicationCommand("P1", _request())
    )

    assert preview.mode == "download"
    assert preview.status == "ready"


def test_preview_targets_formal_matrix_in_source_book_when_authority_matches(
    tmp_path: Path,
) -> None:
    workspace = _workspace(tmp_path)
    service = MatrixEditorLiveXlsxPublicationService(
        workspace_store=_WorkspaceStore(workspace),
        authority_matcher=_AuthorityMatcher(matches=True),
        export_service=_ExportService(),
        file_gateway=_FileGateway(),
    )

    preview = service.preview(
        PreviewMatrixEditorLiveXlsxPublicationCommand("P1", _request())
    )

    assert preview.mode == "official"
    assert preview.status == "ready"
    assert preview.target_path == workspace.source_book_path / "DL-2026-08-004 Matrix.xlsx"
    assert preview.existing_file is False


def test_execute_publishes_formal_matrix_without_draft_suffix(
    tmp_path: Path,
) -> None:
    workspace = _workspace(tmp_path)
    service = MatrixEditorLiveXlsxPublicationService(
        workspace_store=_WorkspaceStore(workspace),
        authority_matcher=_AuthorityMatcher(matches=True),
        export_service=_ExportService(content=b"formal matrix"),
        file_gateway=PublicationGateway(resource_label="Matrix"),
    )
    preview = service.preview(
        PreviewMatrixEditorLiveXlsxPublicationCommand("P1", _request())
    )

    result = service.execute(
        ExecuteMatrixEditorLiveXlsxPublicationCommand(
            project_id="P1",
            request=_request(),
            preview_token=preview.preview_token,
            conflict_action="none",
            staging_dir=tmp_path / "staging",
        )
    )

    assert result.file_name == "DL-2026-08-004 Matrix.xlsx"
    assert result.target_path.read_bytes() == b"formal matrix"
    assert "Draft" not in result.file_name


def test_preview_blocks_when_formal_matrix_target_is_a_directory(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path)
    target = workspace.source_book_path / "DL-2026-08-004 Matrix.xlsx"
    target.mkdir()
    service = MatrixEditorLiveXlsxPublicationService(
        workspace_store=_WorkspaceStore(workspace),
        authority_matcher=_AuthorityMatcher(matches=True),
        export_service=_ExportService(),
        file_gateway=PublicationGateway(resource_label="Matrix"),
    )

    preview = service.preview(
        PreviewMatrixEditorLiveXlsxPublicationCommand("P1", _request())
    )

    assert preview.status == "blocked"
    with pytest.raises(MatrixEditorLiveXlsxPublicationBlockedError):
        service.execute(
            ExecuteMatrixEditorLiveXlsxPublicationCommand(
                "P1", _request(), preview.preview_token, "none", tmp_path / "staging"
            )
        )


def test_existing_formal_matrix_requires_choice_and_can_be_archived(
    tmp_path: Path,
) -> None:
    workspace = _workspace(tmp_path)
    target = workspace.source_book_path / "DL-2026-08-004 Matrix.xlsx"
    target.write_bytes(b"old matrix")
    service = MatrixEditorLiveXlsxPublicationService(
        workspace_store=_WorkspaceStore(workspace),
        authority_matcher=_AuthorityMatcher(matches=True),
        export_service=_ExportService(content=b"new matrix"),
        file_gateway=PublicationGateway(resource_label="Matrix"),
    )
    preview = service.preview(
        PreviewMatrixEditorLiveXlsxPublicationCommand("P1", _request())
    )
    assert preview.status == "conflict"

    with pytest.raises(MatrixEditorLiveXlsxPublicationConflictError):
        service.execute(
            ExecuteMatrixEditorLiveXlsxPublicationCommand(
                "P1", _request(), preview.preview_token, "none", tmp_path / "staging"
            )
        )

    result = service.execute(
        ExecuteMatrixEditorLiveXlsxPublicationCommand(
            "P1", _request(), preview.preview_token, "archive", tmp_path / "staging"
        )
    )

    assert target.read_bytes() == b"new matrix"
    assert result.archive_path is not None
    assert result.archive_path.read_bytes() == b"old matrix"
    assert result.archive_path.parent == workspace.local_workspace_path / "History" / "Matrix"


def test_execute_checks_project_lifecycle_before_writing(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path)
    guard = _LifecycleGuard()
    service = MatrixEditorLiveXlsxPublicationService(
        workspace_store=_WorkspaceStore(workspace),
        authority_matcher=_AuthorityMatcher(matches=True),
        export_service=_ExportService(content=b"formal matrix"),
        file_gateway=PublicationGateway(resource_label="Matrix"),
        lifecycle_write_guard=guard,
    )
    preview = service.preview(
        PreviewMatrixEditorLiveXlsxPublicationCommand("P1", _request())
    )

    service.execute(
        ExecuteMatrixEditorLiveXlsxPublicationCommand(
            "P1", _request(), preview.preview_token, "none", tmp_path / "staging"
        )
    )

    assert guard.calls == [("P1", LifecycleWriteOperation.MATRIX_EXPORT_PUBLISH)]


def _request() -> MatrixEditorLiveXlsxExportRequest:
    return MatrixEditorLiveXlsxExportRequest(
        source="matrix_editor_current_ui_state",
        project_reference="DL-2026-08-004",
        groups=(
            MatrixEditorLiveXlsxExportGroup("dg1", "g1", "Group 1", "5", "2 d"),
        ),
        rows=(
            MatrixEditorLiveXlsxExportRow(
                "dr1",
                "Visual Examination",
                "5.1",
                "EIA-364",
                "Normal",
                "No damage",
                (MatrixEditorLiveXlsxExportCell("dg1", "1"),),
            ),
        ),
    )


def _workspace(tmp_path: Path):
    source_book = tmp_path / "DL-2026-08-004" / "Source Book"
    source_book.mkdir(parents=True)
    return SimpleNamespace(
        dl_number="DL-2026-08-004",
        local_workspace_path=source_book.parent,
        source_book_path=source_book,
    )


class _WorkspaceStore:
    def __init__(self, workspace) -> None:
        self.workspace = workspace

    def get_by_project(self, project_id: str):
        return self.workspace


def _snapshot():
    return SimpleNamespace(
        version=SimpleNamespace(),
        groups=(
            SimpleNamespace(
                confirmed_group_id="cg1",
                group_key="g1",
                group_label="Group 1",
                sample_quantity_expression="5",
            ),
        ),
        rows=(
            SimpleNamespace(
                confirmed_row_id="cr1",
                test_item="Visual Examination",
                source_section="5.1",
                method="EIA-364",
                condition="Normal",
                requirement="No damage",
                day_expression="2",
            ),
        ),
        cells=(
            SimpleNamespace(
                confirmed_row_id="cr1",
                confirmed_group_id="cg1",
                cell_value="1",
            ),
        ),
    )


class _ConfirmedStore:
    def __init__(self, snapshot) -> None:
        self.snapshot = snapshot

    def get_active_by_project(self, project_id: str):
        return self.snapshot


class _AuthorityMatcher:
    def __init__(self, *, matches: bool) -> None:
        self.matches = matches

    def matches_active_authority(self, project_id: str, request) -> bool:
        return self.matches


class _ExportService:
    def __init__(self, *, content: bytes | None = None) -> None:
        self.content = content

    def export(self, request):
        if self.content is None:
            raise AssertionError("Draft export is not needed during preview")
        return SimpleNamespace(content=self.content, file_name="ignored draft.xlsx")


class _FileGateway:
    def fingerprint(self, path: Path) -> str:
        return "fingerprint"


class _LifecycleGuard:
    def __init__(self) -> None:
        self.calls = []

    def require_write_allowed(self, project_id: str, operation) -> None:
        self.calls.append((project_id, operation))
