from __future__ import annotations

import json
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from typing import Any, Protocol

from backend.application.intake_section1_precheck import (
    DraftPrecheckIssue,
    blocking_issue_fields,
    clear_disallowed_section1_values,
    evaluate_section1_precheck,
)
from backend.domain import IntakeAsset, IntakeCase, IntakeDraft, IntakePackage


class IntakeCaseReviewNotFoundError(LookupError):
    """Raised when review data cannot be found for an intake package."""


class IntakePackageStore(Protocol):
    """Read port for intake packages."""

    def get(self, package_id: str) -> IntakePackage | None: ...


class IntakeAssetStore(Protocol):
    """Read port for intake package assets."""

    def get(self, asset_id: str) -> IntakeAsset | None: ...


class IntakeCaseStore(Protocol):
    """Read port for intake cases."""

    def get(self, case_id: str) -> IntakeCase | None: ...

    def list_by_package(self, package_id: str) -> list[IntakeCase]: ...


class IntakeDraftStore(Protocol):
    """Read port for intake drafts."""

    def get_by_case(self, case_id: str) -> IntakeDraft | None: ...

    def update(self, draft: IntakeDraft) -> IntakeDraft: ...


@dataclass(frozen=True)
class IntakeCaseReviewItem:
    """Review data for one selected intake case."""

    case: IntakeCase
    draft: IntakeDraft
    selected_asset: IntakeAsset | None
    parsed_fields: dict[str, Any]
    missing_required_fields: tuple[str, ...]
    precheck_issues: tuple[DraftPrecheckIssue, ...]


@dataclass(frozen=True)
class IntakeCaseReview:
    """Unified review data for an intake package."""

    package: IntakePackage
    cases: tuple[IntakeCaseReviewItem, ...]


