from __future__ import annotations

import json
from pathlib import Path

import pytest

from backend.application import IntakeConfirmationError, IntakeConfirmationService
from backend.domain import (
    ApplicationForm,
    FileAsset,
    IntakeAsset,
    IntakeAssetRole,
    IntakeCase,
    IntakeCaseStatus,
    IntakeDraft,
    IntakePackage,
    IntakePackageSourceType,
    IntakePackageStatus,
    Project,
    ProjectStatus,
    SampleInfo,
)


class Store:
    def __init__(self, items=None, key="id") -> None:
        self.key = key
        self.items = {getattr(item, key): item for item in items or []}

    def create(self, item):
        self.items[getattr(item, self.key)] = item
        return item

    def get(self, item_id):
        return self.items.get(item_id)

    def update(self, item):
        self.items[getattr(item, self.key)] = item
        return item

    def list_by_package(self, package_id):
        return [item for item in self.items.values() if item.package_id == package_id]

    def get_by_case(self, case_id):
        return next((item for item in self.items.values() if item.case_id == case_id), None)


def _package() -> IntakePackage:
    return IntakePackage(
        package_id="pkg-1",
        source_type=IntakePackageSourceType.OUTLOOK_MSG,
        status=IntakePackageStatus.READY_FOR_REVIEW,
        source_original_name="request.msg",
        source_stored_path=Path("data/intake/pkg-1/source/request.msg"),
    )


def _asset(asset_id: str = "asset-1") -> IntakeAsset:
    return IntakeAsset(
        asset_id=asset_id,
        package_id="pkg-1",
        original_name="application.docx",
        stored_path=Path("data/intake/pkg-1/attachments/application.docx"),
        extension=".docx",
        mime_type="application/octet-stream",
        size_bytes=100,
        sha256="a" * 64,
        asset_role=IntakeAssetRole.SELECTED_APPLICATION_FORM,
    )


def _case(status: IntakeCaseStatus = IntakeCaseStatus.NEEDS_REVIEW) -> IntakeCase:
    return IntakeCase(
        case_id="case-1",
        package_id="pkg-1",
        selected_form_asset_id="asset-1",
        status=status,
    )


def _draft(parsed_fields_json: str) -> IntakeDraft:
    return IntakeDraft(
        draft_id="draft-1",
        case_id="case-1",
        parsed_fields_json=parsed_fields_json,
    )


def _service(draft: IntakeDraft, case: IntakeCase | None = None) -> tuple[IntakeConfirmationService, dict[str, Store]]:
    stores = {
        "packages": Store([_package()], "package_id"),
        "intake_assets": Store([_asset(), _asset("supporting-1")], "asset_id"),
        "cases": Store([case or _case()], "case_id"),
        "drafts": Store([draft], "draft_id"),
        "projects": Store([], "project_id"),
        "forms": Store([], "form_id"),
        "samples": Store([], "sample_id"),
        "file_assets": Store([], "asset_id"),
    }
    return (
        IntakeConfirmationService(
            stores["packages"],
            stores["intake_assets"],
            stores["cases"],
            stores["drafts"],
            stores["projects"],
            stores["forms"],
            stores["samples"],
            stores["file_assets"],
        ),
        stores,
    )


def test_confirm_case_creates_project_records_and_marks_case_confirmed() -> None:
    service, stores = _service(
        _draft(_complete_section1_json(project_no="P-1", product_name="Connector"))
    )

    result = service.confirm_case("case-1")

    assert result.project.status is ProjectStatus.INTAKE_RECEIVED
    assert result.application_form.project_number == "P-1"
    assert result.sample_infos[0].part_number == "PN-1"
    assert len(result.file_assets) == 3
    assert stores["cases"].get("case-1").status is IntakeCaseStatus.CONFIRMED
    assert stores["cases"].get("case-1").confirmed_project_id == result.project.project_id
    assert len(stores["projects"].items) == 1
    assert len(stores["forms"].items) == 1
    assert len(stores["samples"].items) == 1


def test_confirm_case_rejects_missing_required_project_fields() -> None:
    service, _ = _service(_draft('{"project_no":"P-1","requester":"White"}'))

    with pytest.raises(IntakeConfirmationError, match="Product Name"):
        service.confirm_case("case-1")


def test_confirm_case_allows_missing_project_no() -> None:
    service, _ = _service(
        _draft(_complete_section1_json(project_no=None, product_name="Connector"))
    )

    result = service.confirm_case("case-1")

    assert result.project.project_no is None
    assert result.application_form.project_number is None


def test_confirm_case_rejects_unreviewed_or_already_confirmed_case() -> None:
    service, _ = _service(_draft("{}"), _case(IntakeCaseStatus.DRAFT_CREATED))
    with pytest.raises(IntakeConfirmationError):
        service.confirm_case("case-1")

    confirmed_case = IntakeCase(
        case_id="case-1",
        package_id="pkg-1",
        selected_form_asset_id="asset-1",
        status=IntakeCaseStatus.CONFIRMED,
        confirmed_project_id="project-1",
    )
    service, _ = _service(_draft("{}"), confirmed_case)
    with pytest.raises(IntakeConfirmationError):
        service.confirm_case("case-1")


def test_confirm_case_applies_manual_overrides() -> None:
    draft = IntakeDraft(
        draft_id="draft-1",
        case_id="case-1",
        parsed_fields_json=_complete_section1_json(project_no="P-1", product_name="Wrong"),
        manual_overrides_json='{"product_name":"Correct"}',
    )
    service, _ = _service(draft)

    result = service.confirm_case("case-1")

    assert result.project.product_name == "Correct"


def _complete_section1_json(
    *,
    project_no: str | None,
    product_name: str,
) -> str:
    data = {
        "project_no": project_no,
        "form_no": "E-3718",
        "revision": "H",
        "product_name": product_name,
        "requester": "White",
        "phone": "555-0100",
        "request_date": "2026-05-03",
        "email": "white@example.com",
        "business_unit": "BU",
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
                "product_name": product_name,
                "part_number": "PN-1",
                "lot_or_traceability": "LOT-1",
                "material": "Copper",
                "plating": "Ag",
                "housing_material": "PA10T",
                "quantity": 2,
            }
        ],
    }
    return json.dumps(data)
