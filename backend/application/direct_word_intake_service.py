from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol
from uuid import uuid4

from backend.application.intake_candidate_service import ApplicationFormCandidateDetector
from backend.domain import (
    IntakeAsset,
    IntakeAssetRole,
    IntakePackage,
    IntakePackageSourceType,
    IntakePackageStatus,
)
from backend.infrastructure.files import IntakeStorage
from backend.infrastructure.office import OfficeFacade, OfficeFileKind


class DirectWordIntakeError(ValueError):
    """Raised when a direct Word intake source is invalid."""


class IntakePackageStore(Protocol):
    def create(self, package: IntakePackage) -> IntakePackage: ...


class IntakeAssetStore(Protocol):
    def create(self, asset: IntakeAsset) -> IntakeAsset: ...

    def list_by_package(self, package_id: str) -> list[IntakeAsset]: ...

    def update(self, asset: IntakeAsset) -> IntakeAsset: ...


@dataclass(frozen=True)
class DirectWordIntakeResult:
    package: IntakePackage
    asset: IntakeAsset


class DirectWordIntakeService:
    """Imports one local Word application form into the intake review flow."""

    _allowed_kinds = {OfficeFileKind.DOCX, OfficeFileKind.DOC}

    def __init__(
        self,
        storage: IntakeStorage,
        package_store: IntakePackageStore,
        asset_store: IntakeAssetStore,
        office: OfficeFacade | None = None,
    ) -> None:
        self._storage = storage
        self._package_store = package_store
        self._asset_store = asset_store
        self._office = office or OfficeFacade()

    def import_word_form(self, source_path: Path) -> DirectWordIntakeResult:
        classification = self._office.classify_file(source_path)
        if classification.kind not in self._allowed_kinds:
            raise DirectWordIntakeError("Direct intake accepts only .docx or .doc files.")

        package_id = f"pkg-{uuid4().hex}"
        asset_id = f"asset-{uuid4().hex}"
        stored = self._storage.copy_source_file(
            package_id,
            Path(source_path),
            original_name=classification.original_name,
        )

        package = self._package_store.create(
            IntakePackage(
                package_id=package_id,
                source_type=IntakePackageSourceType.DIRECT_APPLICATION_FORM,
                status=IntakePackageStatus.READY_FOR_REVIEW,
                source_original_name=stored.original_name,
                source_stored_path=stored.stored_path,
                subject=classification.original_name,
            )
        )
        asset = self._asset_store.create(
            IntakeAsset(
                asset_id=asset_id,
                package_id=package.package_id,
                original_name=stored.original_name,
                stored_path=stored.stored_path,
                extension=f".{classification.extension}",
                mime_type=classification.mime_type,
                size_bytes=stored.size_bytes,
                sha256=stored.sha256,
                asset_role=IntakeAssetRole.UNKNOWN,
            )
        )

        ApplicationFormCandidateDetector(self._asset_store).detect_for_package(package.package_id)
        updated_asset = self._asset_store.update(
            self._asset_store.list_by_package(package.package_id)[0]
        )
        return DirectWordIntakeResult(package=package, asset=updated_asset)
