from __future__ import annotations

import json
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Protocol
from uuid import uuid4

from backend.domain import (
    IntakeAsset,
    IntakeAssetRole,
    IntakeCase,
    IntakeCaseStatus,
    IntakeDraft,
    IntakePackage,
)


class IntakeSelectionError(ValueError):
    """Raised when a selected intake asset cannot become an application form."""


class IntakeSelectionNotFoundError(LookupError):
    """Raised when intake package or asset records are missing."""


class IntakePackageStore(Protocol):
    def get(self, package_id: str) -> IntakePackage | None: ...


class IntakeAssetStore(Protocol):
    def get(self, asset_id: str) -> IntakeAsset | None: ...

    def update(self, asset: IntakeAsset) -> IntakeAsset: ...


class IntakeCaseStore(Protocol):
    def create(self, case: IntakeCase) -> IntakeCase: ...

    def list_by_package(self, package_id: str) -> list[IntakeCase]: ...

    def update(self, case: IntakeCase) -> IntakeCase: ...


class IntakeDraftStore(Protocol):
    def create(self, draft: IntakeDraft) -> IntakeDraft: ...

    def get_by_case(self, case_id: str) -> IntakeDraft | None: ...

    def update(self, draft: IntakeDraft) -> IntakeDraft: ...


@dataclass(frozen=True)
class FormSelectionResult:
    package_id: str
    case: IntakeCase
    draft: IntakeDraft
    selected_asset: IntakeAsset


class IntakeFormSelectionService:
    """Creates review records after a human selects one application form asset."""

    _word_extensions = {".docx", ".doc"}
    _blocked_roles = {IntakeAssetRole.EMAIL_SOURCE, IntakeAssetRole.IGNORED}

    def __init__(
        self,
        package_store: IntakePackageStore,
        asset_store: IntakeAssetStore,
        case_store: IntakeCaseStore,
        draft_store: IntakeDraftStore,
    ) -> None:
        self._package_store = package_store
        self._asset_store = asset_store
        self._case_store = case_store
        self._draft_store = draft_store

    def select_form_asset(self, package_id: str, asset_id: str) -> FormSelectionResult:
        package = self._package_store.get(package_id)
        if package is None:
            raise IntakeSelectionNotFoundError(f"Intake package not found: {package_id}")

        asset = self._asset_store.get(asset_id)
        if asset is None:
            raise IntakeSelectionNotFoundError(f"Intake asset not found: {asset_id}")
        if asset.package_id != package.package_id:
            raise IntakeSelectionError("Selected asset does not belong to the intake package.")
        if not self._is_selectable_application_form(asset):
            raise IntakeSelectionError("Selected asset is not an application form candidate.")

        selected_asset = self._asset_store.update(
            replace(asset, asset_role=IntakeAssetRole.SELECTED_APPLICATION_FORM)
        )
        case = self._create_or_update_case(package.package_id, selected_asset.asset_id)
        draft = self._create_or_update_draft(case.case_id)

        return FormSelectionResult(
            package_id=package.package_id,
            case=case,
            draft=draft,
            selected_asset=selected_asset,
        )

    def _is_selectable_application_form(self, asset: IntakeAsset) -> bool:
        if asset.asset_role in self._blocked_roles:
            return False
        if asset.asset_role is IntakeAssetRole.APPLICATION_FORM_CANDIDATE:
            return True
        return self._normalized_extension(asset) in self._word_extensions

    def _create_or_update_case(self, package_id: str, selected_asset_id: str) -> IntakeCase:
        existing_cases = self._case_store.list_by_package(package_id)
        if existing_cases:
            current = existing_cases[0]
            return self._case_store.update(
                replace(
                    current,
                    selected_form_asset_id=selected_asset_id,
                    status=IntakeCaseStatus.NEEDS_REVIEW,
                    confirmed_project_id=None,
                )
            )
        return self._case_store.create(
            IntakeCase(
                case_id=f"case-{uuid4().hex}",
                package_id=package_id,
                selected_form_asset_id=selected_asset_id,
                status=IntakeCaseStatus.NEEDS_REVIEW,
            )
        )

    def _create_or_update_draft(self, case_id: str) -> IntakeDraft:
        existing_draft = self._draft_store.get_by_case(case_id)
        if existing_draft is not None:
            return self._draft_store.update(
                replace(
                    existing_draft,
                    parsed_fields_json=self._empty_json_object(),
                    parser_warnings_json=self._initial_parser_warnings(),
                )
            )
        return self._draft_store.create(
            IntakeDraft(
                draft_id=f"draft-{uuid4().hex}",
                case_id=case_id,
                parsed_fields_json=self._empty_json_object(),
                parser_warnings_json=self._initial_parser_warnings(),
            )
        )

    def _normalized_extension(self, asset: IntakeAsset) -> str:
        extension = asset.extension or Path(asset.original_name).suffix
        extension = extension.lower()
        if extension and not extension.startswith("."):
            return f".{extension}"
        return extension

    def _empty_json_object(self) -> str:
        return json.dumps({}, separators=(",", ":"))

    def _initial_parser_warnings(self) -> str:
        return json.dumps(
            ["Word content parsing is intentionally deferred until the parsing task."],
            separators=(",", ":"),
        )
