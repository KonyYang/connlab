"""Preview and execute controlled encryption for official project files."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Literal, Protocol

from backend.application.official_project_workspace_service import OfficialWorkspaceRecord
from backend.modules.ltr import LtrNumberError, excel_password_for_dl_number
from backend.shared.office_document_password import OFFICE_DOCUMENT_PASSWORD


ConflictAction = Literal["overwrite", "skip"]
FileLocation = Literal["official_root", "test_results"]
OfficeKind = Literal["word", "excel", "powerpoint"]
EncryptionMode = Literal["replace_in_place", "secured_copy"]

_ROOT_FILE_KINDS: dict[str, OfficeKind] = {
    ".doc": "word",
    ".docx": "word",
    ".pptx": "powerpoint",
}
_TEST_RESULTS_FILE_KINDS: dict[str, OfficeKind] = {
    **_ROOT_FILE_KINDS,
    ".xls": "excel",
    ".xlsx": "excel",
}


class ProjectFileEncryptionError(RuntimeError):
    """Base error for controlled project-file encryption."""


class ProjectFileEncryptionWorkspaceNotFoundError(ProjectFileEncryptionError):
    """Raised when the project has no trusted local official workspace."""


class ProjectFileEncryptionPlanStaleError(ProjectFileEncryptionError):
    """Raised when files changed after preview and before execution."""


class ProjectFileEncryptionBlockedError(ProjectFileEncryptionError):
    """Raised when a blocked preview is submitted for execution."""


class OfficialWorkspaceRepositoryPort(Protocol):
    """Workspace lookup required by the encryption service."""

    def get_by_project(self, project_id: str) -> OfficialWorkspaceRecord | None:
        """Return the project workspace record when it exists."""


class ProjectFileEncryptionGatewayPort(Protocol):
    """Transactional file-mutation boundary used by the service."""

    def encrypt(
        self,
        *,
        item: "ProjectFileEncryptionPlanItem",
        password: str,
        history_root: Path,
        overwrite: bool,
    ) -> Path:
        """Encrypt one planned item and return its final path."""


@dataclass(frozen=True, slots=True)
class ProjectFileEncryptionPlanItem:
    """One backend-resolved file mutation in an encryption plan."""

    source_path: Path
    target_path: Path
    file_name: str
    location: FileLocation
    office_kind: OfficeKind
    mode: EncryptionMode
    conflict: bool
    source_fingerprint: str
    target_fingerprint: str | None


@dataclass(frozen=True, slots=True)
class ProjectFileEncryptionPreview:
    """Safe preview exposed to API consumers."""

    project_id: str
    status: Literal["ready", "conflict", "empty", "blocked"]
    plan_token: str
    items: tuple[ProjectFileEncryptionPlanItem, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]

    @property
    def conflict_count(self) -> int:
        return sum(1 for item in self.items if item.conflict)


@dataclass(frozen=True, slots=True)
class ProjectFileEncryptionCommand:
    """Execute a previously previewed project-file encryption plan."""

    project_id: str
    expected_plan_token: str
    conflict_action: ConflictAction


@dataclass(frozen=True, slots=True)
class ProjectFileEncryptionItemResult:
    """Observable outcome for one preview item."""

    file_name: str
    location: FileLocation
    status: Literal["encrypted", "skipped", "failed"]
    message: str


@dataclass(frozen=True, slots=True)
class ProjectFileEncryptionResult:
    """Batch execution result; one Office failure does not hide other outcomes."""

    project_id: str
    encrypted_count: int
    skipped_count: int
    failed_count: int
    items: tuple[ProjectFileEncryptionItemResult, ...]


class ProjectFileEncryptionService:
    """Own file selection, trusted paths, password policy, and stale-plan checks."""

    def __init__(
        self,
        *,
        workspace_repository: OfficialWorkspaceRepositoryPort,
        gateway: ProjectFileEncryptionGatewayPort,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        self._workspace_repository = workspace_repository
        self._gateway = gateway
        self._now = now or datetime.now

    def preview(self, project_id: str) -> ProjectFileEncryptionPreview:
        """Build a nonrecursive plan from the trusted official workspace record."""
        workspace = self._workspace(project_id)
        blockers = self._validate_workspace(workspace)
        if blockers:
            return ProjectFileEncryptionPreview(
                project_id=project_id,
                status="blocked",
                plan_token=_plan_token((), blockers),
                items=(),
                blockers=blockers,
                warnings=(),
            )

        official = workspace.official_folder_path.resolve()
        results = (official / "Test results").resolve()
        items = tuple(
            sorted(
                (
                    *self._scan_layer(
                        official,
                        location="official_root",
                        file_kinds=_ROOT_FILE_KINDS,
                    ),
                    *self._scan_layer(
                        results,
                        location="test_results",
                        file_kinds=_TEST_RESULTS_FILE_KINDS,
                    ),
                ),
                key=lambda item: (item.location, item.file_name.casefold()),
            )
        )
        status: Literal["ready", "conflict", "empty", "blocked"]
        if not items:
            status = "empty"
        elif any(item.conflict for item in items):
            status = "conflict"
        else:
            status = "ready"
        return ProjectFileEncryptionPreview(
            project_id=project_id,
            status=status,
            plan_token=_plan_token(items, ()),
            items=items,
            blockers=(),
            warnings=(
                "Only the official folder root and Test results current layer are scanned; subfolders are not processed.",
            ),
        )

    def execute(self, command: ProjectFileEncryptionCommand) -> ProjectFileEncryptionResult:
        """Execute an unchanged preview using one timestamped History location."""
        if command.conflict_action not in {"overwrite", "skip"}:
            raise ValueError("conflict_action must be 'overwrite' or 'skip'.")
        preview = self.preview(command.project_id)
        if preview.status == "blocked":
            raise ProjectFileEncryptionBlockedError(preview.blockers[0])
        if preview.plan_token != command.expected_plan_token:
            raise ProjectFileEncryptionPlanStaleError(
                "Project files changed after preview. Preview the encryption plan again."
            )
        workspace = self._workspace(command.project_id)
        timestamp = self._now().strftime("%Y%m%d%H%M%S%f")
        history_root = (
            workspace.local_workspace_path
            / "History"
            / "Encryption"
            / timestamp
            / "Test results"
        )
        excel_password = _derive_excel_password(workspace.dl_number)
        outcomes: list[ProjectFileEncryptionItemResult] = []
        for item in preview.items:
            if item.conflict and command.conflict_action == "skip":
                outcomes.append(
                    ProjectFileEncryptionItemResult(
                        file_name=item.file_name,
                        location=item.location,
                        status="skipped",
                        message="Existing secured file was kept; source was not changed.",
                    )
                )
                continue
            if not _item_matches_preview(item):
                outcomes.append(
                    ProjectFileEncryptionItemResult(
                        file_name=item.file_name,
                        location=item.location,
                        status="failed",
                        message="The file changed during encryption; it was left unchanged. Preview again.",
                    )
                )
                continue
            password = (
                excel_password
                if item.office_kind == "excel"
                else OFFICE_DOCUMENT_PASSWORD
            )
            try:
                self._gateway.encrypt(
                    item=item,
                    password=password,
                    history_root=history_root,
                    overwrite=command.conflict_action == "overwrite",
                )
            except Exception as exc:
                outcomes.append(
                    ProjectFileEncryptionItemResult(
                        file_name=item.file_name,
                        location=item.location,
                        status="failed",
                        message=_safe_error_message(exc),
                    )
                )
            else:
                outcomes.append(
                    ProjectFileEncryptionItemResult(
                        file_name=item.file_name,
                        location=item.location,
                        status="encrypted",
                        message="Encrypted successfully.",
                    )
                )
        return ProjectFileEncryptionResult(
            project_id=command.project_id,
            encrypted_count=sum(item.status == "encrypted" for item in outcomes),
            skipped_count=sum(item.status == "skipped" for item in outcomes),
            failed_count=sum(item.status == "failed" for item in outcomes),
            items=tuple(outcomes),
        )

    def _workspace(self, project_id: str) -> OfficialWorkspaceRecord:
        workspace = self._workspace_repository.get_by_project(project_id)
        if workspace is None:
            raise ProjectFileEncryptionWorkspaceNotFoundError(
                "Create the local project folder before encrypting project files."
            )
        return workspace

    def _validate_workspace(self, workspace: OfficialWorkspaceRecord) -> tuple[str, ...]:
        local = workspace.local_workspace_path.resolve()
        official = workspace.official_folder_path.resolve()
        if official == local or not official.is_relative_to(local):
            return ("The indexed official project folder is outside the trusted local workspace.",)
        if not official.is_dir():
            return ("The indexed official project folder is missing.",)
        if not (official / "Test results").is_dir():
            return ("The official project folder is missing its Test results folder.",)
        return ()

    def _scan_layer(
        self,
        directory: Path,
        *,
        location: FileLocation,
        file_kinds: dict[str, OfficeKind],
    ) -> tuple[ProjectFileEncryptionPlanItem, ...]:
        items: list[ProjectFileEncryptionPlanItem] = []
        for source in directory.iterdir():
            suffix = source.suffix.lower()
            if (
                not source.is_file()
                or source.is_symlink()
                or source.name.startswith("~$")
                or source.stem.casefold().endswith("_secured")
                or suffix not in file_kinds
            ):
                continue
            if location == "official_root":
                target = source
                mode: EncryptionMode = "replace_in_place"
            else:
                target = source.with_name(f"{source.stem}_Secured{source.suffix}")
                mode = "secured_copy"
            target_fingerprint = (
                _file_fingerprint(target)
                if target != source and target.is_file()
                else None
            )
            items.append(
                ProjectFileEncryptionPlanItem(
                    source_path=source,
                    target_path=target,
                    file_name=source.name,
                    location=location,
                    office_kind=file_kinds[suffix],
                    mode=mode,
                    conflict=target_fingerprint is not None,
                    source_fingerprint=_file_fingerprint(source),
                    target_fingerprint=target_fingerprint,
                )
            )
        return tuple(items)


def _derive_excel_password(dl_number: str) -> str:
    try:
        return excel_password_for_dl_number(dl_number)
    except LtrNumberError as exc:
        raise ProjectFileEncryptionBlockedError(
            "The project DL number cannot be converted to the Excel password format."
        ) from exc


def _file_fingerprint(path: Path) -> str:
    stat = path.stat()
    digest = hashlib.sha256()
    digest.update(path.name.encode("utf-8"))
    digest.update(str(stat.st_size).encode("ascii"))
    digest.update(str(stat.st_mtime_ns).encode("ascii"))
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _plan_token(
    items: tuple[ProjectFileEncryptionPlanItem, ...],
    blockers: tuple[str, ...],
) -> str:
    payload = {
        "blockers": blockers,
        "items": [
            {
                "location": item.location,
                "name": item.file_name,
                "kind": item.office_kind,
                "mode": item.mode,
                "source": item.source_fingerprint,
                "target": item.target_fingerprint,
            }
            for item in items
        ],
    }
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _safe_error_message(exc: Exception) -> str:
    del exc
    return (
        "Encryption failed; the source file was kept unchanged. "
        "Close the file in Microsoft Office and try again."
    )


def _item_matches_preview(item: ProjectFileEncryptionPlanItem) -> bool:
    if not item.source_path.is_file() or item.source_path.is_symlink():
        return False
    if _file_fingerprint(item.source_path) != item.source_fingerprint:
        return False
    if item.target_path == item.source_path:
        return True
    if item.target_fingerprint is None:
        return not item.target_path.exists()
    return (
        item.target_path.is_file()
        and not item.target_path.is_symlink()
        and _file_fingerprint(item.target_path) == item.target_fingerprint
    )
