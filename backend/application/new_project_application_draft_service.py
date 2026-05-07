"""Application draft preparation for the single-page New Project flow."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from typing import Protocol
from uuid import uuid4

from backend.application.intake_form_selection_service import (
    IntakeFormSelectionService,
    IntakeSelectionError,
    IntakeSelectionNotFoundError,
)
from backend.domain import (
    IntakeAsset,
    IntakeCase,
    IntakeCaseStatus,
    IntakeDraft,
    IntakePackage,
    IntakePackageStatus,
)

logger = logging.getLogger(__name__)


class NewProjectApplicationDraftNotFoundError(LookupError):
    """Raised when a New Project package cannot be found."""


class IntakePackageStore(Protocol):
    """Persistence port for intake packages."""

    def get(self, package_id: str) -> IntakePackage | None: ...

    def update(self, package: IntakePackage) -> IntakePackage: ...


class IntakeAssetStore(Protocol):
    """Persistence port for intake package assets."""

    def list_by_package(self, package_id: str) -> list[IntakeAsset]: ...


class IntakeCaseStore(Protocol):
    """Persistence port for intake cases."""

    def create(self, case: IntakeCase) -> IntakeCase: ...

    def list_by_package(self, package_id: str) -> list[IntakeCase]: ...

    def update(self, case: IntakeCase) -> IntakeCase: ...


class IntakeDraftStore(Protocol):
    """Persistence port for intake drafts."""

    def create(self, draft: IntakeDraft) -> IntakeDraft: ...

    def get_by_case(self, case_id: str) -> IntakeDraft | None: ...


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

    def ensure_draft(self, package_id: str) -> NewProjectApplicationDraftResult:
        """Return an editable draft case, creating a blank one when needed."""
        package = self._packages.get(package_id)
        if package is None:
            raise NewProjectApplicationDraftNotFoundError(
                f"Intake package not found: {package_id}"
            )

        case = self._reusable_case(package.package_id)
        if case is None:
            case = self._cases.create(
                IntakeCase(
                    case_id=f"case-{uuid4().hex}",
                    package_id=package.package_id,
                    selected_form_asset_id=None,
                    status=IntakeCaseStatus.NEEDS_REVIEW,
                )
            )
        else:
            case = self._cases.update(
                replace(case, status=IntakeCaseStatus.NEEDS_REVIEW)
            )

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

    def _auto_select_application_form(
        self, package_id: str
    ) -> tuple[IntakeCase, IntakeDraft] | None:
        """Select the highest-ranked candidate form when the editor opens blank."""
        if self._assets is None or self._selection_service is None:
            return None
        reusable_case = next(
            (
                case
                for case in self._cases.list_by_package(package_id)
                if case.confirmed_project_id is None
                and case.status is not IntakeCaseStatus.CONFIRMED
                and case.selected_form_asset_id is None
            ),
            None,
        )
        if reusable_case is None:
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

    def _is_word_document(self, asset: IntakeAsset) -> bool:
        """Return whether the asset should be considered for default form selection."""
        extension = asset.extension or Path(asset.original_name).suffix
        extension = extension.lower()
        if extension and not extension.startswith("."):
            extension = f".{extension}"
        return extension == ".docx"
