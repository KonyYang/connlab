from __future__ import annotations

import json
from pathlib import Path

import pytest

from backend.application import (
    IntakeCaseReviewNotFoundError,
    IntakeCaseReviewService,
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


class PackageStore:
    """In-memory package read store."""

    def __init__(self, package: IntakePackage | None = None) -> None:
        self.items = {package.package_id: package} if package else {}

    def get(self, package_id: str) -> IntakePackage | None:
        return self.items.get(package_id)


class AssetStore:
    """In-memory asset read store."""

    def __init__(self, *assets: IntakeAsset) -> None:
        self.items = {asset.asset_id: asset for asset in assets}

    def get(self, asset_id: str) -> IntakeAsset | None:
        return self.items.get(asset_id)


class CaseStore:
    """In-memory case read store."""

    def __init__(self, *cases: IntakeCase) -> None:
        self.items = list(cases)

    def get(self, case_id: str) -> IntakeCase | None:
        return next((case for case in self.items if case.case_id == case_id), None)

    def list_by_package(self, package_id: str) -> list[IntakeCase]:
        return [case for case in self.items if case.package_id == package_id]


class DraftStore:
    """In-memory draft read store."""

    def __init__(self, *drafts: IntakeDraft) -> None:
        self.items = {draft.case_id: draft for draft in drafts}

    def get_by_case(self, case_id: str) -> IntakeDraft | None:
        return self.items.get(case_id)

    def update(self, draft: IntakeDraft) -> IntakeDraft:
        self.items[draft.case_id] = draft
        return draft


def test_review_service_returns_complete_case_without_blockers(tmp_path: Path) -> None:
    """Complete draft data is reviewable and has no required blockers."""
    service = _service(
        _package(tmp_path),
        _asset(tmp_path),
        _case(),
        _draft(
            {
                **_complete_section1_fields(),
                "product_name": "Connector sample",
                "project_no": "Legacy-01",
            }
        ),
    )

    review = service.get_package_review("pkg-1")

    assert review.package.package_id == "pkg-1"
    assert len(review.cases) == 1
    item = review.cases[0]
    assert item.selected_asset is not None
    assert item.selected_asset.original_name == "request.docx"
    assert item.parsed_fields["product_name"] == "Connector sample"
    assert item.missing_required_fields == ()
    assert item.precheck_issues == ()


def test_review_service_reports_missing_required_fields(tmp_path: Path) -> None:
    """Blank product and requester stay visible as confirmation blockers."""
    service = _service(
        _package(tmp_path),
        _asset(tmp_path),
        _case(),
        _draft({"product_name": " ", "requester": ""}),
    )

    review = service.get_package_review("pkg-1")

    assert "product_name" in review.cases[0].missing_required_fields
    assert "requester" in review.cases[0].missing_required_fields


def test_review_service_applies_manual_overrides(tmp_path: Path) -> None:
    """Operator overrides participate in required field readiness."""
    service = _service(
        _package(tmp_path),
        _asset(tmp_path),
        _case(),
        _draft(
            {"product_name": "", "requester": ""},
            overrides={**_complete_section1_fields(), "product_name": "Corrected connector", "requester": "White"},
        ),
    )

    review = service.get_package_review("pkg-1")

    assert review.cases[0].parsed_fields["product_name"] == "Corrected connector"
    assert review.cases[0].parsed_fields["requester"] == "White"
    assert review.cases[0].missing_required_fields == ()


def test_review_service_updates_operator_overrides(tmp_path: Path) -> None:
    """Operator field corrections are persisted as manual draft overrides."""
    service = _service(
        _package(tmp_path),
        _asset(tmp_path),
        _case(),
        _draft(_complete_section1_fields() | {"product_name": "", "requester": ""}),
    )

    item = service.update_case_fields(
        "case-1",
        {
            "product_name": "Corrected connector",
            "requester": "White",
            "unknown": "ignored",
        },
    )

    assert item.parsed_fields["product_name"] == "Corrected connector"
    assert item.parsed_fields["requester"] == "White"
    assert "unknown" not in item.parsed_fields
    assert item.missing_required_fields == ()


def test_review_service_updates_sample_rows_as_manual_overrides(tmp_path: Path) -> None:
    """Operator sample row corrections are persisted for project confirmation."""
    service = _service(
        _package(tmp_path),
        _asset(tmp_path),
        _case(),
        _draft(
            {
                **_complete_section1_fields(),
                "product_name": "Connector",
                "samples": [{"part_number": "OLD"}],
            }
        ),
    )

    item = service.update_case_fields(
        "case-1",
        {},
        sample_rows=[
            {
                "product_name": "Connector A",
                "part_number": "PN-100",
                "quantity": "20 pcs",
                "empty": "",
            }
        ],
    )

    assert item.parsed_fields["samples"] == [
        {
            "product_name": "Connector A",
            "part_number": "PN-100",
            "quantity": "20 pcs",
        }
    ]


def test_review_service_section1_precheck_warns_without_blocking_project_no_and_ltr(
    tmp_path: Path,
) -> None:
    """Project # and prefilled Lab Test Request Number are warnings, not blockers."""
    service = _service(
        _package(tmp_path),
        _asset(tmp_path),
        _case(),
        _draft(
            {
                **_complete_section1_fields(),
                "project_no": "",
                "lab_test_request_number": "LTR-001",
            }
        ),
    )

    item = service.get_package_review("pkg-1").cases[0]

    assert item.missing_required_fields == ()
    assert item.parsed_fields["lab_test_request_number"] == ""
    assert {issue.field_key for issue in item.precheck_issues} == {
        "project_no",
        "lab_test_request_number",
    }
    assert {issue.level for issue in item.precheck_issues} == {"warning"}


def test_review_service_excludes_section2_lab_fields_from_preproject_check(
    tmp_path: Path,
) -> None:
    """Lab section fields are excluded from Project confirmation precheck."""
    fields = _complete_section1_fields()
    fields.update(
        {
            "lab": "",
            "assigned_personnel": "",
            "received_date": "",
            "estimated_completion_date": "",
            "sample_condition": "",
        }
    )
    service = _service(_package(tmp_path), _asset(tmp_path), _case(), _draft(fields))

    item = service.get_package_review("pkg-1").cases[0]

    assert item.missing_required_fields == ()
    assert all("estimated_completion_date" != issue.field_key for issue in item.precheck_issues)


def test_review_service_raises_for_missing_package(tmp_path: Path) -> None:
    """Unknown package IDs fail explicitly."""
    service = _service(None, _asset(tmp_path), _case(), _draft({}))

    with pytest.raises(IntakeCaseReviewNotFoundError):
        service.get_package_review("pkg-1")


def _service(
    package: IntakePackage | None,
    asset: IntakeAsset,
    case: IntakeCase,
    draft: IntakeDraft,
) -> IntakeCaseReviewService:
    return IntakeCaseReviewService(
        PackageStore(package),
        AssetStore(asset),
        CaseStore(case),
        DraftStore(draft),
    )


def _package(tmp_path: Path) -> IntakePackage:
    return IntakePackage(
        package_id="pkg-1",
        source_type=IntakePackageSourceType.MANUAL,
        status=IntakePackageStatus.READY_FOR_REVIEW,
        source_original_name="manual-intake.json",
        source_stored_path=tmp_path / "manual-intake.json",
    )


def _asset(tmp_path: Path) -> IntakeAsset:
    return IntakeAsset(
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


def _case() -> IntakeCase:
    return IntakeCase(
        case_id="case-1",
        package_id="pkg-1",
        selected_form_asset_id="asset-1",
        status=IntakeCaseStatus.NEEDS_REVIEW,
    )


def _draft(
    fields: dict[str, object],
    *,
    overrides: dict[str, object] | None = None,
) -> IntakeDraft:
    return IntakeDraft(
        draft_id="draft-1",
        case_id="case-1",
        parsed_fields_json=json.dumps(fields),
        manual_overrides_json=json.dumps(overrides) if overrides else None,
    )


def _complete_section1_fields() -> dict[str, object]:
    return {
        "form_no": "E-3718",
        "revision": "H",
        "product_name": "Connector",
        "requester": "White",
        "phone": "555-0100",
        "request_date": "2026-05-03",
        "email": "white@example.com",
        "business_unit": "Power Solutions",
        "manufacturing_site": "Nantong",
        "results_format": "Formal Report (Customer)",
        "requested_completion_date": "2026-05-10",
        "test_type": "Customer Specific Testing",
        "sample_status": "Production",
        "project_type": "New Product Development",
        "requested_testing": "Bend testing",
        "post_testing_disposition": "Keep in the Lab",
        "confidential": "No",
        "subcontract": "Yes",
        "send_copies_recipients": "Neo Xu",
        "samples": [
            {
                "product_name": "Connector",
                "part_number": "PN-100 revA",
                "lot_or_traceability": "LOT-1",
                "material": "Copper",
                "plating": "Ag",
                "housing_material": "PA10T",
                "quantity": "20 pcs",
            }
        ],
    }
