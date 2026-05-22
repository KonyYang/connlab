"""FastAPI dependency wiring for ConnLab."""

from __future__ import annotations

from collections.abc import Generator
from functools import lru_cache

from fastapi import Depends
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from backend.application.exception_workflow_service import ExceptionWorkflowService
from backend.application.external_excel_read_service import ExternalExcelReadService
from backend.application.external_resource_service import ExternalResourceService
from backend.application.frozen_field_revision_request_service import (
    FrozenFieldRevisionRequestService,
)
from backend.application.intake_asset_download_service import (
    IntakeAssetDownloadService,
)
from backend.application.evidence_placement_service import EvidencePlacementService
from backend.application.folder_service import FolderService
from backend.application.direct_word_intake_service import DirectWordIntakeService
from backend.application.duplicate_draft_history_cleanup_service import (
    DuplicateDraftHistoryCleanupService,
)
from backend.application.email_package_application_form_service import (
    EmailPackageApplicationFormService,
)
from backend.application.intake_precheck_service import IntakePrecheckService
from backend.application.application_form_eligibility_service import (
    IntakeAssetApplicationFormEligibilityService,
)
from backend.application.approval_package_service import ApprovalPackageService
from backend.application.intake_asset_preview_service import IntakeAssetPreviewService
from backend.application.intake_case_review_service import IntakeCaseReviewService
from backend.application.intake_confirmation_service import IntakeConfirmationService
from backend.application.intake_form_selection_service import IntakeFormSelectionService
from backend.application.intake_package_query_service import IntakePackageQueryService
from backend.application.ltr_authority import LtrAuthorityPort
from backend.application.ltr_excel_authority_adapter import (
    ExcelWorkbookLtrAuthorityAdapter,
)
from backend.application.ltr_local_commit_service import LtrLocalCommitService
from backend.application.ltr_renumber_preview_service import LtrRenumberPreviewService
from backend.application.ltr_registration_preview_service import (
    LtrRegistrationPreviewService,
)
from backend.application.ltr_workbook_write_preview_service import (
    LtrWorkbookWritePreviewService,
)
from backend.application.ltr_workbook_compatibility_service import (
    LtrWorkbookCompatibilityService,
)
from backend.application.ltr_workbook_write_commit_service import (
    LtrWorkbookYearSheetBootstrapPolicy,
    LtrWorkbookWriteCommitService,
)
from backend.application.ltr_readiness_service import LtrReadinessService
from backend.application.ltr_service import LtrService
from backend.application.lookup_options_service import LookupOptionService
from backend.application.lookup_service import LookupService
from backend.application.manual_intake_service import ManualIntakeService
from backend.application.msg_package_intake_service import MsgPackageIntakeService
from backend.application.new_project_application_draft_service import (
    NewProjectApplicationDraftService,
)
from backend.application.new_project_completion_service import (
    NewProjectCompletionService,
)
from backend.application.no_ltr_project_cleanup_service import (
    NoLtrProjectCleanupService,
)
from backend.application.project_creation_draft_lifecycle_service import (
    ProjectCreationDraftLifecycleService,
)
from backend.application.project_creation_draft_query_service import (
    ProjectCreationDraftQueryService,
)
from backend.application.project_lifecycle_service import ProjectLifecycleService
from backend.application.project_ltr_cleanup_audit_service import (
    ProjectLtrCleanupAuditService,
)
from backend.application.project_service import ProjectService
from backend.application.project_test_plan_matrix_preview_service import (
    ProjectTestPlanMatrixPreviewService,
)
from backend.application.project_matrix_draft_persistence_service import (
    ProjectMatrixDraftPersistenceService,
)
from backend.application.confirmed_matrix_authority_service import (
    ConfirmedMatrixAuthorityService,
)
from backend.application.project_test_plan_draft_service import (
    ProjectTestPlanDraftService,
)
from backend.application.source_matrix_import_persistence_service import (
    SourceMatrixImportPersistenceService,
)
from backend.application.project_test_plan_matrix_edit_service import (
    ProjectTestPlanMatrixEditService,
)
from backend.application.project_test_plan_source_candidate_service import (
    ProjectTestPlanSourceCandidateService,
)
from backend.application.project_output_record_service import (
    ProjectOutputRecordService,
)
from backend.application.section2_completion_preview_service import (
    Section2CompletionPreviewService,
)
from backend.application.section2_write_back_service import (
    Section2WriteBackService,
)
from backend.application.test_record_fee_dataset_preview_service import (
    TestRecordFeeDatasetPreviewService,
)
from backend.application.test_record_fee_document_generation_service import (
    TestRecordFeeDocumentGenerationService,
)
from backend.infrastructure.files import IntakeStorage
from backend.infrastructure.office import (
    FeeEvaluationWorkbookGateway,
    TestRecordDocumentGateway,
    LtrWorkbookTransactionConfig,
    LtrWorkbookTransactionGateway,
    OfficeFacade,
)
from backend.infrastructure.storage.database import (
    create_database_engine,
    create_session_factory,
    init_db,
)
from backend.infrastructure.storage.repositories import (
    ApplicationFormRepository,
    ConfirmedMatrixAuthorityRepository,
    ExternalResourceRepository,
    FileAssetRepository,
    FrozenFieldRevisionRequestRepository,
    LtrRecordRepository,
    PrecheckResultRepository,
    ProjectCleanupAuditRecordRepository,
    ProjectFolderRecordRepository,
    ProjectMatrixDraftRepository,
    ProjectRepository,
    ProjectOutputRecordRepository,
    ProjectTestPlanDraftRepository,
    SourceMatrixImportRepository,
    SampleInfoRepository,
)
from backend.infrastructure.storage.repositories.lookup_options import (
    LookupOptionRepository,
)
from backend.infrastructure.storage.repositories.intake_package import (
    IntakeAssetRepository,
    IntakeCaseRepository,
    IntakeDraftRepository,
    IntakePackageRepository,
)
from backend.shared.config import Settings


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    """Return the application database engine."""
    engine = create_database_engine()
    init_db(engine)
    return engine


