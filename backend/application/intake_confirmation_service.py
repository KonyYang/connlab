from __future__ import annotations

import json
import re
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Protocol
from uuid import uuid4

from backend.application.intake_section1_precheck import evaluate_section1_precheck
from backend.domain import (
    ApplicationForm,
    FileAsset,
    FileAssetType,
    IntakeAsset,
    IntakeCase,
    IntakeCaseStatus,
    IntakeDraft,
    IntakePackage,
    Project,
    ProjectStatus,
    SampleInfo,
)


class IntakeConfirmationError(ValueError):
    """Raised when an intake case cannot be confirmed into a project."""


class IntakeConfirmationNotFoundError(LookupError):
    """Raised when confirmation prerequisites cannot be found."""


class IntakePackageStore(Protocol):
    def get(self, package_id: str) -> IntakePackage | None: ...


class IntakeAssetStore(Protocol):
    def get(self, asset_id: str) -> IntakeAsset | None: ...

    def list_by_package(self, package_id: str) -> list[IntakeAsset]: ...


class IntakeCaseStore(Protocol):
    def get(self, case_id: str) -> IntakeCase | None: ...

    def update(self, case: IntakeCase) -> IntakeCase: ...


class IntakeDraftStore(Protocol):
    def get_by_case(self, case_id: str) -> IntakeDraft | None: ...


class ProjectStore(Protocol):
    def create(self, project: Project) -> Project: ...


class ApplicationFormStore(Protocol):
    def create(self, form: ApplicationForm) -> ApplicationForm: ...


class SampleInfoStore(Protocol):
    def create(self, sample: SampleInfo) -> SampleInfo: ...


class FileAssetStore(Protocol):
    def create(self, asset: FileAsset) -> FileAsset: ...


@dataclass(frozen=True)
class IntakeConfirmationResult:
    project: Project
    application_form: ApplicationForm
    sample_infos: tuple[SampleInfo, ...]
    file_assets: tuple[FileAsset, ...]
    intake_case: IntakeCase


