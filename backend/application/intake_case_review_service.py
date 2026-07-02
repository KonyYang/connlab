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
from backend.application.new_project_setup_policy import normalize_lab_performing_tests
from backend.domain import (
    IntakeAsset,
    IntakeCase,
    IntakeDraft,
    IntakePackage,
    LtrRecord,
    LtrStatus,
)


class IntakeCaseReviewNotFoundError(LookupError):
    """Raised when review data cannot be found for an intake package."""


class IntakeCaseReviewFrozenError(ValueError):
    """Raised when normal review edits target fields frozen by LTR registration."""

    def __init__(self, message: str, field_keys: tuple[str, ...]) -> None:
        """Create the error with the frozen fields that triggered it."""
        super().__init__(message)
        self.field_keys = field_keys


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


class LtrRecordStore(Protocol):
    """Read port for project LTR records."""

    def list_by_project(self, project_id: str) -> list[LtrRecord]: ...


@dataclass(frozen=True)
class IntakeCaseReviewItem:
    """Review data for one selected intake case."""

    case: IntakeCase
    draft: IntakeDraft
    selected_asset: IntakeAsset | None
    parsed_fields: dict[str, Any]
    missing_required_fields: tuple[str, ...]
    precheck_issues: tuple[DraftPrecheckIssue, ...]
    project_setup: dict[str, Any]
    base_editing_frozen: bool = False
    frozen_field_keys: tuple[str, ...] = ()
    frozen_reason: str | None = None


@dataclass(frozen=True)
class IntakeCaseReview:
    """Unified review data for an intake package."""

    package: IntakePackage
    cases: tuple[IntakeCaseReviewItem, ...]


