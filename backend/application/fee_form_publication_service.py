"""Draft-or-official Fee Form publication from the Fee Evaluation page."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Protocol
from uuid import uuid4

from backend.application.confirmed_fee_pricing_snapshot import (
    edited_values_json_from_confirmed_fee_snapshot,
)
from backend.application.fee_evaluation_edited_export_values import (
    FeeEvaluationEditedExportValues,
)
from backend.application.fee_evaluation_pricing_draft_serialization import (
    edited_values_from_json,
)
from backend.application.project_basic_information_output import (
    ConfirmedBasicInformationReader,
)
from backend.application.project_basic_information_output_identity import fee_form_identity
from backend.application.project_lifecycle_write_guard import (
    LifecycleWriteOperation,
    ProjectLifecycleWriteGuard,
)
from backend.application.project_output_record_service import RegisterProjectOutputCommand
from backend.domain import ProjectOutputKind, ProjectOutputSource, ProjectOutputStatus


class FeeFormPublicationError(ValueError):
    """Base error for direct Fee Form publication."""


class FeeFormPublicationBlockedError(FeeFormPublicationError):
    """Raised when official publication prerequisites are missing."""


class FeeFormPublicationConflictError(FeeFormPublicationError):
    """Raised when the target changes after preview."""


class WorkspaceLookup(Protocol):
    def get_by_project(self, project_id: str): ...


class ConfirmedFeeReader(Protocol):
    def get_latest(self, project_id: str): ...


class FeeFormGenerator(Protocol):
    def generate(
        self,
        *,
        project_id: str,
        output_dir: Path,
        output_file_name: str,
        confirmed_fee: object,
        basic_information: object,
    ) -> Path: ...


class PublicationFileGateway(Protocol):
    def fingerprint(self, path: Path) -> str: ...

    def publish(
        self,
        *,
        staged_path: Path,
        target_path: Path,
        conflict_action: str,
        history_dir: Path,
        expected_target_fingerprint: str | None,
    ) -> Path | None: ...


class OutputService(Protocol):
    def register_output(self, command: RegisterProjectOutputCommand): ...


@dataclass(frozen=True, slots=True)
class PreviewFeeFormPublicationCommand:
    project_id: str
    current_values: FeeEvaluationEditedExportValues


@dataclass(frozen=True, slots=True)
class ExecuteFeeFormPublicationCommand:
    project_id: str
    current_values: FeeEvaluationEditedExportValues
    preview_token: str
    conflict_action: str
    staging_dir: Path


@dataclass(frozen=True, slots=True)
class FeeFormPublicationPreview:
    project_id: str
    mode: str
    status: str
    target_path: Path | None
    target_fingerprint: str | None
    existing_file: bool
    existing_modified_at: str | None
    blockers: tuple[str, ...]
    preview_token: str


@dataclass(frozen=True, slots=True)
class FeeFormPublicationResult:
    project_id: str
    target_path: Path
    archive_path: Path | None
    file_name: str


class FeeFormPublicationService:
    """Publish only a Fee Form whose page values equal current confirmed Fee."""

    def __init__(
        self,
        *,
        workspace_store: WorkspaceLookup,
        confirmed_fee_reader: ConfirmedFeeReader,
        basic_information_reader: ConfirmedBasicInformationReader,
        generator: FeeFormGenerator,
        file_gateway: PublicationFileGateway,
        output_service: OutputService,
        lifecycle_write_guard: ProjectLifecycleWriteGuard | None = None,
    ) -> None:
        self._workspaces = workspace_store
        self._fees = confirmed_fee_reader
        self._basic_information = basic_information_reader
        self._generator = generator
        self._files = file_gateway
        self._outputs = output_service
        self._lifecycle_write_guard = lifecycle_write_guard

    def preview(self, command: PreviewFeeFormPublicationCommand) -> FeeFormPublicationPreview:
        workspace = self._workspaces.get_by_project(command.project_id)
        if workspace is None:
            return self._preview(command, mode="download")
        fee_result = self._fees.get_latest(command.project_id)
        fee = getattr(fee_result, "latest_confirmed_fee", None)
        if getattr(fee_result, "status", None) != "current" or fee is None:
            return self._preview(command, mode="download")
        try:
            confirmed_values = edited_values_from_json(
                edited_values_json_from_confirmed_fee_snapshot(
                    str(getattr(fee, "pricing_snapshot_json"))
                )
            )
        except (AttributeError, KeyError, TypeError, ValueError):
            return self._preview(command, mode="download")
        if confirmed_values != command.current_values:
            return self._preview(command, mode="download")

        official = Path(workspace.official_folder_path)
        if not official.is_dir():
            return self._preview(
                command,
                mode="official",
                status="blocked",
                blockers=("The recorded official project folder is missing.",),
            )
        basic = self._basic_information.get_latest_confirmed(command.project_id)
        if basic is None:
            return self._preview(
                command,
                mode="official",
                status="blocked",
                blockers=("Confirm Basic Information before saving Fee Form.",),
            )
        identity = fee_form_identity(basic)
        dl_number = identity.dl_number.strip()
        if not dl_number:
            return self._preview(
                command,
                mode="official",
                status="blocked",
                blockers=("Confirmed Basic Information is missing DL/LTR Number.",),
            )
        workspace_dl = str(getattr(workspace, "dl_number", "") or "").strip()
        if workspace_dl and workspace_dl != dl_number:
            return self._preview(
                command,
                mode="official",
                status="blocked",
                blockers=("Confirmed Basic Information does not match the project folder.",),
            )
        target = official / f"{_safe_file_stem(dl_number)} Fee Form.xls"
        fingerprint = self._files.fingerprint(target) if target.is_file() else None
        modified_at = (
            datetime.fromtimestamp(target.stat().st_mtime).astimezone().isoformat()
            if fingerprint is not None
            else None
        )
        return self._preview(
            command,
            mode="official",
            status="conflict" if fingerprint else "ready",
            target_path=target,
            target_fingerprint=fingerprint,
            existing_modified_at=modified_at,
            basic_information=basic,
            confirmed_fee=fee,
        )

    def execute(self, command: ExecuteFeeFormPublicationCommand) -> FeeFormPublicationResult:
        if self._lifecycle_write_guard is not None:
            self._lifecycle_write_guard.require_write_allowed(
                command.project_id, LifecycleWriteOperation.REQUIRED_FORMS_GENERATE
            )
        current = self.preview(
            PreviewFeeFormPublicationCommand(command.project_id, command.current_values)
        )
        if current.preview_token != command.preview_token:
            raise FeeFormPublicationConflictError(
                "Fee Form target or authority changed after preview. Try again."
            )
        if current.mode != "official" or current.target_path is None:
            raise FeeFormPublicationBlockedError(
                "Update Fee before publishing an official Fee Form."
            )
        if current.status == "blocked":
            raise FeeFormPublicationBlockedError(current.blockers[0])
        action = command.conflict_action.strip().lower()
        if current.existing_file and action not in {"archive", "recycle"}:
            raise FeeFormPublicationConflictError(
                "Choose Archive old file, Move old file to Recycle Bin, or Cancel."
            )
        if not current.existing_file and action != "none":
            raise FeeFormPublicationConflictError("The Fee Form conflict no longer exists.")

        workspace = self._workspaces.get_by_project(command.project_id)
        fee = getattr(self._fees.get_latest(command.project_id), "latest_confirmed_fee", None)
        basic = self._basic_information.get_latest_confirmed(command.project_id)
        if workspace is None or fee is None or basic is None:
            raise FeeFormPublicationConflictError("Fee Form authority changed after preview.")
        operation_dir = Path(command.staging_dir) / uuid4().hex
        staged: Path | None = None
        try:
            staged = self._generator.generate(
                project_id=command.project_id,
                output_dir=operation_dir,
                output_file_name=current.target_path.name,
                confirmed_fee=fee,
                basic_information=basic,
            )
            output_hash = self._files.fingerprint(staged)
            archive = self._files.publish(
                staged_path=staged,
                target_path=current.target_path,
                conflict_action=action,
                history_dir=(
                    Path(workspace.local_workspace_path) / "History" / "Fee Form"
                ),
                expected_target_fingerprint=current.target_fingerprint,
            )
        finally:
            if staged is not None and staged.exists():
                staged.unlink()
            if operation_dir.is_dir() and not any(operation_dir.iterdir()):
                operation_dir.rmdir()
        self._outputs.register_output(
            RegisterProjectOutputCommand(
                project_id=command.project_id,
                output_kind=ProjectOutputKind.FEE_EVALUATION,
                status=ProjectOutputStatus.CURRENT,
                source=ProjectOutputSource.SYSTEM_GENERATED,
                output_path=str(current.target_path),
                draft_id=None,
                output_sha256=output_hash,
                output_size_bytes=current.target_path.stat().st_size,
                source_context_signature=_source_context(fee, basic),
                note="Published from current confirmed Fee authority.",
            )
        )
        return FeeFormPublicationResult(
            command.project_id, current.target_path, archive, current.target_path.name
        )

    def _preview(
        self,
        command: PreviewFeeFormPublicationCommand,
        *,
        mode: str,
        status: str = "ready",
        target_path: Path | None = None,
        target_fingerprint: str | None = None,
        existing_modified_at: str | None = None,
        blockers: tuple[str, ...] = (),
        basic_information=None,
        confirmed_fee=None,
    ) -> FeeFormPublicationPreview:
        payload = {
            "project_id": command.project_id,
            "current_values": asdict(command.current_values),
            "mode": mode,
            "status": status,
            "target_path": str(target_path) if target_path else None,
            "target_fingerprint": target_fingerprint,
            "blockers": blockers,
            "basic_version": getattr(basic_information, "version", None),
            "fee_id": getattr(confirmed_fee, "confirmed_fee_id", None),
            "fee_revision": getattr(confirmed_fee, "confirmed_fee_revision", None),
        }
        token = sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        return FeeFormPublicationPreview(
            project_id=command.project_id,
            mode=mode,
            status=status,
            target_path=target_path,
            target_fingerprint=target_fingerprint,
            existing_file=target_fingerprint is not None,
            existing_modified_at=existing_modified_at,
            blockers=blockers,
            preview_token=token,
        )


def _safe_file_stem(value: str) -> str:
    return re.sub(r'[<>:"/\\|?*]+', "_", value).strip(" .") or "Fee"


def _source_context(fee: object, basic: object) -> str:
    return (
        f"confirmed-fee:{getattr(fee, 'confirmed_fee_id', '')}:"
        f"r{getattr(fee, 'confirmed_fee_revision', '')}|"
        f"basic-information:v{getattr(basic, 'version', '')}:"
        f"{getattr(basic, 'source_signature_hash', '')}"
    )