class IntakeConfirmationService:
    """Confirms reviewed intake draft data into formal MVP project records."""

    def __init__(
        self,
        package_store: IntakePackageStore,
        intake_asset_store: IntakeAssetStore,
        intake_case_store: IntakeCaseStore,
        intake_draft_store: IntakeDraftStore,
        project_store: ProjectStore,
        application_form_store: ApplicationFormStore,
        sample_store: SampleInfoStore,
        file_asset_store: FileAssetStore,
    ) -> None:
        self._package_store = package_store
        self._intake_asset_store = intake_asset_store
        self._intake_case_store = intake_case_store
        self._intake_draft_store = intake_draft_store
        self._project_store = project_store
        self._application_form_store = application_form_store
        self._sample_store = sample_store
        self._file_asset_store = file_asset_store

    def confirm_case(self, case_id: str) -> IntakeConfirmationResult:
        intake_case = self._get_case(case_id)
        if intake_case.status is not IntakeCaseStatus.NEEDS_REVIEW:
            raise IntakeConfirmationError("Only reviewed intake cases can be confirmed.")
        if intake_case.confirmed_project_id:
            raise IntakeConfirmationError("Intake case is already confirmed.")

        package = self._get_package(intake_case.package_id)
        selected_asset = self._get_selected_asset(intake_case)
        draft = self._get_draft(intake_case.case_id)
        draft_data = self._merged_draft_data(draft)
        self._validate_required_fields(draft_data)

        project_id = uuid4().hex
        project = self._project_store.create(self._to_project(project_id, draft_data))
        form = self._application_form_store.create(
            self._to_application_form(project.project_id, draft_data)
        )
        samples = tuple(
            self._sample_store.create(sample)
            for sample in self._to_sample_infos(project.project_id, draft_data)
        )
        assets = tuple(
            self._file_asset_store.create(asset)
            for asset in self._to_file_assets(project.project_id, package, selected_asset)
        )
        confirmed_case = self._intake_case_store.update(
            replace(
                intake_case,
                status=IntakeCaseStatus.CONFIRMED,
                confirmed_project_id=project.project_id,
            )
        )

        return IntakeConfirmationResult(
            project=project,
            application_form=form,
            sample_infos=samples,
            file_assets=assets,
            intake_case=confirmed_case,
        )

    def _get_case(self, case_id: str) -> IntakeCase:
        intake_case = self._intake_case_store.get(case_id)
        if intake_case is None:
            raise IntakeConfirmationNotFoundError(f"Intake case not found: {case_id}")
        return intake_case

    def _get_package(self, package_id: str) -> IntakePackage:
        package = self._package_store.get(package_id)
        if package is None:
            raise IntakeConfirmationNotFoundError(f"Intake package not found: {package_id}")
        return package

    def _get_selected_asset(self, intake_case: IntakeCase) -> IntakeAsset:
        if not intake_case.selected_form_asset_id:
            raise IntakeConfirmationError("Intake case has no selected application form asset.")
        asset = self._intake_asset_store.get(intake_case.selected_form_asset_id)
        if asset is None:
            raise IntakeConfirmationNotFoundError(
                f"Selected intake asset not found: {intake_case.selected_form_asset_id}"
            )
        if asset.package_id != intake_case.package_id:
            raise IntakeConfirmationError("Selected asset does not belong to the intake package.")
        return asset

    def _get_draft(self, case_id: str) -> IntakeDraft:
        draft = self._intake_draft_store.get_by_case(case_id)
        if draft is None:
            raise IntakeConfirmationNotFoundError(f"Intake draft not found for case: {case_id}")
        return draft

    def _merged_draft_data(self, draft: IntakeDraft) -> dict[str, Any]:
        parsed = self._load_json_object(draft.parsed_fields_json, "parsed_fields_json")
        overrides = (
            self._load_json_object(draft.manual_overrides_json, "manual_overrides_json")
            if draft.manual_overrides_json
            else {}
        )
        return {**parsed, **{key: value for key, value in overrides.items() if value not in (None, "")}}

    def _load_json_object(self, raw: str, field_name: str) -> dict[str, Any]:
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise IntakeConfirmationError(f"{field_name} must be valid JSON.") from exc
        if not isinstance(value, dict):
            raise IntakeConfirmationError(f"{field_name} must be a JSON object.")
        return value

    def _validate_required_fields(self, data: dict[str, Any]) -> None:
        blockers = [
            issue.message
            for issue in evaluate_section1_precheck(data)
            if issue.level == "error"
        ]
        if blockers:
            raise IntakeConfirmationError(
                "SECTION 1 precheck blockers: " + "; ".join(blockers)
            )

    def _to_project(self, project_id: str, data: dict[str, Any]) -> Project:
        return Project(
            project_id=project_id,
            project_no=self._optional_text(data, "project_no"),
            product_name=self._text(data, "product_name"),
            requestor=self._text(data, "requester"),
            status=ProjectStatus.INTAKE_RECEIVED,
            business_unit=self._optional_text(data, "business_unit"),
        )

    def _to_application_form(self, project_id: str, data: dict[str, Any]) -> ApplicationForm:
        return ApplicationForm(
            form_id=uuid4().hex,
            project_id=project_id,
            form_no=self._optional_text(data, "form_no") or "UNCONFIRMED",
            revision=self._optional_text(data, "revision") or "UNCONFIRMED",
            requester=self._text(data, "requester"),
            phone=self._optional_text(data, "phone"),
            email=self._optional_text(data, "email"),
            business_unit=self._optional_text(data, "business_unit"),
            manufacturing_site=self._optional_text(data, "manufacturing_site"),
            requested_testing=self._optional_text(data, "requested_testing"),
            subcontract_allowed=self._optional_bool(data, "subcontract"),
            reference_doc=self._optional_text(data, "reference_doc"),
            lab_test_request_number=self._optional_text(data, "lab_test_request_number"),
            project_number=self._optional_text(data, "project_no"),
            requested_completion_date=self._optional_text(data, "requested_completion_date"),
            results_format=self._optional_text(data, "results_format"),
            test_type=self._optional_text(data, "test_type"),
            sample_status=self._optional_text(data, "sample_status"),
            project_type=self._optional_text(data, "project_type"),
            post_testing_disposition=self._optional_text(data, "post_testing_disposition"),
            confidential=self._optional_text(data, "confidential"),
            subcontract=self._optional_text(data, "subcontract"),
            additional_information=self._optional_text(data, "additional_information"),
            send_copies_recipients=self._optional_text(data, "send_copies_recipients"),
            lab=self._optional_text(data, "lab"),
            assigned_personnel=self._optional_text(data, "assigned_personnel"),
            received_date=self._optional_text(data, "received_date"),
            estimated_completion_date=self._optional_text(data, "estimated_completion_date"),
            sample_condition=self._optional_text(data, "sample_condition"),
        )

    def _to_sample_infos(self, project_id: str, data: dict[str, Any]) -> tuple[SampleInfo, ...]:
        rows = data.get("samples")
        if not isinstance(rows, list):
            rows = [{}]
        samples: list[SampleInfo] = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            samples.append(
                SampleInfo(
                    sample_id=uuid4().hex,
                    project_id=project_id,
                    product_name=self._optional_text(row, "product_name")
                    or self._text(data, "product_name"),
                    part_number=self._optional_text(row, "part_number") or "UNCONFIRMED",
                    revision=self._optional_text(row, "revision"),
                    lot_or_traceability=self._optional_text(row, "lot_or_traceability"),
                    material=self._optional_text(row, "material"),
                    plating=self._optional_text(row, "plating"),
                    housing_material=self._optional_text(row, "housing_material"),
                    quantity=self._optional_int(row, "quantity"),
                )
            )
        return tuple(samples)

    def _to_file_assets(
        self,
        project_id: str,
        package: IntakePackage,
        selected_asset: IntakeAsset,
    ) -> tuple[FileAsset, ...]:
        assets = [
            FileAsset(
                asset_id=uuid4().hex,
                project_id=project_id,
                asset_type=FileAssetType.APPLICATION_FORM,
                path=selected_asset.stored_path,
                original_name=selected_asset.original_name,
                source_package_id=package.package_id,
                source_intake_asset_id=selected_asset.asset_id,
                source_role="selected_application_form",
                sha256=selected_asset.sha256,
            ),
            FileAsset(
                asset_id=uuid4().hex,
                project_id=project_id,
                asset_type=FileAssetType.ATTACHMENT,
                path=package.source_stored_path,
                original_name=package.source_original_name,
                source_package_id=package.package_id,
                source_role="email_source",
            ),
        ]
        for asset in self._intake_asset_store.list_by_package(package.package_id):
            if asset.asset_id == selected_asset.asset_id:
                continue
            assets.append(
                FileAsset(
                    asset_id=uuid4().hex,
                    project_id=project_id,
                    asset_type=FileAssetType.ATTACHMENT,
                    path=asset.stored_path,
                    original_name=asset.original_name,
                    source_package_id=package.package_id,
                    source_intake_asset_id=asset.asset_id,
                    source_role=asset.asset_role.value,
                    sha256=asset.sha256,
                )
            )
        return _dedupe_file_assets(assets)

    def _text(self, data: dict[str, Any], key: str) -> str:
        value = self._optional_text(data, key)
        if value is None:
            raise IntakeConfirmationError(f"Missing required field: {key}")
        return value

    def _optional_text(self, data: dict[str, Any], key: str) -> str | None:
        value = data.get(key)
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    def _optional_int(self, data: dict[str, Any], key: str) -> int | None:
        value = data.get(key)
        if value in (None, ""):
            return None
        if isinstance(value, str):
            match = re.search(r"\d+", value)
            if match:
                return int(match.group(0))
        try:
            return int(value)
        except (TypeError, ValueError) as exc:
            raise IntakeConfirmationError(f"{key} must be an integer.") from exc

    def _optional_bool(self, data: dict[str, Any], key: str) -> bool | None:
        value = self._optional_text(data, key)
        if value is None:
            return None
        lowered = value.lower()
        if lowered in {"yes", "y", "true", "1", "allowed"}:
            return True
        if lowered in {"no", "n", "false", "0", "not allowed"}:
            return False
        return None


def _dedupe_file_assets(assets: list[FileAsset]) -> tuple[FileAsset, ...]:
    """Return one project file asset per canonical source path with best provenance."""
    best_by_key: dict[str, FileAsset] = {}
    for asset in assets:
        key = _canonical_path_key(asset.path)
        current = best_by_key.get(key)
        if current is None or _role_priority(asset.source_role) < _role_priority(current.source_role):
            best_by_key[key] = asset
    return tuple(best_by_key.values())


def _canonical_path_key(path: Path) -> str:
    """Return a stable, case-insensitive source path key."""
    return str(path).replace("/", "\\").casefold()


def _role_priority(role: str | None) -> int:
    """Return lower numbers for higher-confidence source roles."""
    return {
        "selected_application_form": 0,
        "email_source": 1,
        "supporting_attachment": 2,
        "specification": 3,
    }.get(role or "", 10)
