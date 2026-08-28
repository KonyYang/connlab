from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from backend.application.matrix_editor_test_record_publication_service import (
    ExecuteMatrixEditorTestRecordPublicationCommand,
    MatrixEditorTestRecordPublicationBlockedError,
    MatrixEditorTestRecordPublicationConflictError,
    MatrixEditorTestRecordPublicationService,
    PreviewMatrixEditorTestRecordPublicationCommand,
)
from backend.domain import ProjectOutputKind, ProjectOutputStatus
from backend.infrastructure.files.test_record_publication_gateway import (
    TestRecordPublicationGateway as PublicationGateway,
)


def test_preview_uses_download_mode_before_official_workspace_exists(tmp_path: Path) -> None:
    service = _service(tmp_path, workspace=None)

    preview = service.preview(
        PreviewMatrixEditorTestRecordPublicationCommand(
            project_id="P1",
            draft_signature="draft-a",
        )
    )

    assert preview.mode == "download"
    assert preview.status == "ready"
    assert preview.target_path is None


def test_preview_uses_download_mode_when_current_matrix_is_not_confirmed(
    tmp_path: Path,
) -> None:
    service = _service(
        tmp_path,
        workspace=_workspace(tmp_path),
        authority_matches=False,
    )

    preview = service.preview(
        PreviewMatrixEditorTestRecordPublicationCommand(
            project_id="P1",
            draft_signature="draft-a",
        )
    )

    assert preview.mode == "download"
    assert preview.status == "ready"
    assert preview.target_path is None


def test_execute_publishes_current_draft_to_test_results_and_registers_output(
    tmp_path: Path,
) -> None:
    workspace = _workspace(tmp_path)
    service = _service(tmp_path, workspace=workspace)
    preview = service.preview(
        PreviewMatrixEditorTestRecordPublicationCommand("P1", "draft-a")
    )

    result = service.execute(
        ExecuteMatrixEditorTestRecordPublicationCommand(
            project_id="P1",
            draft_signature="draft-a",
            preview_token=preview.preview_token,
            conflict_action="none",
            staging_dir=tmp_path / "staging",
            template_path=_template(tmp_path),
            groups=(),
            rows=(),
        )
    )

    target = workspace.official_folder_path / "Test results" / "DL-001 Test Record.docx"
    assert result.target_path == target
    assert target.read_text(encoding="utf-8") == "current Matrix draft"
    assert service._outputs.commands[-1].output_kind is ProjectOutputKind.TEST_RECORD_FORM
    assert service._outputs.commands[-1].status is ProjectOutputStatus.CURRENT
    assert service._outputs.commands[-1].output_path == str(target)
    assert service._outputs.commands[-1].draft_id is None
    assert service._outputs.commands[-1].source_context_signature.startswith(
        "matrix-editor:draft-a|basic-information:v3:"
    )
    assert service._generator.commands[-1].require_confirmed_header is True


def test_existing_file_requires_archive_or_recycle_choice(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path)
    target = workspace.official_folder_path / "Test results" / "DL-001 Test Record.docx"
    target.write_text("old", encoding="utf-8")
    service = _service(tmp_path, workspace=workspace)

    preview = service.preview(
        PreviewMatrixEditorTestRecordPublicationCommand("P1", "draft-a")
    )

    assert preview.status == "conflict"
    assert preview.existing_file is True
    with pytest.raises(MatrixEditorTestRecordPublicationConflictError):
        service.execute(
            ExecuteMatrixEditorTestRecordPublicationCommand(
                project_id="P1",
                draft_signature="draft-a",
                preview_token=preview.preview_token,
                conflict_action="none",
                staging_dir=tmp_path / "staging",
                template_path=_template(tmp_path),
                groups=(),
                rows=(),
            )
        )