@lru_cache(maxsize=1)
def get_session_factory() -> sessionmaker[Session]:
    """Return the application session factory."""
    return create_session_factory(get_engine())


def get_session() -> Generator[Session, None, None]:
    """Yield a database session for one request."""
    with get_session_factory()() as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise


def get_project_service(session: Session = Depends(get_session)) -> ProjectService:
    """Build a project service for API routes."""
    return ProjectService(ProjectRepository(session))


def get_project_test_plan_matrix_preview_service() -> ProjectTestPlanMatrixPreviewService:
    """Build the read-only project test-plan Matrix preview service."""
    return ProjectTestPlanMatrixPreviewService()


def get_project_test_plan_draft_service(
    session: Session = Depends(get_session),
) -> ProjectTestPlanDraftService:
    """Build the Project test-plan draft persistence service."""
    return ProjectTestPlanDraftService(
        project_store=ProjectRepository(session),
        draft_store=ProjectTestPlanDraftRepository(session),
        source_matrix_import_persistence_service=SourceMatrixImportPersistenceService(
            store=SourceMatrixImportRepository(session)
        ),
    )


def get_project_matrix_draft_persistence_service(
    session: Session = Depends(get_session),
) -> ProjectMatrixDraftPersistenceService:
    """Build the Project Matrix draft persistence service."""
    return ProjectMatrixDraftPersistenceService(
        project_store=ProjectRepository(session),
        source_store=SourceMatrixImportRepository(session),
        draft_store=ProjectMatrixDraftRepository(session),
    )


def get_confirmed_matrix_authority_service(
    session: Session = Depends(get_session),
) -> ConfirmedMatrixAuthorityService:
    """Build the Confirmed Matrix authority confirmation service."""
    return ConfirmedMatrixAuthorityService(
        project_store=ProjectRepository(session),
        draft_store=ProjectMatrixDraftRepository(session),
        confirmed_store=ConfirmedMatrixAuthorityRepository(session),
    )


def get_project_test_plan_matrix_edit_service(
    session: Session = Depends(get_session),
) -> ProjectTestPlanMatrixEditService:
    """Build the controlled Matrix edit/validate/confirm service."""
    return ProjectTestPlanMatrixEditService(
        draft_service=ProjectTestPlanDraftService(
            project_store=ProjectRepository(session),
            draft_store=ProjectTestPlanDraftRepository(session),
        )
    )


