from pathlib import Path
from dataclasses import replace

from sqlalchemy import create_engine, inspect

from backend.application import (
    DirectWordIntakeService,
    ApplicationFormCandidateDetector,
    IntakeConfirmationService,
    IntakeFormSelectionService,
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
from backend.infrastructure.files import IntakeStorage
from backend.infrastructure.storage.database import create_session_factory, init_db
from backend.infrastructure.storage.repositories import (
    ApplicationFormRepository,
    FileAssetRepository,
    IntakeAssetRepository,
    IntakeCaseRepository,
    IntakeDraftRepository,
    IntakePackageRepository,
    ProjectRepository,
    SampleInfoRepository,
)


def _new_session():
    engine = create_engine("sqlite:///:memory:", future=True)
    init_db(engine)
    session_factory = create_session_factory(engine)
    return engine, session_factory()


def test_init_db_creates_intake_package_tables() -> None:
    engine, session = _new_session()
    try:
        table_names = set(inspect(engine).get_table_names())

        assert {
            "intake_packages",
            "intake_assets",
            "intake_cases",
            "intake_drafts",
        }.issubset(table_names)
    finally:
        session.close()


def test_intake_package_asset_case_and_draft_round_trip() -> None:
    _, session = _new_session()
    try:
        package_repository = IntakePackageRepository(session)
        asset_repository = IntakeAssetRepository(session)
        case_repository = IntakeCaseRepository(session)
        draft_repository = IntakeDraftRepository(session)

        package_repository.create(
            IntakePackage(
                package_id="pkg-1",
                source_type=IntakePackageSourceType.OUTLOOK_MSG,
                status=IntakePackageStatus.IMPORTED,
                source_original_name="request.msg",
                source_stored_path=Path("data/intake/pkg-1/source/request.msg"),
                subject="Connector test request",
                sender_email="requester@example.com",
                recipients_json='["lab@example.com"]',
            )
        )
        asset_repository.create(
            IntakeAsset(
                asset_id="asset-1",
                package_id="pkg-1",
                original_name="application.docx",
                stored_path=Path("data/intake/pkg-1/attachments/application.docx"),
                extension=".docx",
                mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                size_bytes=2048,
                sha256="b" * 64,
                asset_role=IntakeAssetRole.APPLICATION_FORM_CANDIDATE,
                candidate_score=90,
            )
        )
        case_repository.create(
            IntakeCase(
                case_id="case-1",
                package_id="pkg-1",
                selected_form_asset_id="asset-1",
                status=IntakeCaseStatus.NEEDS_REVIEW,
            )
        )
        draft_repository.create(
            IntakeDraft(
                draft_id="draft-1",
                case_id="case-1",
                parsed_fields_json='{"project_no":"P-1","product_name":"Connector"}',
                parser_warnings_json="[]",
            )
        )
        session.commit()

        assert package_repository.get("pkg-1").status is IntakePackageStatus.IMPORTED
        assert asset_repository.list_by_package("pkg-1")[0].asset_role is (
            IntakeAssetRole.APPLICATION_FORM_CANDIDATE
        )
        assert case_repository.list_by_package("pkg-1")[0].status is IntakeCaseStatus.NEEDS_REVIEW
        assert draft_repository.get_by_case("case-1").parsed_fields_json.startswith("{")
    finally:
        session.close()


def test_intake_repositories_update_review_state_without_auto_confirming_project() -> None:
    _, session = _new_session()
    try:
        package_repository = IntakePackageRepository(session)
        case_repository = IntakeCaseRepository(session)
        draft_repository = IntakeDraftRepository(session)

        package_repository.create(
            IntakePackage(
                package_id="pkg-2",
                source_type=IntakePackageSourceType.DIRECT_APPLICATION_FORM,
                status=IntakePackageStatus.NEEDS_APPLICATION_FORM_SELECTION,
                source_original_name="application.docx",
                source_stored_path=Path("data/intake/pkg-2/source/application.docx"),
            )
        )
        case_repository.create(
            IntakeCase(
                case_id="case-2",
                package_id="pkg-2",
                selected_form_asset_id=None,
                status=IntakeCaseStatus.DRAFT_CREATED,
            )
        )
        draft_repository.create(
            IntakeDraft(
                draft_id="draft-2",
                case_id="case-2",
                parsed_fields_json="{}",
            )
        )
        session.commit()

        package_repository.update(
            replace(
                package_repository.get("pkg-2"),
                status=IntakePackageStatus.READY_FOR_REVIEW,
            )
        )
        case_repository.update(
            replace(
                case_repository.get("case-2"),
                status=IntakeCaseStatus.NEEDS_REVIEW,
                reviewer_notes="Needs manual field confirmation.",
            )
        )
        draft_repository.update(
            replace(
                draft_repository.get("draft-2"),
                manual_overrides_json='{"requester":"White"}',
            )
        )
        session.commit()

        assert package_repository.get("pkg-2").status is IntakePackageStatus.READY_FOR_REVIEW
        updated_case = case_repository.get("case-2")
        assert updated_case.status is IntakeCaseStatus.NEEDS_REVIEW
        assert updated_case.confirmed_project_id is None
        assert draft_repository.get_by_case("case-2").manual_overrides_json == (
            '{"requester":"White"}'
        )
    finally:
        session.close()


def test_candidate_detector_persists_asset_roles_and_scores() -> None:
    _, session = _new_session()
    try:
        package_repository = IntakePackageRepository(session)
        asset_repository = IntakeAssetRepository(session)
        package_repository.create(
            IntakePackage(
                package_id="pkg-3",
                source_type=IntakePackageSourceType.OUTLOOK_MSG,
                status=IntakePackageStatus.IMPORTED,
                source_original_name="request.msg",
                source_stored_path=Path("data/intake/pkg-3/source/request.msg"),
            )
        )
        asset_repository.create(
            IntakeAsset(
                asset_id="asset-3a",
                package_id="pkg-3",
                original_name="Application Form E-3718.docx",
                stored_path=Path("data/intake/pkg-3/attachments/Application Form E-3718.docx"),
                extension=".docx",
                mime_type="application/octet-stream",
                size_bytes=100,
                sha256="c" * 64,
            )
        )
        asset_repository.create(
            IntakeAsset(
                asset_id="asset-3b",
                package_id="pkg-3",
                original_name="product specification.pdf",
                stored_path=Path("data/intake/pkg-3/attachments/product specification.pdf"),
                extension=".pdf",
                mime_type="application/pdf",
                size_bytes=100,
                sha256="d" * 64,
            )
        )
        session.commit()

        result = ApplicationFormCandidateDetector(asset_repository).detect_for_package("pkg-3")
        session.commit()

        assert [candidate.asset_id for candidate in result.candidates] == ["asset-3a"]
        updated_assets = {asset.asset_id: asset for asset in asset_repository.list_by_package("pkg-3")}
        assert updated_assets["asset-3a"].asset_role is IntakeAssetRole.APPLICATION_FORM_CANDIDATE
        assert updated_assets["asset-3a"].candidate_score == 80
        assert updated_assets["asset-3b"].asset_role is IntakeAssetRole.SUPPORTING_ATTACHMENT
    finally:
        session.close()


def test_form_selection_service_creates_case_and_draft_with_repositories() -> None:
    _, session = _new_session()
    try:
        package_repository = IntakePackageRepository(session)
        asset_repository = IntakeAssetRepository(session)
        case_repository = IntakeCaseRepository(session)
        draft_repository = IntakeDraftRepository(session)
        package_repository.create(
            IntakePackage(
                package_id="pkg-4",
                source_type=IntakePackageSourceType.OUTLOOK_MSG,
                status=IntakePackageStatus.READY_FOR_REVIEW,
                source_original_name="request.msg",
                source_stored_path=Path("data/intake/pkg-4/source/request.msg"),
            )
        )
        asset_repository.create(
            IntakeAsset(
                asset_id="asset-4a",
                package_id="pkg-4",
                original_name="Application Form E-3718.docx",
                stored_path=Path("data/intake/pkg-4/attachments/Application Form E-3718.docx"),
                extension=".docx",
                mime_type="application/octet-stream",
                size_bytes=100,
                sha256="e" * 64,
                asset_role=IntakeAssetRole.APPLICATION_FORM_CANDIDATE,
                candidate_score=80,
            )
        )
        session.commit()

        result = IntakeFormSelectionService(
            package_repository,
            asset_repository,
            case_repository,
            draft_repository,
        ).select_form_asset("pkg-4", "asset-4a")
        session.commit()

        assert result.case.package_id == "pkg-4"
        assert result.draft.case_id == result.case.case_id
        assert asset_repository.get("asset-4a").asset_role is (
            IntakeAssetRole.SELECTED_APPLICATION_FORM
        )
        assert case_repository.list_by_package("pkg-4")[0].selected_form_asset_id == "asset-4a"
        assert draft_repository.get_by_case(result.case.case_id).parsed_fields_json == "{}"
    finally:
        session.close()


def test_confirmation_service_creates_project_records_with_repositories() -> None:
    _, session = _new_session()
    try:
        package_repository = IntakePackageRepository(session)
        intake_asset_repository = IntakeAssetRepository(session)
        case_repository = IntakeCaseRepository(session)
        draft_repository = IntakeDraftRepository(session)
        project_repository = ProjectRepository(session)
        form_repository = ApplicationFormRepository(session)
        sample_repository = SampleInfoRepository(session)
        file_asset_repository = FileAssetRepository(session)

        package_repository.create(
            IntakePackage(
                package_id="pkg-5",
                source_type=IntakePackageSourceType.OUTLOOK_MSG,
                status=IntakePackageStatus.READY_FOR_REVIEW,
                source_original_name="request.msg",
                source_stored_path=Path("data/intake/pkg-5/source/request.msg"),
            )
        )
        intake_asset_repository.create(
            IntakeAsset(
                asset_id="asset-5a",
                package_id="pkg-5",
                original_name="application.docx",
                stored_path=Path("data/intake/pkg-5/attachments/application.docx"),
                extension=".docx",
                mime_type="application/octet-stream",
                size_bytes=100,
                sha256="f" * 64,
                asset_role=IntakeAssetRole.SELECTED_APPLICATION_FORM,
            )
        )
        case_repository.create(
            IntakeCase(
                case_id="case-5",
                package_id="pkg-5",
                selected_form_asset_id="asset-5a",
                status=IntakeCaseStatus.NEEDS_REVIEW,
            )
        )
        draft_repository.create(
            IntakeDraft(
                draft_id="draft-5",
                case_id="case-5",
                parsed_fields_json=(
                    '{"project_no":"P-5","product_name":"Connector",'
                    '"requester":"White","form_no":"E-3718","revision":"H",'
                    '"phone":"555-0100","request_date":"2026-05-03",'
                    '"email":"white@example.com","business_unit":"BU",'
                    '"manufacturing_site":"Nantong",'
                    '"results_format":"Formal Report (Customer)",'
                    '"requested_completion_date":"2026-05-10",'
                    '"test_type":"Customer Specific Testing",'
                    '"sample_status":"Production",'
                    '"project_type":"New Product Development",'
                    '"requested_testing":"Bend testing",'
                    '"post_testing_disposition":"Keep in the Lab",'
                    '"confidential":"No","subcontract":"Yes",'
                    '"send_copies_recipients":"Neo Xu",'
                    '"samples":[{"product_name":"Connector",'
                    '"part_number":"PN-5","lot_or_traceability":"LOT-5",'
                    '"material":"Copper","plating":"Ag",'
                    '"housing_material":"PA10T","quantity":3}]}'
                ),
            )
        )
        session.commit()

        result = IntakeConfirmationService(
            package_repository,
            intake_asset_repository,
            case_repository,
            draft_repository,
            project_repository,
            form_repository,
            sample_repository,
            file_asset_repository,
        ).confirm_case("case-5")
        session.commit()

        assert project_repository.get(result.project.project_id).project_no == "P-5"
        assert form_repository.list_by_project(result.project.project_id)[0].form_no == "E-3718"
        assert sample_repository.list_by_project(result.project.project_id)[0].quantity == 3
        assert len(file_asset_repository.list_by_project(result.project.project_id)) == 2
        assert case_repository.get("case-5").confirmed_project_id == result.project.project_id
    finally:
        session.close()


def test_direct_word_intake_service_persists_package_and_asset_with_repositories(
    tmp_path: Path,
) -> None:
    source = tmp_path / "E-3718 Application Form.docx"
    source.write_bytes(b"word")
    _, session = _new_session()
    try:
        package_repository = IntakePackageRepository(session)
        asset_repository = IntakeAssetRepository(session)

        result = DirectWordIntakeService(
            IntakeStorage(tmp_path / "intake"),
            package_repository,
            asset_repository,
        ).import_word_form(source)
        session.commit()

        package = package_repository.get(result.package.package_id)
        assets = asset_repository.list_by_package(result.package.package_id)

        assert package.source_type is IntakePackageSourceType.DIRECT_APPLICATION_FORM
        assert package.source_stored_path.is_file()
        assert assets[0].asset_role is IntakeAssetRole.APPLICATION_FORM_CANDIDATE
        assert assets[0].sha256 == result.asset.sha256
    finally:
        session.close()