def test_archive_moves_old_file_to_workspace_history_before_replacement(
    tmp_path: Path,
) -> None:
    workspace = _workspace(tmp_path)
    target = workspace.official_folder_path / "Test results" / "DL-001 Test Record.docx"
    target.write_text("old", encoding="utf-8")
    service = _service(tmp_path, workspace=workspace)
    preview = service.preview(
        PreviewMatrixEditorTestRecordPublicationCommand("P1", "draft-a")
    )

    result = service.execute(
        ExecuteMatrixEditorTestRecordPublicationCommand(
            project_id="P1",
            draft_signature="draft-a",
            preview_token=preview.preview_token,
            conflict_action="archive",
            staging_dir=tmp_path / "staging",
            template_path=_template(tmp_path),
            groups=(),
            rows=(),
        )
    )

    assert result.archive_path is not None
    assert result.archive_path.parent == workspace.local_workspace_path / "History" / "Test Record"
    assert result.archive_path.read_text(encoding="utf-8") == "old"
    assert target.read_text(encoding="utf-8") == "current Matrix draft"


def test_missing_confirmed_basic_information_blocks_official_publication(
    tmp_path: Path,
) -> None:
    workspace = _workspace(tmp_path)
    service = _service(tmp_path, workspace=workspace, basic_information=None)

    preview = service.preview(
        PreviewMatrixEditorTestRecordPublicationCommand("P1", "draft-a")
    )

    assert preview.status == "blocked"
    assert preview.blockers == (
        "Confirm Basic Information before saving Test Record to the project folder.",
    )
    with pytest.raises(MatrixEditorTestRecordPublicationBlockedError):
        service.execute(
            ExecuteMatrixEditorTestRecordPublicationCommand(
                project_id="P1",
                draft_signature="draft-a",
                preview_token=preview.preview_token,
                conflict_action="none",
                staging_dir=tmp_path / "staging",
                template_path=_template(tmp_path),
                groups=(),
                rows=(),
            )
        )


def test_recorded_workspace_with_missing_official_folder_is_blocked(
    tmp_path: Path,
) -> None:
    workspace = SimpleNamespace(
        project_id="P1",
        dl_number="DL-001",
        local_workspace_path=tmp_path / "DL-001",
        official_folder_path=tmp_path / "DL-001" / "missing official folder",
    )
    service = _service(tmp_path, workspace=workspace)

    preview = service.preview(
        PreviewMatrixEditorTestRecordPublicationCommand("P1", "draft-a")
    )

    assert preview.mode == "official"
    assert preview.status == "blocked"
    assert "missing" in preview.blockers[0].lower()


def test_basic_information_dl_must_match_official_workspace(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path)
    basic_information = SimpleNamespace(
        version=4,
        source_signature_hash="changed-dl",
        values={
            "dl_number": "DL-002",
            "product_description": "Connector",
            "applicable_specifications": "GS-001",
        },
    )
    service = _service(
        tmp_path,
        workspace=workspace,
        basic_information=basic_information,
    )

    preview = service.preview(
        PreviewMatrixEditorTestRecordPublicationCommand("P1", "draft-a")
    )

    assert preview.status == "blocked"
    assert "DL-002" in preview.blockers[0]
    assert "DL-001" in preview.blockers[0]


def test_execute_rejects_stale_preview_when_existing_file_changes(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path)
    target = workspace.official_folder_path / "Test results" / "DL-001 Test Record.docx"
    target.write_text("old", encoding="utf-8")
    service = _service(tmp_path, workspace=workspace)
    preview = service.preview(
        PreviewMatrixEditorTestRecordPublicationCommand("P1", "draft-a")
    )
    target.write_text("operator edit after preview", encoding="utf-8")

    with pytest.raises(MatrixEditorTestRecordPublicationConflictError, match="changed"):
        service.execute(
            ExecuteMatrixEditorTestRecordPublicationCommand(
                project_id="P1",
                draft_signature="draft-a",
                preview_token=preview.preview_token,
                conflict_action="archive",
                staging_dir=tmp_path / "staging",
                template_path=_template(tmp_path),
                groups=(),
                rows=(),
            )
        )


def test_recycle_failure_preserves_existing_target(tmp_path: Path) -> None:
    target = tmp_path / "DL-001 Test Record.docx"
    target.write_text("old", encoding="utf-8")
    staged = tmp_path / "staged.docx"
    staged.write_text("new", encoding="utf-8")

    def fail_recycle(path: Path) -> None:
        raise OSError("Recycle Bin unavailable")

    gateway = PublicationGateway(recycle_file=fail_recycle)

    with pytest.raises(OSError, match="unavailable"):
        gateway.publish(
            staged_path=staged,
            target_path=target,
            conflict_action="recycle",
            history_dir=tmp_path / "History",
            expected_target_fingerprint=gateway.fingerprint(target),
        )

    assert target.read_text(encoding="utf-8") == "old"