def get_project_test_plan_source_candidate_service(
    session: Session = Depends(get_session),
) -> ProjectTestPlanSourceCandidateService:
    """Build the Project test-plan source candidate read-model service."""
    return ProjectTestPlanSourceCandidateService(
        project_store=ProjectRepository(session),
        file_asset_store=FileAssetRepository(session),
    )


def get_project_output_record_service(
    session: Session = Depends(get_session),
) -> ProjectOutputRecordService:
    """Build the persisted project output ledger service."""
    return ProjectOutputRecordService(
        project_store=ProjectRepository(session),
        draft_store=ProjectTestPlanDraftRepository(session),
        output_store=ProjectOutputRecordRepository(session),
    )


def get_section2_completion_preview_service(
    session: Session = Depends(get_session),
) -> Section2CompletionPreviewService:
    """Build the read-only Section 2 completion preview service."""
    return Section2CompletionPreviewService(
        project_store=ProjectRepository(session),
        draft_store=ProjectTestPlanDraftRepository(session),
    )


def get_section2_write_back_service(
    session: Session = Depends(get_session),
) -> Section2WriteBackService:
    """Build the controlled Section 2 write-back service."""
    return Section2WriteBackService(
        project_store=ProjectRepository(session),
        draft_store=ProjectTestPlanDraftRepository(session),
    )


def get_test_record_fee_dataset_preview_service(
    session: Session = Depends(get_session),
) -> TestRecordFeeDatasetPreviewService:
    """Build the read-only test record and fee dataset preview service."""
    return TestRecordFeeDatasetPreviewService(
        project_store=ProjectRepository(session),
        draft_store=ProjectTestPlanDraftRepository(session),
    )


def get_test_record_fee_document_generation_service(
    session: Session = Depends(get_session),
) -> TestRecordFeeDocumentGenerationService:
    """Build the controlled test-record and fee document generation service."""
    return TestRecordFeeDocumentGenerationService(
        dataset_preview_service=TestRecordFeeDatasetPreviewService(
            project_store=ProjectRepository(session),
            draft_store=ProjectTestPlanDraftRepository(session),
        ),
        test_record_writer=TestRecordDocumentGateway(),
        fee_writer=FeeEvaluationWorkbookGateway(),
    )


def get_approval_package_service(
    session: Session = Depends(get_session),
) -> ApprovalPackageService:
    """Build the approval package preview and execute service."""
    project_repository = ProjectRepository(session)
    return ApprovalPackageService(
        project_repository=project_repository,
        lifecycle_guard=ProjectLifecycleService(project_repository),
    )


def get_project_ltr_cleanup_audit_service(
    session: Session = Depends(get_session),
) -> ProjectLtrCleanupAuditService:
    """Build the read-only Project/LTR cleanup audit service."""
    return ProjectLtrCleanupAuditService(
        project_store=ProjectRepository(session),
        ltr_store=LtrRecordRepository(session),
    )


def get_no_ltr_project_cleanup_service(
    session: Session = Depends(get_session),
) -> NoLtrProjectCleanupService:
    """Build the controlled no-LTR project cleanup execution service."""
    return NoLtrProjectCleanupService(
        project_store=ProjectRepository(session),
        ltr_store=LtrRecordRepository(session),
        audit_store=ProjectCleanupAuditRecordRepository(session),
    )


def get_settings() -> Settings:
    """Return application settings."""
    return Settings.load()


