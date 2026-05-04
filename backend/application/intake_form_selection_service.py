from __future__ import annotations

import json
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Protocol
from uuid import uuid4

from backend.application.application_form_eligibility_service import (
    ApplicationFormEligibility,
    ApplicationFormEligibilityService,
)
from backend.domain import (
    IntakeAsset,
    IntakeAssetRole,
    IntakeCase,
    IntakeCaseStatus,
    IntakeDraft,
    IntakePackage,
)
from backend.modules.intake import ApplicationFormParser, ParsedApplicationForm


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


class ApplicationFormEligibilityValidator(Protocol):
    """Port for checking whether an intake asset can be selected for Precheck."""

    def evaluate(self, asset: IntakeAsset) -> ApplicationFormEligibility: ...


@dataclass(frozen=True)
class FormSelectionResult:
    package_id: str
    case: IntakeCase
    draft: IntakeDraft
    selected_asset: IntakeAsset


@dataclass(frozen=True)
class _CaseSelection:
    """Selected or reused case plus whether it already belonged to this asset."""

    case: IntakeCase
    same_selected_asset: bool


class IntakeFormSelectionService:
    """Creates review records after a human selects one application form asset."""

    _word_extensions = {".docx"}
    _blocked_roles = {IntakeAssetRole.EMAIL_SOURCE, IntakeAssetRole.IGNORED}

    def __init__(
        self,
        package_store: IntakePackageStore,
        asset_store: IntakeAssetStore,
        case_store: IntakeCaseStore,
        draft_store: IntakeDraftStore,
        parser: ApplicationFormParser | None = None,
        eligibility_validator: ApplicationFormEligibilityValidator | None = None,
    ) -> None:
        """Create the selection service from explicit stores and parser."""
        self._package_store = package_store
        self._asset_store = asset_store
        self._case_store = case_store
        self._draft_store = draft_store
        self._parser = parser or ApplicationFormParser()
        self._eligibility_validator = (
            eligibility_validator or ApplicationFormEligibilityService()
        )

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
        eligibility = self._eligibility_validator.evaluate(asset)
        if not eligibility.eligible:
            raise IntakeSelectionError(eligibility.message)

        selected_asset = self._asset_store.update(
            replace(asset, asset_role=IntakeAssetRole.SELECTED_APPLICATION_FORM)
        )
        case_selection = self._create_or_update_case(package.package_id, selected_asset.asset_id)
        draft_payload, parser_warnings = self._parse_selected_asset(selected_asset)
        draft = self._create_or_update_draft(
            case_selection.case.case_id,
            draft_payload,
            parser_warnings,
            keep_manual_overrides=case_selection.same_selected_asset,
        )

        return FormSelectionResult(
            package_id=package.package_id,
            case=case_selection.case,
            draft=draft,
            selected_asset=selected_asset,
        )

    def _is_selectable_application_form(self, asset: IntakeAsset) -> bool:
        if asset.asset_role in self._blocked_roles:
            return False
        if asset.asset_role is IntakeAssetRole.APPLICATION_FORM_CANDIDATE:
            return True
        return self._normalized_extension(asset) in self._word_extensions

    def _create_or_update_case(self, package_id: str, selected_asset_id: str) -> _CaseSelection:
        existing_cases = self._case_store.list_by_package(package_id)
        for current in existing_cases:
            if (
                current.selected_form_asset_id == selected_asset_id
                and self._can_reuse_case(current)
            ):
                return _CaseSelection(
                    case=self._case_store.update(
                        replace(
                            current,
                            status=IntakeCaseStatus.NEEDS_REVIEW,
                            confirmed_project_id=None,
                        )
                    ),
                    same_selected_asset=True,
                )
        reusable_cases = [
            case
            for case in existing_cases
            if self._can_reuse_case(case)
        ]
        if reusable_cases:
            current = reusable_cases[0]
            return _CaseSelection(
                case=self._case_store.update(
                    replace(
                        current,
                        selected_form_asset_id=selected_asset_id,
                        status=IntakeCaseStatus.NEEDS_REVIEW,
                        confirmed_project_id=None,
                    )
                ),
                same_selected_asset=False,
            )
        return _CaseSelection(
            case=self._case_store.create(
                IntakeCase(
                    case_id=f"case-{uuid4().hex}",
                    package_id=package_id,
                    selected_form_asset_id=selected_asset_id,
                    status=IntakeCaseStatus.NEEDS_REVIEW,
                )
            ),
            same_selected_asset=False,
        )

    def _can_reuse_case(self, case: IntakeCase) -> bool:
        """Return whether an intake case can be rebound before project confirmation."""
        return (
            case.confirmed_project_id is None
            and case.status is not IntakeCaseStatus.CONFIRMED
        )

    def _create_or_update_draft(
        self,
        case_id: str,
        parsed_fields: dict[str, object],
        parser_warnings: list[str],
        keep_manual_overrides: bool,
    ) -> IntakeDraft:
        existing_draft = self._draft_store.get_by_case(case_id)
        parsed_fields_json = json.dumps(parsed_fields, ensure_ascii=False, sort_keys=True)
        parser_warnings_json = json.dumps(parser_warnings, ensure_ascii=False)
        if existing_draft is not None:
            manual_overrides_json = (
                existing_draft.manual_overrides_json if keep_manual_overrides else None
            )
            return self._draft_store.update(
                replace(
                    existing_draft,
                    parsed_fields_json=parsed_fields_json,
                    parser_warnings_json=parser_warnings_json,
                    manual_overrides_json=manual_overrides_json,
                )
            )
        return self._draft_store.create(
            IntakeDraft(
                draft_id=f"draft-{uuid4().hex}",
                case_id=case_id,
                parsed_fields_json=parsed_fields_json,
                parser_warnings_json=parser_warnings_json,
            )
        )

    def _parse_selected_asset(self, asset: IntakeAsset) -> tuple[dict[str, object], list[str]]:
        """Parse the selected application form into review draft fields."""
        if self._normalized_extension(asset) != ".docx":
            return {}, ["Only .docx selected forms can be parsed for Precheck draft fields."]
        try:
            parsed = self._parser.parse(asset.stored_path)
        except Exception as exc:  # pragma: no cover - defensive boundary for corrupt Word files
            return {}, [f"Selected application form could not be parsed: {exc}"]
        return self._draft_payload(parsed), []

    def _draft_payload(self, parsed: ParsedApplicationForm) -> dict[str, object]:
        """Convert parser output into the draft fields consumed by Precheck review."""
        first_sample = parsed.samples[0] if parsed.samples else None
        return {
            "form_no": self._clean(parsed.form_no),
            "revision": self._clean(parsed.form_rev),
            "reference_doc": self._clean(parsed.reference_doc),
            "lab_test_request_number": self._clean(parsed.lab_test_request_number),
            "requester": self._clean(parsed.requested_by),
            "phone": self._clean(parsed.phone),
            "request_date": self._clean(parsed.request_date),
            "email": self._clean(parsed.email),
            "business_unit": self._clean(parsed.business_unit),
            "manufacturing_site": self._clean(parsed.manufacturing_site),
            "project_no": self._clean(parsed.project_number),
            "requested_completion_date": self._clean(parsed.requested_completion_date),
            "results_format": self._clean(parsed.results_format),
            "test_type": self._clean(parsed.test_type),
            "sample_status": self._clean(parsed.sample_status),
            "project_type": self._clean(parsed.project_type),
            "post_testing_disposition": self._clean(parsed.post_testing_disposition),
            "requested_testing": self._clean(parsed.requested_testing_description),
            "requested_testing_rows": [
                {
                    "test_to_be_performed": self._clean(row.test_to_be_performed),
                    "applicable_specification": self._clean(row.applicable_specification),
                }
                for row in parsed.requested_testing_rows
            ],
            "confidential": self._clean(parsed.confidential),
            "subcontract": self._clean(parsed.subcontract),
            "additional_information": self._clean(parsed.additional_information),
            "send_copies_recipients": self._clean(parsed.send_copies_recipients),
            "product_name": self._clean(first_sample.product_name if first_sample else None),
            "samples": [
                {
                    "product_name": self._clean(sample.product_name),
                    "part_number": self._clean(sample.part_number),
                    "revision": self._clean(sample.revision),
                    "lot_or_traceability": self._clean(sample.lot_or_traceability),
                    "material": self._clean(sample.material),
                    "plating": self._clean(sample.plating),
                    "lubricant": self._clean(sample.lubricant),
                    "housing_material": self._clean(sample.housing_material),
                    "quantity": self._clean(sample.quantity),
                }
                for sample in parsed.samples
            ],
        }

    def _normalized_extension(self, asset: IntakeAsset) -> str:
        extension = asset.extension or Path(asset.original_name).suffix
        extension = extension.lower()
        if extension and not extension.startswith("."):
            return f".{extension}"
        return extension

    def _clean(self, value: object | None) -> str | None:
        """Normalize parser values for draft JSON."""
        if value is None:
            return None
        text = str(value).strip()
        return text or None