def test_recycle_success_places_new_file_after_old_file_is_recycled(
    tmp_path: Path,
) -> None:
    target = tmp_path / "DL-001 Test Record.docx"
    target.write_text("old", encoding="utf-8")
    staged = tmp_path / "staged.docx"
    staged.write_text("new", encoding="utf-8")
    recycled = tmp_path / "recycled.docx"

    gateway = PublicationGateway(
        recycle_file=lambda path: path.replace(recycled)
    )
    gateway.publish(
        staged_path=staged,
        target_path=target,
        conflict_action="recycle",
        history_dir=tmp_path / "History",
        expected_target_fingerprint=gateway.fingerprint(target),
    )

    assert recycled.read_text(encoding="utf-8") == "old"
    assert target.read_text(encoding="utf-8") == "new"


def _workspace(tmp_path: Path):
    local = tmp_path / "DL-001"
    official = local / "DL-001 Connector Qualification test"
    (official / "Test results").mkdir(parents=True)
    return SimpleNamespace(
        project_id="P1",
        dl_number="DL-001",
        local_workspace_path=local,
        official_folder_path=official,
    )


def _template(tmp_path: Path) -> Path:
    path = tmp_path / "template.docx"
    path.write_bytes(b"template")
    return path


def _service(
    tmp_path: Path,
    *,
    workspace,
    basic_information=...,
    authority_matches: bool = True,
) -> MatrixEditorTestRecordPublicationService:
    if basic_information is ...:
        basic_information = SimpleNamespace(
            version=3,
            source_signature_hash="basic-info-hash",
            values={
                "dl_number": "DL-001",
                "product_description": "Connector",
                "applicable_specifications": "GS-001",
            },
        )
    generator = _Generator()
    outputs = _Outputs()
    service = MatrixEditorTestRecordPublicationService(
        workspace_store=_WorkspaceStore(workspace),
        authority_matcher=_AuthorityMatcher(authority_matches),
        basic_information_reader=_BasicInformationReader(basic_information),
        document_generation_service=generator,
        file_gateway=_FileGateway(),
        output_service=outputs,
    )
    service._generator = generator
    service._outputs = outputs
    return service


class _AuthorityMatcher:
    def __init__(self, matches: bool) -> None:
        self.matches = matches

    def matches_active_authority(self, project_id: str, draft_signature: str) -> bool:
        return self.matches


class _WorkspaceStore:
    def __init__(self, workspace) -> None:
        self.workspace = workspace

    def get_by_project(self, project_id: str):
        return self.workspace


class _BasicInformationReader:
    def __init__(self, snapshot) -> None:
        self.snapshot = snapshot

    def get_latest_confirmed(self, project_id: str):
        return self.snapshot


class _Generator:
    def __init__(self) -> None:
        self.commands = []

    def generate(self, command):
        self.commands.append(command)
        command.output_dir.mkdir(parents=True, exist_ok=True)
        path = command.output_dir / "staged.docx"
        path.write_text("current Matrix draft", encoding="utf-8")
        return SimpleNamespace(output_path=path)


class _FileGateway:
    def fingerprint(self, path: Path) -> str:
        import hashlib

        return hashlib.sha256(path.read_bytes()).hexdigest()

    def publish(
        self,
        *,
        staged_path: Path,
        target_path: Path,
        conflict_action: str,
        history_dir: Path,
        expected_target_fingerprint: str | None,
    ) -> Path | None:
        archive_path = None
        if target_path.exists():
            assert self.fingerprint(target_path) == expected_target_fingerprint
            if conflict_action == "archive":
                history_dir.mkdir(parents=True, exist_ok=True)
                archive_path = history_dir / "DL-001 Test Record_20260828-120000.docx"
                target_path.replace(archive_path)
            elif conflict_action == "recycle":
                target_path.unlink()
        staged_path.replace(target_path)
        return archive_path


class _Outputs:
    def __init__(self) -> None:
        self.commands = []

    def get_status_summary(self, project_id: str):
        return SimpleNamespace(active_draft_id=None)

    def register_output(self, command):
        self.commands.append(command)
        return command