def get_duplicate_draft_history_cleanup_service(
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> DuplicateDraftHistoryCleanupService:
    """Build duplicate draft history cleanup service."""
    return DuplicateDraftHistoryCleanupService(
        package_store=IntakePackageRepository(session),
        asset_store=IntakeAssetRepository(session),
        case_store=IntakeCaseRepository(session),
        draft_store=IntakeDraftRepository(session),
        storage=IntakeStorage(settings.data_dir / "intake"),
    )


def get_intake_precheck_service(
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> IntakePrecheckService:
    """Build an intake/precheck service for API routes."""
    return IntakePrecheckService(
        project_repository=ProjectRepository(session),
        form_repository=ApplicationFormRepository(session),
        sample_repository=SampleInfoRepository(session),
        file_asset_repository=FileAssetRepository(session),
        precheck_repository=PrecheckResultRepository(session),
        settings=settings,
    )


def get_exception_workflow_service(
    session: Session = Depends(get_session),
) -> ExceptionWorkflowService:
    """Build an exception workflow service for API routes."""
    return ExceptionWorkflowService(
        package_store=IntakePackageRepository(session),
        asset_store=IntakeAssetRepository(session),
        case_store=IntakeCaseRepository(session),
        draft_store=IntakeDraftRepository(session),
    )


def get_external_resource_service(
    session: Session = Depends(get_session),
) -> ExternalResourceService:
    """Build the external resource registry service."""
    return ExternalResourceService(ExternalResourceRepository(session))


def get_external_excel_read_service(
    session: Session = Depends(get_session),
) -> ExternalExcelReadService:
    """Build the read-only external Excel structured read service."""
    return ExternalExcelReadService(ExternalResourceRepository(session))


def get_ltr_workbook_compatibility_service(
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> LtrWorkbookCompatibilityService:
    """Build the real-workbook compatibility baseline service."""
    return LtrWorkbookCompatibilityService(
        resource_store=ExternalResourceRepository(session),
        workbook_settings=settings.ltr_workbook,
    )


def get_msg_package_intake_service(
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> MsgPackageIntakeService:
    """Build a manual `.msg` package intake service for API routes."""
    return MsgPackageIntakeService(
        storage=IntakeStorage(settings.data_dir / "intake"),
        package_store=IntakePackageRepository(session),
        asset_store=IntakeAssetRepository(session),
    )


def get_direct_word_intake_service(
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> DirectWordIntakeService:
    """Build a direct Word application-form intake service for API routes."""
    return DirectWordIntakeService(
        storage=IntakeStorage(settings.data_dir / "intake"),
        package_store=IntakePackageRepository(session),
        asset_store=IntakeAssetRepository(session),
    )


def get_email_package_application_form_service(
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> EmailPackageApplicationFormService:
    """Build a service for adding a Word form to an existing email package."""
    package_store = IntakePackageRepository(session)
    asset_store = IntakeAssetRepository(session)
    return EmailPackageApplicationFormService(
        storage=IntakeStorage(settings.data_dir / "intake"),
        package_store=package_store,
        asset_store=asset_store,
        selection_service=IntakeFormSelectionService(
            package_store=package_store,
            asset_store=asset_store,
            case_store=IntakeCaseRepository(session),
            draft_store=IntakeDraftRepository(session),
        ),
    )


def get_intake_package_query_service(
    session: Session = Depends(get_session),
) -> IntakePackageQueryService:
    """Build a read-only intake package detail query service."""
    return IntakePackageQueryService(
        package_store=IntakePackageRepository(session),
        asset_store=IntakeAssetRepository(session),
        case_store=IntakeCaseRepository(session),
    )


def get_intake_asset_download_service(
    session: Session = Depends(get_session),
) -> IntakeAssetDownloadService:
    """Build an intake asset download service for API routes."""
    return IntakeAssetDownloadService(
        asset_store=IntakeAssetRepository(session),
    )


def get_intake_asset_preview_service(
    session: Session = Depends(get_session),
) -> IntakeAssetPreviewService:
    """Build a safe intake asset preview service."""
    return IntakeAssetPreviewService(
        asset_store=IntakeAssetRepository(session),
    )


def get_intake_asset_application_form_eligibility_service(
    session: Session = Depends(get_session),
) -> IntakeAssetApplicationFormEligibilityService:
    """Build the intake asset application-form eligibility service."""
    return IntakeAssetApplicationFormEligibilityService(
        asset_store=IntakeAssetRepository(session),
    )


def get_intake_form_selection_service(
    session: Session = Depends(get_session),
) -> IntakeFormSelectionService:
    """Build an application-form asset selection service."""
    return IntakeFormSelectionService(
        package_store=IntakePackageRepository(session),
        asset_store=IntakeAssetRepository(session),
        case_store=IntakeCaseRepository(session),
        draft_store=IntakeDraftRepository(session),
        ltr_store=LtrRecordRepository(session),
    )


def get_new_project_application_draft_service(
    session: Session = Depends(get_session),
) -> NewProjectApplicationDraftService:
    """Build the New Project single-page application draft service."""
    package_store = IntakePackageRepository(session)
    asset_store = IntakeAssetRepository(session)
    case_store = IntakeCaseRepository(session)
    draft_store = IntakeDraftRepository(session)
    return NewProjectApplicationDraftService(
        package_store=package_store,
        case_store=case_store,
        draft_store=draft_store,
        asset_store=asset_store,
        selection_service=IntakeFormSelectionService(
            package_store=package_store,
            asset_store=asset_store,
            case_store=case_store,
            draft_store=draft_store,
            ltr_store=LtrRecordRepository(session),
        ),
    )


def get_manual_intake_service(
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> ManualIntakeService:
    """Build a no-email manual intake service for API routes."""
    return ManualIntakeService(
        storage=IntakeStorage(settings.data_dir / "intake"),
        package_store=IntakePackageRepository(session),
        asset_store=IntakeAssetRepository(session),
        case_store=IntakeCaseRepository(session),
        draft_store=IntakeDraftRepository(session),
    )


def get_project_creation_draft_lifecycle_service(
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> ProjectCreationDraftLifecycleService:
    """Build the New Project creation draft lifecycle service."""
    return ProjectCreationDraftLifecycleService(
        storage=IntakeStorage(settings.data_dir / "intake"),
        package_store=IntakePackageRepository(session),
        asset_store=IntakeAssetRepository(session),
        case_store=IntakeCaseRepository(session),
        draft_store=IntakeDraftRepository(session),
    )


def get_project_creation_draft_query_service(
    session: Session = Depends(get_session),
) -> ProjectCreationDraftQueryService:
    """Build the saved creation draft query service."""
    return ProjectCreationDraftQueryService(
        package_store=IntakePackageRepository(session),
        case_store=IntakeCaseRepository(session),
        draft_store=IntakeDraftRepository(session),
    )


def get_intake_case_review_service(
    session: Session = Depends(get_session),
) -> IntakeCaseReviewService:
    """Build a unified intake case review query service."""
    return IntakeCaseReviewService(
        package_store=IntakePackageRepository(session),
        asset_store=IntakeAssetRepository(session),
        case_store=IntakeCaseRepository(session),
        draft_store=IntakeDraftRepository(session),
        ltr_store=LtrRecordRepository(session),
    )


def get_intake_confirmation_service(
    session: Session = Depends(get_session),
) -> IntakeConfirmationService:
    """Build an intake confirmation service for API routes."""
    return IntakeConfirmationService(
        package_store=IntakePackageRepository(session),
        intake_asset_store=IntakeAssetRepository(session),
        intake_case_store=IntakeCaseRepository(session),
        intake_draft_store=IntakeDraftRepository(session),
        project_store=ProjectRepository(session),
        application_form_store=ApplicationFormRepository(session),
        sample_store=SampleInfoRepository(session),
        file_asset_store=FileAssetRepository(session),
    )


def get_frozen_field_revision_request_service(
    session: Session = Depends(get_session),
) -> FrozenFieldRevisionRequestService:
    """Build a frozen-field revision request service for API routes."""
    return FrozenFieldRevisionRequestService(
        request_store=FrozenFieldRevisionRequestRepository(session),
        review_service=IntakeCaseReviewService(
            package_store=IntakePackageRepository(session),
            asset_store=IntakeAssetRepository(session),
            case_store=IntakeCaseRepository(session),
            draft_store=IntakeDraftRepository(session),
            ltr_store=LtrRecordRepository(session),
        ),
        ltr_store=LtrRecordRepository(session),
    )


def get_ltr_service(session: Session = Depends(get_session)) -> LtrService:
    """Build an LTR service for API routes."""
    project_repository = ProjectRepository(session)
    return LtrService(
        project_repository=project_repository,
        ltr_repository=LtrRecordRepository(session),
        lifecycle_guard=ProjectLifecycleService(project_repository),
    )


def get_lookup_service(session: Session = Depends(get_session)) -> LookupService:
    """Build a read-only lookup service for API routes."""
    return LookupService(
        project_repository=ProjectRepository(session),
        form_repository=ApplicationFormRepository(session),
        sample_repository=SampleInfoRepository(session),
        ltr_repository=LtrRecordRepository(session),
        file_asset_repository=FileAssetRepository(session),
    )


def get_lookup_option_service(
    session: Session = Depends(get_session),
) -> LookupOptionService:
    """Build a backend-managed lookup option service for API routes."""
    return LookupOptionService(LookupOptionRepository(session))


def get_ltr_readiness_service(
    session: Session = Depends(get_session),
) -> LtrReadinessService:
    """Build an LTR readiness service for API routes."""
    return LtrReadinessService(
        project_repository=ProjectRepository(session),
        form_repository=ApplicationFormRepository(session),
        sample_repository=SampleInfoRepository(session),
        file_asset_repository=FileAssetRepository(session),
    )


def get_ltr_registration_preview_service(
    session: Session = Depends(get_session),
) -> LtrRegistrationPreviewService:
    """Build an LTR registration preview service for API routes."""
    project_repository = ProjectRepository(session)
    readiness_service = LtrReadinessService(
        project_repository=project_repository,
        form_repository=ApplicationFormRepository(session),
        sample_repository=SampleInfoRepository(session),
        file_asset_repository=FileAssetRepository(session),
    )
    return LtrRegistrationPreviewService(
        ltr_repository=LtrRecordRepository(session),
        readiness_service=readiness_service,
        lifecycle_guard=ProjectLifecycleService(project_repository),
    )


def get_ltr_local_commit_service(
    session: Session = Depends(get_session),
) -> LtrLocalCommitService:
    """Build an LTR local commit service for API routes."""
    project_repository = ProjectRepository(session)
    readiness_service = LtrReadinessService(
        project_repository=project_repository,
        form_repository=ApplicationFormRepository(session),
        sample_repository=SampleInfoRepository(session),
        file_asset_repository=FileAssetRepository(session),
    )
    ltr_repository = LtrRecordRepository(session)
    lifecycle_guard = ProjectLifecycleService(project_repository)
    preview_service = LtrRegistrationPreviewService(
        ltr_repository=ltr_repository,
        readiness_service=readiness_service,
        lifecycle_guard=lifecycle_guard,
    )
    return LtrLocalCommitService(
        preview_service=preview_service,
        ltr_service=LtrService(
            project_repository=project_repository,
            ltr_repository=ltr_repository,
            lifecycle_guard=lifecycle_guard,
        ),
    )


def get_ltr_renumber_preview_service(
    session: Session = Depends(get_session),
) -> LtrRenumberPreviewService:
    """Build an LTR renumber preview service for API routes."""
    return LtrRenumberPreviewService(
        project_repository=ProjectRepository(session),
        ltr_repository=LtrRecordRepository(session),
        folder_repository=ProjectFolderRecordRepository(session),
        file_asset_repository=FileAssetRepository(session),
    )


def get_ltr_workbook_write_preview_service(
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> LtrWorkbookWritePreviewService:
    """Build the no-write LTR workbook mapping preview service."""
    return LtrWorkbookWritePreviewService(
        project_store=ProjectRepository(session),
        application_form_store=ApplicationFormRepository(session),
        sample_store=SampleInfoRepository(session),
        workbook_settings=settings.ltr_workbook,
    )


def get_ltr_workbook_write_commit_service(
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> LtrWorkbookWriteCommitService:
    """Build the external LTR workbook write commit service."""
    project_repository = ProjectRepository(session)
    ltr_repository = LtrRecordRepository(session)
    lifecycle_guard = ProjectLifecycleService(project_repository)
    preview_service = LtrWorkbookWritePreviewService(
        project_store=project_repository,
        application_form_store=ApplicationFormRepository(session),
        sample_store=SampleInfoRepository(session),
        workbook_settings=settings.ltr_workbook,
    )
    transaction_gateway = LtrWorkbookTransactionGateway(
        OfficeFacade(),
        LtrWorkbookTransactionConfig(
            path=settings.ltr_workbook.path,
            write_enabled=settings.ltr_workbook.write_enabled,
            modify_password=settings.ltr_workbook.modify_password,
            lock_dir=settings.ltr_workbook.lock_dir,
            lock_timeout_seconds=settings.ltr_workbook.lock_timeout_seconds,
            backup_dir=settings.ltr_workbook.backup_dir,
        ),
    )
    return LtrWorkbookWriteCommitService(
        preview_service=preview_service,
        transaction_gateway=transaction_gateway,
        ltr_service=LtrService(
            project_repository=project_repository,
            ltr_repository=ltr_repository,
            lifecycle_guard=lifecycle_guard,
        ),
        ltr_store=ltr_repository,
        year_sheet_bootstrap_policy=LtrWorkbookYearSheetBootstrapPolicy(
            allow_system_assisted_create_year_sheet=(
                settings.ltr_workbook.allow_system_assisted_create_year_sheet
            ),
            require_operator_confirmation_for_year_sheet_bootstrap=(
                settings.ltr_workbook.require_operator_confirmation_for_year_sheet_bootstrap
            ),
            template_sheet_name=settings.ltr_workbook.template_sheet_name,
            sheet_bootstrap_clear_start_row=(
                settings.ltr_workbook.sheet_bootstrap_clear_start_row
            ),
        ),
    )


def get_ltr_authority_service(
    workbook_service: LtrWorkbookWriteCommitService = Depends(
        get_ltr_workbook_write_commit_service
    ),
) -> LtrAuthorityPort:
    """Build the active LTR authority adapter (Excel mode for Phase 10E)."""
    return ExcelWorkbookLtrAuthorityAdapter(workbook_service)


def get_new_project_completion_service(
    session: Session = Depends(get_session),
    ltr_commit_service: LtrAuthorityPort = Depends(
        get_ltr_authority_service
    ),
) -> NewProjectCompletionService:
    """Build the New Project single-page completion orchestration service."""
    project_repository = ProjectRepository(session)
    ltr_repository = LtrRecordRepository(session)
    file_asset_repository = FileAssetRepository(session)
    lifecycle_guard = ProjectLifecycleService(project_repository)
    confirmation_service = IntakeConfirmationService(
        package_store=IntakePackageRepository(session),
        intake_asset_store=IntakeAssetRepository(session),
        intake_case_store=IntakeCaseRepository(session),
        intake_draft_store=IntakeDraftRepository(session),
        project_store=project_repository,
        application_form_store=ApplicationFormRepository(session),
        sample_store=SampleInfoRepository(session),
        file_asset_store=file_asset_repository,
    )
    return NewProjectCompletionService(
        intake_case_store=IntakeCaseRepository(session),
        project_store=project_repository,
        ltr_store=ltr_repository,
        confirmation_service=confirmation_service,
        ltr_commit_service=ltr_commit_service,
    )


def _default_folder_template_path(templates_dir):
    """Return the first configured template directory, or the root as a fallback."""
    if "{" in templates_dir.name and "}" in templates_dir.name:
        return templates_dir
    template_dirs = sorted(path for path in templates_dir.iterdir() if path.is_dir())
    return template_dirs[0] if template_dirs else templates_dir


def get_folder_service(session: Session = Depends(get_session)) -> FolderService:
    """Build a folder service for API routes."""
    project_repository = ProjectRepository(session)
    return FolderService(
        project_repository=project_repository,
        folder_repository=ProjectFolderRecordRepository(session),
        file_asset_repository=FileAssetRepository(session),
        lifecycle_guard=ProjectLifecycleService(project_repository),
    )


def get_evidence_placement_service(
    session: Session = Depends(get_session),
) -> EvidencePlacementService:
    """Build an evidence placement service for API routes."""
    project_repository = ProjectRepository(session)
    return EvidencePlacementService(
        project_repository=project_repository,
        folder_repository=ProjectFolderRecordRepository(session),
        file_asset_repository=FileAssetRepository(session),
        lifecycle_guard=ProjectLifecycleService(project_repository),
    )
