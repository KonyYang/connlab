from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, replace
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import BinaryIO, Protocol
from uuid import uuid4

from backend.application.intake_candidate_service import (
    ApplicationFormCandidate,
    ApplicationFormCandidateDetector,
)
from backend.domain import (
    IntakeAsset,
    IntakeAssetRole,
    IntakePackage,
    IntakePackageSourceType,
    IntakePackageStatus,
)
from backend.infrastructure.files import IntakeStorage
from backend.infrastructure.office import OfficeFacade
from backend.infrastructure.office.outlook_msg_gateway import OutlookMsgImportError


class MsgPackageIntakeError(ValueError):
    """Raised when a manual `.msg` package import cannot be completed."""


class IntakePackageStore(Protocol):
    """Persistence port for intake packages."""

    def create(self, package: IntakePackage) -> IntakePackage: ...

    def update(self, package: IntakePackage) -> IntakePackage: ...


class IntakeAssetStore(Protocol):
    """Persistence port for intake package assets."""

    def create(self, asset: IntakeAsset) -> IntakeAsset: ...

    def list_by_package(self, package_id: str) -> list[IntakeAsset]: ...

    def update(self, asset: IntakeAsset) -> IntakeAsset: ...


@dataclass(frozen=True)
class MsgPackageIntakeResult:
    """Imported `.msg` package and detected asset state."""

    package: IntakePackage
    assets: tuple[IntakeAsset, ...]
    candidates: tuple[ApplicationFormCandidate, ...]
    duplicate_check: None = None
    resolution_action: str | None = None


class MsgPackageIntakeService:
    """Imports one uploaded Outlook `.msg` package into intake review storage."""

    def __init__(
        self,
        storage: IntakeStorage,
        package_store: IntakePackageStore,
        asset_store: IntakeAssetStore,
        office: OfficeFacade | None = None,
    ) -> None:
        """Create the service with explicit storage and persistence ports."""
        self._storage = storage
        self._package_store = package_store
        self._asset_store = asset_store
        self._office = office or OfficeFacade()

    def import_msg_package(
        self,
        filename: str,
        source: BinaryIO,
        resolution_action: str | None = None,
        resolution_package_id: str | None = None,
    ) -> MsgPackageIntakeResult:
        """Import an uploaded `.msg` file and register extracted attachments."""
        safe_name = self._safe_msg_filename(filename)
        package_id = f"pkg-{uuid4().hex}"
        with TemporaryDirectory(prefix="connlab-msg-import-") as directory:
            uploaded_path = Path(directory) / safe_name
            with uploaded_path.open("wb") as handle:
                shutil.copyfileobj(source, handle)

            try:
                imported = self._office.import_outlook_msg(
                    uploaded_path,
                    self._storage.package_root(package_id),
                )
            except OutlookMsgImportError as exc:
                raise MsgPackageIntakeError(str(exc)) from exc

        if resolution_action is not None or resolution_package_id is not None:
            self._storage.delete_package(package_id)
            raise MsgPackageIntakeError(
                "Email package duplicate resolution now happens when a draft is created."
            )

        package = self._package_store.create(
            IntakePackage(
                package_id=package_id,
                source_type=IntakePackageSourceType.OUTLOOK_MSG,
                status=IntakePackageStatus.IMPORTED,
                source_original_name=imported.source_original_name,
                source_stored_path=imported.source_stored_path,
                subject=imported.subject,
                sender_name=imported.sender_name,
                sender_email=imported.sender_email,
                recipients_json=json.dumps(imported.recipients, ensure_ascii=False),
                cc_json=json.dumps(imported.cc, ensure_ascii=False),
                received_at=imported.sent_at.isoformat() if imported.sent_at else None,
                body_text=imported.body_text,
            )
        )
        self._asset_store.create(
            IntakeAsset(
                asset_id=f"asset-{uuid4().hex}",
                package_id=package.package_id,
                original_name=imported.source_original_name,
                stored_path=imported.source_stored_path,
                extension=".msg",
                mime_type="application/vnd.ms-outlook",
                size_bytes=imported.source_stored_path.stat().st_size,
                sha256=self._storage.sha256(imported.source_stored_path),
                asset_role=IntakeAssetRole.EMAIL_SOURCE,
            )
        )
        for attachment in imported.attachments:
            self._asset_store.create(
                IntakeAsset(
                    asset_id=f"asset-{uuid4().hex}",
                    package_id=package.package_id,
                    original_name=attachment.original_name,
                    stored_path=attachment.stored_path,
                    extension=f".{attachment.extension}" if attachment.extension else "",
                    mime_type=attachment.mime_type,
                    size_bytes=attachment.size_bytes,
                    sha256=attachment.sha256,
                    asset_role=IntakeAssetRole.UNKNOWN,
                    content_id=attachment.content_id,
                )
            )

        detection = ApplicationFormCandidateDetector(self._asset_store).detect_for_package(
            package.package_id
        )
        updated_package = self._package_store.update(
            replace(
                package,
                status=(
                    IntakePackageStatus.READY_FOR_REVIEW
                    if detection.candidates
                    else IntakePackageStatus.NEEDS_APPLICATION_FORM_SELECTION
                ),
            )
        )
        return MsgPackageIntakeResult(
            package=updated_package,
            assets=tuple(self._asset_store.list_by_package(package.package_id)),
            candidates=detection.candidates,
            resolution_action=None,
        )

    def _safe_msg_filename(self, filename: str) -> str:
        """Return a safe uploaded `.msg` filename or raise a validation error."""
        safe_name = self._storage.sanitize_filename(filename or "source.msg")
        if Path(safe_name).suffix.lower() != ".msg":
            raise MsgPackageIntakeError("Manual package import accepts only .msg files.")
        return safe_name