class IntakeCaseReviewService:
    """Loads unified email/manual intake case review data."""

    FROZEN_REASON = "LTR registered. Base application fields require revise/exception handling."
    _default_test_type_in_sheet = "Partial Qualification"
    _test_type_in_sheet_options = (
        "Failure Analysis",
        "Partial Qualification",
        "Solderability",
        "Environmental",
        "Qualification",
        "Mechanical",
        "Electrical",
        "Chemical",
        "Analysis",
        "Whisker",
        "Other",
        "ORT",
    )

    _frozen_field_keys = (
        "form_no",
        "revision",
        "product_name",
        "requester",
        "phone",
        "request_date",
        "email",
        "business_unit",
        "manufacturing_site",
        "project_no",
        "results_format",
        "requested_completion_date",
        "test_type",
        "sample_status",
        "project_type",
        "post_testing_disposition",
        "requested_testing",
        "confidential",
        "subcontract",
        "samples",
        "requested_testing_rows",
    )

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
        ltr_store: LtrRecordStore | None = None,
    ) -> None:
        """Create the service from explicit repository ports."""
        self._packages = package_store
        self._assets = asset_store
        self._cases = case_store
        self._drafts = draft_store
        self._ltrs = ltr_store

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
            items.append(self._build_case_review_item(case, draft, selected_asset=selected_asset))
        return IntakeCaseReview(package=package, cases=tuple(items))

    @classmethod
    def frozen_field_keys(cls) -> tuple[str, ...]:
        """Return the authoritative frozen field list for post-LTR base edits."""
        return cls._frozen_field_keys

    def get_case_review_item(self, case_id: str) -> IntakeCaseReviewItem:
        """Return one case review item by case id."""
        intake_case = self._cases.get(case_id)
        if intake_case is None:
            raise IntakeCaseReviewNotFoundError(f"Intake case not found: {case_id}")
        draft = self._drafts.get_by_case(case_id)
        if draft is None:
            raise IntakeCaseReviewNotFoundError(f"Intake draft not found for case: {case_id}")
        selected_asset = (
            self._assets.get(intake_case.selected_form_asset_id)
            if intake_case.selected_form_asset_id
            else None
        )
        return self._build_case_review_item(intake_case, draft, selected_asset=selected_asset)

    def update_case_fields(
        self,
        case_id: str,
        fields: dict[str, Any],
        sample_rows: list[dict[str, Any]] | None = None,
        requested_testing_rows: list[dict[str, Any]] | None = None,
        project_setup: dict[str, Any] | None = None,
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
        draft_fields = self._merged_draft_fields(draft)
        frozen_changes = self._changed_frozen_fields(
            draft_fields,
            fields,
            sample_rows=sample_rows,
            requested_testing_rows=requested_testing_rows,
        )
        if frozen_changes and self._freeze_state(intake_case):
            raise IntakeCaseReviewFrozenError(self.FROZEN_REASON, frozen_changes)
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
        if project_setup is not None:
            normalized_setup = self._normalized_project_setup(project_setup)
            if normalized_setup:
                overrides["project_setup"] = normalized_setup
            else:
                overrides.pop("project_setup", None)
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
        return self._build_case_review_item(
            intake_case,
            updated_draft,
            selected_asset=selected_asset,
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

    def _normalized_project_setup(self, values: dict[str, Any]) -> dict[str, str]:
        """Return persistable New Project setup values."""
        allowed_keys = {
            "ltr_mode",
            "specified_ltr_number",
            "test_item",
            "sample_description",
            "location",
            "test_type_in_sheet",
            "project_leader",
            "lab_performing_tests",
        }
        normalized: dict[str, str] = {}
        for key in allowed_keys:
            if key == "lab_performing_tests":
                lab = normalize_lab_performing_tests(values.get(key), required=False)
                if lab is not None:
                    normalized[key] = lab
                continue
            value = self._normalized_override(values.get(key))
            if value is not None:
                normalized[key] = value
        return normalized

    def _freeze_state(self, intake_case: IntakeCase) -> bool:
        """Return whether base review edits are frozen by registered LTR state."""
        if self._ltrs is None or not intake_case.confirmed_project_id:
            return False
        return any(
            ltr.status is LtrStatus.REGISTERED
            for ltr in self._ltrs.list_by_project(intake_case.confirmed_project_id)
        )

    def _changed_frozen_fields(
        self,
        current_fields: dict[str, Any],
        fields: dict[str, Any],
        *,
        sample_rows: list[dict[str, Any]] | None,
        requested_testing_rows: list[dict[str, Any]] | None,
    ) -> tuple[str, ...]:
        """Return frozen field keys whose requested value differs from current draft data."""
        changed: list[str] = []
        frozen_scalar_fields = set(self._frozen_field_keys) - {"samples", "requested_testing_rows"}
        for key, value in fields.items():
            if key not in frozen_scalar_fields:
                continue
            if self._normalized_override(value) != self._normalized_override(current_fields.get(key)):
                changed.append(key)
        if sample_rows is not None:
            current_samples = current_fields.get("samples")
            if self._normalized_sample_rows(sample_rows) != (
                current_samples if isinstance(current_samples, list) else []
            ):
                changed.append("samples")
        if requested_testing_rows is not None:
            current_testing_rows = current_fields.get("requested_testing_rows")
            if self._normalized_requested_testing_rows(requested_testing_rows) != (
                current_testing_rows if isinstance(current_testing_rows, list) else []
            ):
                changed.append("requested_testing_rows")
        return tuple(dict.fromkeys(changed))

    def _build_case_review_item(
        self,
        intake_case: IntakeCase,
        draft: IntakeDraft,
        *,
        selected_asset: IntakeAsset | None,
    ) -> IntakeCaseReviewItem:
        """Build one review item from a case and draft."""
        draft_fields = self._merged_draft_fields(draft)
        overrides = self._json_object(draft.manual_overrides_json or "{}")
        raw_project_setup = overrides.get("project_setup")
        project_setup = (
            raw_project_setup
            if isinstance(raw_project_setup, dict)
            else self._default_project_setup(draft_fields)
        )
        precheck_issues = evaluate_section1_precheck(draft_fields)
        parsed_fields = clear_disallowed_section1_values(draft_fields)
        freeze_state = self._freeze_state(intake_case)
        return IntakeCaseReviewItem(
            case=intake_case,
            draft=draft,
            selected_asset=selected_asset,
            parsed_fields=parsed_fields,
            missing_required_fields=blocking_issue_fields(precheck_issues),
            precheck_issues=precheck_issues,
            project_setup=project_setup,
            base_editing_frozen=freeze_state,
            frozen_field_keys=self._frozen_field_keys if freeze_state else (),
            frozen_reason=self.FROZEN_REASON if freeze_state else None,
        )

    def _default_project_setup(self, draft_fields: dict[str, Any]) -> dict[str, str]:
        setup: dict[str, str] = {}
        sample_description = self._first_sample_product_name(draft_fields.get("samples"))
        test_item = self._first_requested_testing_cell(
            draft_fields.get("requested_testing_rows")
        )
        test_type_in_sheet = self._default_test_type_in_sheet_value(
            draft_fields.get("test_type"),
            test_item,
        )
        if sample_description is not None:
            setup["sample_description"] = sample_description
        if test_item is not None:
            setup["test_item"] = test_item
        setup["test_type_in_sheet"] = test_type_in_sheet
        return setup

    def _first_sample_product_name(self, samples: object) -> str | None:
        if not isinstance(samples, list) or not samples:
            return None
        for sample in samples:
            if not isinstance(sample, dict):
                continue
            text = self._text(sample.get("product_name"))
            if text is not None:
                return text
        return None

    def _first_requested_testing_cell(self, rows: object) -> str | None:
        if not isinstance(rows, list) or not rows:
            return None
        first_row = rows[0]
        if not isinstance(first_row, dict):
            return None
        return self._text(first_row.get("test_to_be_performed"))

    def _default_test_type_in_sheet_value(
        self,
        application_test_type: object,
        test_item: str | None,
    ) -> str:
        if self._text(application_test_type) == "Lab/Failure Analysis":
            return "Analysis"
        normalized_test_item = (test_item or "").casefold()
        for option in self._test_type_in_sheet_options:
            if option.casefold() in normalized_test_item:
                return option
        return self._default_test_type_in_sheet
