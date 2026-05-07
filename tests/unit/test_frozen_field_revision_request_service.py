from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

from backend.application.frozen_field_revision_request_service import (
    FrozenFieldRevisionRequestService,
    FrozenFieldRevisionRequestValidationError,
)
from backend.application.intake_case_review_service import IntakeCaseReviewService
from backend.domain import (
    FrozenFieldRevisionRequest,
    FrozenFieldRevisionRequestStatus,
    IntakeAsset,
    IntakeAssetRole,
    IntakeCase,
    IntakeCaseStatus,
    IntakeDraft,
    IntakePackage,
    IntakePackageSourceType,
    IntakePackageStatus,
    LtrRecord,
    LtrStatus,
)


class RequestStore:
    def __init__(self) -> None:
        self.items: dict[str, FrozenFieldRevisionRequest] = {}

    def create(self, request: FrozenFieldRevisionRequest) -> FrozenFieldRevisionRequest:
        self.items[request.request_id] = request
        return request

    def get(self, request_id: str) -> FrozenFieldRevisionRequest | None:
        return self.items.get(request_id)

    def list_by_case(self, case_id: str) -> list[FrozenFieldRevisionRequest]:
        return [item for item in self.items.values() if item.intake_case_id == case_id]

    def list_by_project(self, project_id: str) -> list[FrozenFieldRevisionRequest]:
        return [item for item in self.items.values() if item.project_id == project_id]


class PackageStore:
    def __init__(self, package: IntakePackage) -> None:
        self.package = package

    def get(self, package_id: str) -> IntakePackage | None:
        return self.package if self.package.package_id == package_id else None


class AssetStore:
    def __init__(self, asset: IntakeAsset) -> None:
        self.asset = asset

    def get(self, asset_id: str) -> IntakeAsset | None:
        return self.asset if self.asset.asset_id == asset_id else None


class CaseStore:
    def __init__(self, case: IntakeCase) -> None:
        self.case = case

    def get(self, case_id: str) -> IntakeCase | None:
        return self.case if self.case.case_id == case_id else None

    def list_by_package(self, package_id: str) -> list[IntakeCase]:
        return [self.case] if self.case.package_id == package_id else []


class DraftStore:
    def __init__(self, draft: IntakeDraft) -> None:
        self.draft = draft

    def get_by_case(self, case_id: str) -> IntakeDraft | None:
        return self.draft if self.draft.case_id == case_id else None

    def update(self, draft: IntakeDraft) -> IntakeDraft:
        self.draft = draft
        return draft


class LtrStore:
    def __init__(self, *records: LtrRecord) -> None:
        self.records = list(records)

    def list_by_project(self, project_id: str) -> list[LtrRecord]:
        return [record for record in self.records if record.project_id == project_id]


def test_create_request_records_backend_current_value_snapshot(tmp_path: Path) -> None:
    service = _service(tmp_path, frozen=True)

    request = service.create_request(
        "case-1",
        reason="Corrected by customer clarification.",
        requested_by="White",
        changes=[{"field_key": "product_name", "proposed_value": "Connector X"}],
    )

    assert request.status is FrozenFieldRevisionRequestStatus.REQUESTED
    assert request.intake_case_id == "case-1"
    assert request.project_id == "project-1"
    assert request.ltr_number == "DL-2026-05-001"
    changes = json.loads(request.field_changes_json)
    assert changes[0]["field_key"] == "product_name"
    assert changes[0]["current_value"] == "Connector sample"
    assert changes[0]["proposed_value"] == "Connector X"


def test_create_request_rejects_non_frozen_case(tmp_path: Path) -> None:
    service = _service(tmp_path, frozen=False)

    with pytest.raises(FrozenFieldRevisionRequestValidationError) as exc_info:
        service.create_request(
            "case-1",
            reason="Need update",
            requested_by=None,
            changes=[{"field_key": "product_name", "proposed_value": "Connector X"}],
        )

    assert "not frozen" in str(exc_info.value)


def test_create_request_rejects_non_frozen_field_key(tmp_path: Path) -> None:
    service = _service(tmp_path, frozen=True)

    with pytest.raises(FrozenFieldRevisionRequestValidationError) as exc_info:
        service.create_request(
            "case-1",
            reason="Need update",
            requested_by=None,
            changes=[{"field_key": "additional_information", "proposed_value": "Note"}],
        )

    assert "not an allowed frozen field" in str(exc_info.value)


def _service(tmp_path: Path, *, frozen: bool) -> FrozenFieldRevisionRequestService:
    package = IntakePackage(
        package_id="pkg-1",
        source_type=IntakePackageSourceType.MANUAL,
        status=IntakePackageStatus.READY_FOR_REVIEW,
        source_original_name="manual-intake.json",
        source_stored_path=tmp_path / "manual-intake.json",
    )
    asset = IntakeAsset(
        asset_id="asset-1",
        package_id="pkg-1",
        original_name="request.docx",
        stored_path=tmp_path / "request.docx",
        extension=".docx",
        mime_type=None,
        size_bytes=12,
        sha256="abc",
        asset_role=IntakeAssetRole.SELECTED_APPLICATION_FORM,
    )
    case = IntakeCase(
        case_id="case-1",
        package_id="pkg-1",
        selected_form_asset_id="asset-1",
        status=IntakeCaseStatus.NEEDS_REVIEW,
        confirmed_project_id="project-1" if frozen else None,
    )
    draft = IntakeDraft(
        draft_id="draft-1",
        case_id="case-1",
        parsed_fields_json=json.dumps({"product_name": "Connector sample", "requester": "White"}),
    )
    ltr_records: tuple[LtrRecord, ...] = ()
    if frozen:
        ltr_records = (
            LtrRecord(
                ltr_id="ltr-1",
                project_id="project-1",
                ltr_number="DL-2026-05-001",
                status=LtrStatus.REGISTERED,
                registered_on=date(2026, 5, 7),
            ),
        )
    review_service = IntakeCaseReviewService(
        PackageStore(package),
        AssetStore(asset),
        CaseStore(case),
        DraftStore(draft),
        ltr_store=LtrStore(*ltr_records),
    )
    return FrozenFieldRevisionRequestService(
        request_store=RequestStore(),
        review_service=review_service,
        ltr_store=LtrStore(*ltr_records),
    )
