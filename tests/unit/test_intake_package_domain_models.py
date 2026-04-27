from pathlib import Path

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


def test_intake_package_domain_defaults_keep_human_review_state() -> None:
    package = IntakePackage(
        package_id="pkg-1",
        source_type=IntakePackageSourceType.OUTLOOK_MSG,
        status=IntakePackageStatus.IMPORTED,
        source_original_name="request.msg",
        source_stored_path=Path("data/intake/pkg-1/source/request.msg"),
    )
    asset = IntakeAsset(
        asset_id="asset-1",
        package_id=package.package_id,
        original_name="application.docx",
        stored_path=Path("data/intake/pkg-1/attachments/application.docx"),
        extension=".docx",
        mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        size_bytes=120,
        sha256="a" * 64,
    )
    case = IntakeCase(
        case_id="case-1",
        package_id=package.package_id,
        selected_form_asset_id=asset.asset_id,
        status=IntakeCaseStatus.NEEDS_REVIEW,
    )
    draft = IntakeDraft(
        draft_id="draft-1",
        case_id=case.case_id,
        parsed_fields_json='{"project_no":"P-1"}',
    )

    assert asset.asset_role is IntakeAssetRole.UNKNOWN
    assert case.confirmed_project_id is None
    assert draft.manual_overrides_json is None
