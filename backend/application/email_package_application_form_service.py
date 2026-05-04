from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol
from uuid import uuid4

from backend.application.intake_form_selection_service import (
    FormSelectionResult,
    IntakeFormSelectionService,
)
from backend.domain import (
    IntakeAsset,
    IntakeAssetRole,
    IntakePackage,
    IntakePackageSourceType,
)
from backend.infrastructure.files import IntakeStorage
from backend.infrastructure.office import OfficeFacade, OfficeFileKind


class EmailPackageApplicationFormError(ValueError):
    """Raised when a supplemental email-package form cannot be accepted."""


class EmailPackageApplicationFormNotFoundError(LookupError):
    """Raised when the target intake package does not exist."""


class IntakePackageStore(Protocol):
    """Persistence port for intake packages."""

    def get(self, package_id: str) -> IntakePackage | None: ...


class IntakeAssetStore(Protocol):
    """Persistence port for intake assets."""

    def create(self, asset: IntakeAsset) -> IntakeAsset: ...


@dataclass(frozen=True)
class EmailPackageApplicationFormService:
    """Attach a supplemental Word application form to an existing email package."""

    storage: IntakeStorage
    package_store: IntakePackageStore
    asset_store: IntakeAssetStore
    selection_service: IntakeFormSelectionService
    office: OfficeFacade | None = None

    _allowed_kinds = {OfficeFileKind.DOCX}

    def upload_application_form(
        self,
        package_id: str,
        source_path: Path,
    ) -> FormSelectionResult:
        """Store a Word form in an existing `.msg` package and select it."""
        package = self.package_store.get(package_id)
        if package is None:
            raise EmailPackageApplicationFormNotFoundError(
                f"Intake package not found: {package_id}"
            )
        if package.source_type is not IntakePackageSourceType.OUTLOOK_MSG:
            raise EmailPackageApplicationFormError(
                "Supplemental application-form upload is only available for email packages."
            )

        office = self.office or OfficeFacade()
        classification = office.classify_file(source_path)
        if classification.kind not in self._allowed_kinds:
            raise EmailPackageApplicationFormError(
                "Supplemental application-form upload accepts only .docx files."
            )

        asset_id = f"asset-{uuid4().hex}"
        stored = self.storage.copy_attachment(
            package.package_id,
            asset_id,
            source_path,
            original_name=classification.original_name,
        )
        asset = self.asset_store.create(
            IntakeAsset(
                asset_id=asset_id,
                package_id=package.package_id,
                original_name=classification.original_name,
                stored_path=stored.stored_path,
                extension=f".{classification.extension}",
                mime_type=classification.mime_type,
                size_bytes=stored.size_bytes,
                sha256=stored.sha256,
                asset_role=IntakeAssetRole.APPLICATION_FORM_CANDIDATE,
                candidate_score=100,
            )
        )
        return self.selection_service.select_form_asset(package.package_id, asset.asset_id)
