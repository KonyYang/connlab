"""Read models for saved New Project creation drafts."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Protocol

from backend.domain import IntakeCase, IntakeDraft, IntakePackage, IntakePackageStatus


class ProjectCreationDraftQueryError(ValueError):
    """Raised when saved draft data cannot be read."""


class IntakePackageStore(Protocol):
    """Read port for intake packages."""

    def list(self) -> list[IntakePackage]: ...


class IntakeCaseStore(Protocol):
    """Read port for intake cases."""

    def list_by_package(self, package_id: str) -> list[IntakeCase]: ...


class IntakeDraftStore(Protocol):
    """Read port for intake drafts."""

    def get_by_case(self, case_id: str) -> IntakeDraft | None: ...


@dataclass(frozen=True)
class ProjectCreationDraftRow:
    """One saved creation draft row shown outside the confirmed project registry."""

    package_id: str
    source_type: str
    source_name: str
    subject: str | None
    requester: str | None
    product_name: str | None
    updated_at: str | None
    current_step: str
    selected_form_asset_id: str | None
    active_case_id: str | None


class ProjectCreationDraftQueryService:
    """Loads saved creation drafts for Drafts / In Progress."""

    def __init__(
        self,
        package_store: IntakePackageStore,
        case_store: IntakeCaseStore,
        draft_store: IntakeDraftStore,
    ) -> None:
        """Create the query service from explicit persistence ports."""
        self._packages = package_store
        self._cases = case_store
        self._drafts = draft_store

    def list_saved_drafts(self) -> tuple[ProjectCreationDraftRow, ...]:
        """Return saved creation drafts ordered by most recent update text."""
        rows = [
            self._to_row(package)
            for package in self._packages.list()
            if package.status is IntakePackageStatus.DRAFT_SAVED
        ]
        return tuple(
            sorted(rows, key=lambda row: row.updated_at or "", reverse=True)
        )

    def _to_row(self, package: IntakePackage) -> ProjectCreationDraftRow:
        """Build one draft display row and continuation target."""
        cases = self._cases.list_by_package(package.package_id)
        active_case = cases[0] if cases else None
        draft = self._drafts.get_by_case(active_case.case_id) if active_case else None
        data = self._merged_draft_data(draft) if draft else {}
        return ProjectCreationDraftRow(
            package_id=package.package_id,
            source_type=package.source_type.value,
            source_name=package.source_original_name,
            subject=package.subject,
            requester=self._optional_text(data, "requester") or package.sender_name,
            product_name=self._optional_text(data, "product_name"),
            updated_at=(draft.updated_at if draft else None) or package.updated_at or package.created_at,
            current_step="precheck" if active_case else "intake",
            selected_form_asset_id=active_case.selected_form_asset_id if active_case else None,
            active_case_id=active_case.case_id if active_case else None,
        )

    def _merged_draft_data(self, draft: IntakeDraft) -> dict[str, Any]:
        """Return parsed fields overlaid with non-empty manual corrections."""
        parsed = self._load_json_object(draft.parsed_fields_json)
        overrides = self._load_json_object(draft.manual_overrides_json) if draft.manual_overrides_json else {}
        return {
            **parsed,
            **{key: value for key, value in overrides.items() if value not in (None, "")},
        }

    def _load_json_object(self, raw: str | None) -> dict[str, Any]:
        """Parse a JSON object, returning an empty object for invalid optional text."""
        if not raw:
            return {}
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ProjectCreationDraftQueryError("Saved draft data is not valid JSON.") from exc
        if not isinstance(value, dict):
            raise ProjectCreationDraftQueryError("Saved draft data must be a JSON object.")
        return value

    def _optional_text(self, data: dict[str, Any], key: str) -> str | None:
        """Return a stripped text value from draft data."""
        value = data.get(key)
        if value is None:
            return None
        text = str(value).strip()
        return text or None
