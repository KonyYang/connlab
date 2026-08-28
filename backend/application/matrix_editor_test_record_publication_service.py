"""Preview and publish a current-state Matrix Editor Test Record safely."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Protocol
from uuid import uuid4

from backend.application.matrix_editor_test_record_document_generation_service import (
    GenerateMatrixEditorTestRecordDocumentCommand,
    MatrixEditorTestRecordGroupInput,
    MatrixEditorTestRecordRowInput,
)
from backend.application.project_basic_information_output import (
    ConfirmedBasicInformationReader,
)
from backend.application.project_basic_information_output_identity import (
    test_record_header_identity,
)
from backend.application.project_output_record_service import (
    RegisterProjectOutputCommand,
)
from backend.application.project_lifecycle_write_guard import (
    LifecycleWriteOperation,
    ProjectLifecycleWriteGuard,
)
from backend.domain import (
    ProjectOutputKind,
    ProjectOutputSource,
    ProjectOutputStatus,
)


class MatrixEditorTestRecordPublicationError(ValueError):
    """Base error for direct Test Record publication."""


class MatrixEditorTestRecordPublicationBlockedError(
    MatrixEditorTestRecordPublicationError
):
    """Raised when authoritative prerequisites are missing."""


class MatrixEditorTestRecordPublicationConflictError(
    MatrixEditorTestRecordPublicationError
):
    """Raised when a conflict choice or preview is no longer valid."""


class OfficialWorkspaceLookup(Protocol):
    def get_by_project(self, project_id: str):
        """Return the official workspace record when it exists."""


class MatrixEditorTestRecordAuthorityMatcher(Protocol):
    def matches_active_authority(
        self, project_id: str, draft_signature: str
    ) -> bool:
        """Return whether the current Test Record payload matches Matrix authority."""


class MatrixEditorTestRecordGenerator(Protocol):
    def generate(self, command: GenerateMatrixEditorTestRecordDocumentCommand):
        """Generate a staged Test Record and return its output path."""


class TestRecordPublicationFileGateway(Protocol):
    def fingerprint(self, path: Path) -> str:
        """Return a stable file fingerprint."""

    def publish(
        self,
        *,
        staged_path: Path,
        target_path: Path,
        conflict_action: str,
        history_dir: Path,
        expected_target_fingerprint: str | None,
    ) -> Path | None:
        """Place the staged file and return an archive path when one was created."""


class ProjectOutputService(Protocol):
    def register_output(self, command: RegisterProjectOutputCommand):
        """Persist one output lineage record."""


@dataclass(frozen=True, slots=True)
class PreviewMatrixEditorTestRecordPublicationCommand:
    project_id: str
    draft_signature: str


@dataclass(frozen=True, slots=True)
class ExecuteMatrixEditorTestRecordPublicationCommand:
    project_id: str
    draft_signature: str
    preview_token: str
    conflict_action: str
    staging_dir: Path
    template_path: Path
    groups: tuple[MatrixEditorTestRecordGroupInput, ...]
    rows: tuple[MatrixEditorTestRecordRowInput, ...]


@dataclass(frozen=True, slots=True)
class MatrixEditorTestRecordPublicationPreview:
    project_id: str
    mode: str
    status: str
    target_path: Path | None
    target_fingerprint: str | None
    existing_file: bool
    existing_modified_at: str | None
    blockers: tuple[str, ...]
    preview_token: str
    confirmed_basic_information_version: int | None
    confirmed_basic_information_source_signature_hash: str | None


@dataclass(frozen=True, slots=True)
class MatrixEditorTestRecordPublicationResult:
    project_id: str
    target_path: Path
    archive_path: Path | None
    file_name: str


class MatrixEditorTestRecordPublicationService:
    """Keep direct Test Record publication narrow, previewed, and recoverable."""

    def __init__(
        self,
        *,
        workspace_store: OfficialWorkspaceLookup,
        authority_matcher: MatrixEditorTestRecordAuthorityMatcher,
        basic_information_reader: ConfirmedBasicInformationReader,
        document_generation_service: MatrixEditorTestRecordGenerator,
        file_gateway: TestRecordPublicationFileGateway,
        output_service: ProjectOutputService,
        lifecycle_write_guard: ProjectLifecycleWriteGuard | None = None,
    ) -> None:
        self._workspaces = workspace_store
        self._authority_matcher = authority_matcher
        self._basic_information = basic_information_reader
        self._generator = document_generation_service
        self._files = file_gateway
        self._outputs = output_service
        self._lifecycle_write_guard = lifecycle_write_guard

    def preview(
        self, command: PreviewMatrixEditorTestRecordPublicationCommand
    ) -> MatrixEditorTestRecordPublicationPreview:
        workspace = self._workspaces.get_by_project(command.project_id)
        if workspace is None:
            return self._preview_result(
                command=command,
                mode="download",
                status="ready",
                target_path=None,
                target_fingerprint=None,
                existing_modified_at=None,
                blockers=(),
                basic_information=None,
            )
        if not self._authority_matcher.matches_active_authority(
            command.project_id, command.draft_signature
        ):
            return self._preview_result(
                command=command,
                mode="download",
                status="ready",
                target_path=None,
                target_fingerprint=None,
                existing_modified_at=None,
                blockers=(),
                basic_information=None,
            )
        if not Path(workspace.official_folder_path).is_dir():
            return self._preview_result(
                command=command,
                mode="official",
                status="blocked",
                target_path=Path(workspace.official_folder_path),
                target_fingerprint=None,
                existing_modified_at=None,
                blockers=(
                    f"The recorded official project folder is missing: {workspace.official_folder_path}",
                ),
                basic_information=None,
            )

        test_results = Path(workspace.official_folder_path) / "Test results"
        if not test_results.is_dir():
            return self._preview_result(
                command=command,
                mode="official",
                status="blocked",
                target_path=test_results,
                target_fingerprint=None,
                existing_modified_at=None,
                blockers=("The official project folder is missing the Test results folder.",),
                basic_information=None,
            )

        basic_information = self._basic_information.get_latest_confirmed(
            command.project_id
        )
        if basic_information is None:
            return self._preview_result(
                command=command,
                mode="official",
                status="blocked",
                target_path=None,
                target_fingerprint=None,
                existing_modified_at=None,
                blockers=(
                    "Confirm Basic Information before saving Test Record to the project folder.",
                ),
                basic_information=None,
            )
        identity = test_record_header_identity(basic_information)
        missing = []
        if not identity.lab_test_request_number.strip():
            missing.append("DL/LTR Number")
        if not identity.product_description.strip():
            missing.append("Product Description")
        if missing:
            return self._preview_result(
                command=command,
                mode="official",
                status="blocked",
                target_path=None,
                target_fingerprint=None,
                existing_modified_at=None,
                blockers=(
                    "Confirm Basic Information before saving Test Record: "
                    + ", ".join(missing)
                    + " is missing.",
                ),
                basic_information=basic_information,
            )
        workspace_dl = str(getattr(workspace, "dl_number", "") or "").strip()
        if workspace_dl and identity.lab_test_request_number.strip() != workspace_dl:
            return self._preview_result(
                command=command,
                mode="official",
                status="blocked",
                target_path=None,
                target_fingerprint=None,
                existing_modified_at=None,
                blockers=(
                    "Confirmed Basic Information DL/LTR Number "
                    f"{identity.lab_test_request_number.strip()} does not match the "
                    f"official workspace {workspace_dl}. Update the project folder identity first.",
                ),
                basic_information=basic_information,
            )

        file_name = f"{_safe_file_stem(identity.lab_test_request_number)} Test Record.docx"
        target = test_results / file_name
        if target.exists() and not target.is_file():
            return self._preview_result(
                command=command,
                mode="official",
                status="blocked",
                target_path=target,
                target_fingerprint=None,
                existing_modified_at=None,
                blockers=(f"Test Record target is not a file: {target}",),
                basic_information=basic_information,
            )
        fingerprint = self._files.fingerprint(target) if target.is_file() else None
        modified_at = _modified_timestamp(target) if target.is_file() else None
        return self._preview_result(
            command=command,
            mode="official",
            status="conflict" if fingerprint is not None else "ready",
            target_path=target,
            target_fingerprint=fingerprint,
            existing_modified_at=modified_at,
            blockers=(),
            basic_information=basic_information,
        )

    def execute(
        self, command: ExecuteMatrixEditorTestRecordPublicationCommand
    ) -> MatrixEditorTestRecordPublicationResult:
        if self._lifecycle_write_guard is not None:
            self._lifecycle_write_guard.require_write_allowed(
                command.project_id,
                LifecycleWriteOperation.REQUIRED_FORMS_GENERATE,
            )
        current = self.preview(
            PreviewMatrixEditorTestRecordPublicationCommand(
                project_id=command.project_id,
                draft_signature=command.draft_signature,
            )
        )
        if current.preview_token != command.preview_token:
            raise MatrixEditorTestRecordPublicationConflictError(
                "Test Record target or authority changed after preview. Try again."
            )
        if current.status == "blocked":
            raise MatrixEditorTestRecordPublicationBlockedError(current.blockers[0])
        if current.mode != "official" or current.target_path is None:
            raise MatrixEditorTestRecordPublicationBlockedError(
                "Create the project folder before publishing Test Record directly."
            )
        action = command.conflict_action.strip().lower()
        if current.existing_file and action not in {"archive", "recycle"}:
            raise MatrixEditorTestRecordPublicationConflictError(
                "Choose Archive old file, Move old file to Recycle Bin, or Cancel."
            )
        if not current.existing_file and action != "none":
            raise MatrixEditorTestRecordPublicationConflictError(
                "The Test Record conflict no longer exists. Try again."
            )

        operation_dir = Path(command.staging_dir) / uuid4().hex
        staged_path: Path | None = None
        try:
            generated = self._generator.generate(
                GenerateMatrixEditorTestRecordDocumentCommand(
                    project_id=command.project_id,
                    output_dir=operation_dir,
                    template_path=Path(command.template_path),
                    groups=command.groups,
                    rows=command.rows,
                    require_confirmed_header=True,
                    output_file_name=current.target_path.name,
                )
            )
            staged_path = Path(generated.output_path)
            workspace = self._workspaces.get_by_project(command.project_id)
            if workspace is None:
                raise MatrixEditorTestRecordPublicationConflictError(
                    "Project workspace changed after preview. Try again."
                )
            output_hash = self._files.fingerprint(staged_path)
            self._outputs.register_output(
                RegisterProjectOutputCommand(
                    project_id=command.project_id,
                    output_kind=ProjectOutputKind.TEST_RECORD_FORM,
                    status=ProjectOutputStatus.CURRENT,
                    source=ProjectOutputSource.SYSTEM_GENERATED,
                    output_path=str(current.target_path),
                    draft_id=None,
                    output_sha256=output_hash,
                    output_size_bytes=staged_path.stat().st_size,
                    source_context_signature=_source_context_signature(
                        command.draft_signature,
                        current.confirmed_basic_information_version,
                        current.confirmed_basic_information_source_signature_hash,
                    ),
                    note="Published from current Matrix Editor UI state.",
                )
            )
            archive_path = self._files.publish(
                staged_path=staged_path,
                target_path=current.target_path,
                conflict_action=action,
                history_dir=(
                    Path(workspace.local_workspace_path) / "History" / "Test Record"
                ),
                expected_target_fingerprint=current.target_fingerprint,
            )
        finally:
            if staged_path is not None and staged_path.exists():
                staged_path.unlink()
            if operation_dir.is_dir() and not any(operation_dir.iterdir()):
                operation_dir.rmdir()
        return MatrixEditorTestRecordPublicationResult(
            project_id=command.project_id,
            target_path=current.target_path,
            archive_path=archive_path,
            file_name=current.target_path.name,
        )

    def _preview_result(
        self,
        *,
        command: PreviewMatrixEditorTestRecordPublicationCommand,
        mode: str,
        status: str,
        target_path: Path | None,
        target_fingerprint: str | None,
        existing_modified_at: str | None,
        blockers: tuple[str, ...],
        basic_information,
    ) -> MatrixEditorTestRecordPublicationPreview:
        version = getattr(basic_information, "version", None)
        source_hash = getattr(basic_information, "source_signature_hash", None)
        payload = {
            "project_id": command.project_id,
            "draft_signature": command.draft_signature,
            "mode": mode,
            "status": status,
            "target_path": str(target_path) if target_path is not None else None,
            "target_fingerprint": target_fingerprint,
            "basic_information_version": version,
            "basic_information_source_hash": source_hash,
            "blockers": list(blockers),
        }
        token = sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        return MatrixEditorTestRecordPublicationPreview(
            project_id=command.project_id,
            mode=mode,
            status=status,
            target_path=target_path,
            target_fingerprint=target_fingerprint,
            existing_file=target_fingerprint is not None,
            existing_modified_at=existing_modified_at,
            blockers=blockers,
            preview_token=token,
            confirmed_basic_information_version=version,
            confirmed_basic_information_source_signature_hash=source_hash,
        )


def _safe_file_stem(value: str) -> str:
    return value.replace("/", "_").replace("\\", "_").strip() or "project"


def _modified_timestamp(path: Path) -> str:
    from datetime import datetime

    return datetime.fromtimestamp(path.stat().st_mtime).astimezone().isoformat()


def _source_context_signature(
    draft_signature: str,
    basic_information_version: int | None,
    basic_information_source_hash: str | None,
) -> str:
    return (
        f"matrix-editor:{draft_signature}|basic-information:"
        f"v{basic_information_version or 0}:{basic_information_source_hash or '-'}"
    )