class IntakeCaseReviewService:
    """Loads unified email/manual intake case review data."""

    _editable_fields = {
        "product_name",
        "requester",
        "email",
        "business_unit",
        "project_no",
        "form_no",
        "revision",
        "requested_testing",
        "requested_testing_rows",
        "phone",
        "request_date",
        "manufacturing_site",
        "results_format",
        "requested_completion_date",
        "test_type",
        "sample_status",
        "project_type",
        "post_testing_disposition",
        "confidential",
        "subcontract",
        "additional_information",
        "send_copies_recipients",
    }

    def __init__(
        self,
        package_store: IntakePackageStore,
        asset_store: IntakeAssetStore,
        case_store: IntakeCaseStore,
        draft_store: IntakeDraftStore,
    ) -> None:
        """Create the service from explicit repository ports."""
        self._packages = package_store
        self._assets = asset_store
        self._cases = case_store
        self._drafts = draft_store

    def get_package_review(self, package_id: str) -> IntakeCaseReview:
        """Return review data for all cases in one package."""
        package = self._packages.get(package_id)
        if package is None:
            raise IntakeCaseReviewNotFoundError(f"Intake package not found: {package_id}")
        items: list[IntakeCaseReviewItem] = []
        for case in self._cases.list_by_package(package.package_id):
            draft = self._drafts.get_by_case(case.case_id)
            if draft is None:
                raise IntakeCaseReviewNotFoundError(
                    f"Intake draft not found for case: {case.case_id}"
                )
            selected_asset = (
                self._assets.get(case.selected_form_asset_id)
                if case.selected_form_asset_id
                else None
            )
            draft_fields = self._merged_draft_fields(draft)
            precheck_issues = evaluate_section1_precheck(draft_fields)
            parsed_fields = clear_disallowed_section1_values(draft_fields)
            items.append(
                IntakeCaseReviewItem(
                    case=case,
                    draft=draft,
                    selected_asset=selected_asset,
                    parsed_fields=parsed_fields,
                    missing_required_fields=blocking_issue_fields(precheck_issues),
                    precheck_issues=precheck_issues,
                )
            )
        return IntakeCaseReview(package=package, cases=tuple(items))

    def update_case_fields(
        self,
        case_id: str,
        fields: dict[str, Any],
        sample_rows: list[dict[str, Any]] | None = None,
        requested_testing_rows: list[dict[str, Any]] | None = None,
    ) -> IntakeCaseReviewItem:
        """Persist operator field corrections and return the refreshed case review."""
        intake_case = self._cases.get(case_id)
        if intake_case is None:
            raise IntakeCaseReviewNotFoundError(f"Intake case not found: {case_id}")
        draft = self._drafts.get_by_case(intake_case.case_id)
        if draft is None:
            raise IntakeCaseReviewNotFoundError(
                f"Intake draft not found for case: {intake_case.case_id}"
            )
        overrides = self._json_object(draft.manual_overrides_json or "{}")
        for key, value in fields.items():
            if key not in self._editable_fields:
                continue
            normalized = self._normalized_override(value)
            if normalized is None:
                overrides.pop(key, None)
            else:
                overrides[key] = normalized
        if sample_rows is not None:
            overrides["samples"] = self._normalized_sample_rows(sample_rows)
        if requested_testing_rows is not None:
            normalized_rows = self._normalized_requested_testing_rows(requested_testing_rows)
            overrides["requested_testing_rows"] = normalized_rows
            # Also update flattened requested_testing for compatibility
            if "requested_testing" not in fields:
                tests_text = "\n".join(
                    row.get("test_to_be_performed", "")
                    for row in normalized_rows
                    if row.get("test_to_be_performed", "").strip()
                )
                if tests_text:
                    overrides["requested_testing"] = tests_text
        updated_draft = self._drafts.update(
            replace(
                draft,
                manual_overrides_json=json.dumps(
                    overrides,
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                updated_at=datetime.now(UTC).isoformat(),
            )
        )
        selected_asset = (
            self._assets.get(intake_case.selected_form_asset_id)
            if intake_case.selected_form_asset_id
            else None
        )
        draft_fields = self._merged_draft_fields(updated_draft)
        precheck_issues = evaluate_section1_precheck(draft_fields)
        parsed_fields = clear_disallowed_section1_values(draft_fields)
        return IntakeCaseReviewItem(
            case=intake_case,
            draft=updated_draft,
            selected_asset=selected_asset,
            parsed_fields=parsed_fields,
            missing_required_fields=blocking_issue_fields(precheck_issues),
            precheck_issues=precheck_issues,
        )

    def _merged_draft_fields(self, draft: IntakeDraft) -> dict[str, Any]:
        """Return parsed draft fields with manual overrides applied."""
        parsed = self._json_object(draft.parsed_fields_json)
        overrides = self._json_object(draft.manual_overrides_json or "{}")
        return {**parsed, **{key: value for key, value in overrides.items() if value not in (None, "")}}

    def _json_object(self, raw: str) -> dict[str, Any]:
        """Parse a JSON object, returning an empty object for invalid data."""
        try:
            value = json.loads(raw)
        except json.JSONDecodeError:
            return {}
        return value if isinstance(value, dict) else {}

    def _text(self, value: object) -> str | None:
        """Return stripped text or None."""
        if value in (None, ""):
            return None
        text = str(value).strip()
        return text or None

    def _normalized_override(self, value: object) -> str | None:
        """Return a persistable operator override value or None to clear it."""
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    def _normalized_sample_rows(self, rows: list[dict[str, Any]]) -> list[dict[str, str]]:
        """Return persistable sample row overrides, preserving at least one row."""
        normalized_rows: list[dict[str, str]] = []
        for row in rows:
            normalized_row = {
                str(key): str(value).strip()
                for key, value in row.items()
                if value is not None and str(value).strip()
            }
            normalized_rows.append(normalized_row)
        return normalized_rows or [{}]

    def _normalized_requested_testing_rows(self, rows: list[dict[str, Any]]) -> list[dict[str, str]]:
        """Return persistable requested-testing row overrides, filtering empty rows."""
        normalized_rows: list[dict[str, str]] = []
        for row in rows:
            normalized_row = {
                "test_to_be_performed": str(row.get("test_to_be_performed", "")).strip(),
                "applicable_specification": str(row.get("applicable_specification", "")).strip(),
            }
            if any(normalized_row.values()):
                normalized_rows.append(normalized_row)
        return normalized_rows
