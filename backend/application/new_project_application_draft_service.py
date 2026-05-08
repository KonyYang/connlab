"""Application draft preparation for the single-page New Project flow."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol
from uuid import uuid4

from backend.application.intake_form_selection_service import (
    IntakeDraftDuplicateCheck,
    IntakeDraftDuplicateResolutionRequiredError,
    IntakeFormSelectionService,
    IntakeSelectionError,
    IntakeSelectionNotFoundError,
)
from backend.domain import (
    IntakeAsset,
    IntakeAssetRole,
    IntakeCase,
    IntakeCaseStatus,
    IntakeDraft,
    IntakePackage,
    IntakePackageSourceType,
    IntakePackageStatus,
)

logger = logging.getLogger(__name__)


class NewProjectApplicationDraftNotFoundError(LookupError):
    """Raised when a New Project package cannot be found."""


class IntakePackageStore(Protocol):
    """Persistence port for intake packages."""

    def get(self, package_id: str) -> IntakePackage | None: ...

    def list(self) -> list[IntakePackage]: ...

    def update(self, package: IntakePackage) -> IntakePackage: ...

    def delete(self, package_id: str) -> bool: ...


class IntakeAssetStore(Protocol):
    """Persistence port for intake package assets."""

    def list_by_package(self, package_id: str) -> list[IntakeAsset]: ...

    def delete_by_package(self, package_id: str) -> int: ...


class IntakeCaseStore(Protocol):
    """Persistence port for intake cases."""

    def create(self, case: IntakeCase) -> IntakeCase: ...

    def list_by_package(self, package_id: str) -> list[IntakeCase]: ...

    def update(self, case: IntakeCase) -> IntakeCase: ...

    def delete_by_package(self, package_id: str) -> int: ...


class IntakeDraftStore(Protocol):
    """Persistence port for intake drafts."""

    def create(self, draft: IntakeDraft) -> IntakeDraft: ...

    def get_by_case(self, case_id: str) -> IntakeDraft | None: ...

    def delete_by_package(self, package_id: str) -> int: ...


@dataclass(frozen=True)
class NewProjectApplicationDraftResult:
    """Editable application draft identity for one New Project package."""

    package: IntakePackage
    case: IntakeCase
    draft: IntakeDraft


class NewProjectApplicationDraftService:
    """Creates the blank durable editor draft used before application-form import."""

    def __init__(
        self,
        package_store: IntakePackageStore,
        case_store: IntakeCaseStore,
        draft_store: IntakeDraftStore,
        asset_store: IntakeAssetStore | None = None,
        selection_service: IntakeFormSelectionService | None = None,
    ) -> None:
        """Create the service from explicit persistence ports."""
        self._packages = package_store
        self._cases = case_store
        self._drafts = draft_store
        self._assets = asset_store
        self._selection_service = selection_service

    def ensure_draft(
        self,
        package_id: str,
        resolution_action: str | None = None,
        resolution_case_id: str | None = None,
    ) -> NewProjectApplicationDraftResult:
        """Return an editable draft case, creating a blank one when needed."""
        package = self._packages.get(package_id)
        if package is None:
            raise NewProjectApplicationDraftNotFoundError(
                f"Intake package not found: {package_id}"
            )

        updated_package = package
        if package.status is not IntakePackageStatus.DRAFT_SAVED:
            updated_package = self._packages.update(
                replace(
                    package,
                    status=IntakePackageStatus.READY_FOR_REVIEW,
                    updated_at=datetime.now(UTC).isoformat(),
                )
            )
        selected_result = self._auto_select_application_form(updated_package.package_id)
        if selected_result is not None:
            case, draft = selected_result
            return NewProjectApplicationDraftResult(
                package=updated_package,
                case=case,
                draft=draft,
            )
        duplicate = self._find_no_form_duplicate(updated_package)
        if duplicate is not None:
            resolved = self._resolve_no_form_duplicate(
                duplicate,
                resolution_action,
                resolution_case_id,
            )
            if resolved is not None:
                return resolved

        case, draft = self._create_or_reuse_blank_draft(updated_package.package_id)
        return NewProjectApplicationDraftResult(
            package=updated_package,
            case=case,
            draft=draft,
        )

    def _reusable_case(self, package_id: str) -> IntakeCase | None:
        """Return the first unconfirmed case for the package."""
        for case in self._cases.list_by_package(package_id):
            if (
                case.confirmed_project_id is None
                and case.status is not IntakeCaseStatus.CONFIRMED
            ):
                return case
        return None

    def _create_or_reuse_blank_draft(self, package_id: str) -> tuple[IntakeCase, IntakeDraft]:
        """Return or create the package's no-form editable draft."""
        case = self._reusable_case(package_id)
        if case is None:
            case = self._cases.create(
                IntakeCase(
                    case_id=f"case-{uuid4().hex}",
                    package_id=package_id,
                    selected_form_asset_id=None,
                    status=IntakeCaseStatus.NEEDS_REVIEW,
                )
            )
        else:
            case = self._cases.update(replace(case, status=IntakeCaseStatus.NEEDS_REVIEW))

        draft = self._drafts.get_by_case(case.case_id)
        if draft is None:
            draft = self._drafts.create(
                IntakeDraft(
                    draft_id=f"draft-{uuid4().hex}",
                    case_id=case.case_id,
                    parsed_fields_json=json.dumps({}, sort_keys=True),
                    parser_warnings_json=json.dumps([], sort_keys=True),
                    updated_at=datetime.now(UTC).isoformat(),
                )
            )
        return case, draft

    def _auto_select_application_form(
        self, package_id: str
    ) -> tuple[IntakeCase, IntakeDraft] | None:
        """Select the highest-ranked candidate form when the editor opens blank."""
        if self._assets is None or self._selection_service is None:
            return None
        candidates = [
            asset
            for asset in self._assets.list_by_package(package_id)
            if self._is_word_document(asset)
        ]
        for asset in candidates:
            try:
                selection = self._selection_service.select_form_asset(
                    package_id,
                    asset.asset_id,
                )
            except IntakeDraftDuplicateResolutionRequiredError:
                raise
            except (IntakeSelectionError, IntakeSelectionNotFoundError) as exc:
                logger.info(
                    "new_project_default_application_form_rejected",
                    extra={
                        "package_id": package_id,
                        "asset_id": asset.asset_id,
                        "reason": str(exc),
                    },
                )
                continue
            return selection.case, selection.draft
        return None

    def _find_no_form_duplicate(
        self,
        package: IntakePackage,
    ) -> IntakeDraftDuplicateCheck | None:
        """Return a duplicate no-form email draft when one already exists."""
        if package.source_type is not IntakePackageSourceType.OUTLOOK_MSG:
            return None
        incoming_source = self._email_source_asset(package.package_id)
        if incoming_source is None:
            return None
        for existing_package in self._packages.list():
            if existing_package.package_id == package.package_id:
                continue
            if existing_package.source_type is not IntakePackageSourceType.OUTLOOK_MSG:
                continue
            existing_source = self._email_source_asset(existing_package.package_id)
            if existing_source is None:
                continue
            if existing_source.original_name != incoming_source.original_name:
                continue
            if existing_source.size_bytes != incoming_source.size_bytes:
                continue
            for existing_case in self._cases.list_by_package(existing_package.package_id):
                if (
                    existing_case.selected_form_asset_id is None
                    and existing_case.confirmed_project_id is None
                    and existing_case.status is not IntakeCaseStatus.CONFIRMED
                ):
                    return IntakeDraftDuplicateCheck(
                        classification="exact_existing_no_form_draft",
                        existing_package_id=existing_package.package_id,
                        existing_case_id=existing_case.case_id,
                        existing_source_original_name=existing_source.original_name,
                        incoming_source_original_name=incoming_source.original_name,
                        existing_source_size_bytes=existing_source.size_bytes,
                        incoming_source_size_bytes=incoming_source.size_bytes,
                        existing_application_form_name=None,
                        incoming_application_form_name=None,
                    )
        return None

    def _resolve_no_form_duplicate(
        self,
        duplicate: IntakeDraftDuplicateCheck,
        resolution_action: str | None,
        resolution_case_id: str | None,
    ) -> NewProjectApplicationDraftResult | None:
        """Apply no-form duplicate resolution or require operator choice."""
        if resolution_case_id and resolution_case_id != duplicate.existing_case_id:
            raise IntakeSelectionError("Duplicate resolution target does not match.")
        if resolution_action is None:
            raise IntakeDraftDuplicateResolutionRequiredError(duplicate)
        if resolution_action == "create_separate":
            return None
        if resolution_action == "open_existing":
            package = self._packages.get(duplicate.existing_package_id)
            case, draft = self._existing_no_form_draft(duplicate)
            if package is None:
                raise NewProjectApplicationDraftNotFoundError(
                    "Existing no-form draft package not found."
                )
            return NewProjectApplicationDraftResult(package=package, case=case, draft=draft)
        if resolution_action == "replace_existing":
            self._delete_package_records(duplicate.existing_package_id)
            return None
        raise IntakeSelectionError("Unsupported duplicate resolution action.")

    def _existing_no_form_draft(
        self,
        duplicate: IntakeDraftDuplicateCheck,
    ) -> tuple[IntakeCase, IntakeDraft]:
        """Return the existing no-form duplicate draft records."""
        case = next(
            (
                current
                for current in self._cases.list_by_package(duplicate.existing_package_id)
                if current.case_id == duplicate.existing_case_id
            ),
            None,
        )
        if case is None:
            raise NewProjectApplicationDraftNotFoundError("Existing no-form draft not found.")
        draft = self._drafts.get_by_case(case.case_id)
        if draft is None:
            raise NewProjectApplicationDraftNotFoundError(
                "Existing no-form draft record not found."
            )
        return case, draft

    def _email_source_asset(self, package_id: str) -> IntakeAsset | None:
        """Return the email source asset for one package."""
        if self._assets is None:
            return None
        return next(
            (
                asset
                for asset in self._assets.list_by_package(package_id)
                if asset.asset_role is IntakeAssetRole.EMAIL_SOURCE
            ),
            None,
        )

    def _delete_package_records(self, package_id: str) -> None:
        """Delete old unconfirmed no-form duplicate records after replacement."""
        self._drafts.delete_by_package(package_id)
        self._cases.delete_by_package(package_id)
        if self._assets is not None:
            self._assets.delete_by_package(package_id)
        self._packages.delete(package_id)

    def _is_word_document(self, asset: IntakeAsset) -> bool:
        """Return whether the asset should be considered for default form selection."""
        extension = asset.extension or Path(asset.original_name).suffix
        extension = extension.lower()
        if extension and not extension.startswith("."):
            extension = f".{extension}"
        return extension == ".docx"
