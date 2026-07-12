"""FastAPI dependency wiring for ConnLab."""

from __future__ import annotations

from collections.abc import Generator
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

from fastapi import Depends
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from backend.application.exception_workflow_service import ExceptionWorkflowService
from backend.application.external_excel_read_service import ExternalExcelReadService
from backend.application.local_path_picker_service import LocalPathPickerService
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
from backend.application.ltr_duplicate_resolution_service import (
    LocalLtrDuplicateResolutionService,
)
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
from backend.application.ltr_workbook_basic_information_sync_service import (
    LtrWorkbookBasicInformationSyncService,
)
from backend.application.ltr_workbook_local_config_service import (
    LtrWorkbookLocalConfigService,
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
from backend.application.specified_ltr_workbook_authority_preview_service import (
    SpecifiedLtrWorkbookAuthorityPreviewService,
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
from backend.application.project_lifecycle_management_service import (
    ProjectLifecycleManagementService,
)
from backend.application.project_lifecycle_state_service import (
    ProjectLifecycleStateService,
)
from backend.application.project_lifecycle_write_guard import (
    ProjectLifecycleWriteGuard,
)
from backend.application.project_ltr_cleanup_audit_service import (
    ProjectLtrCleanupAuditService,
)
from backend.application.project_registry_summary_service import (
    ProjectRegistrySummaryService,
)
from backend.application.project_service import ProjectService
from backend.application.project_basic_information_service import (
    ProjectBasicInformationService,
)
from backend.application.project_basic_information_output import (
    ConfirmedBasicInformationSnapshot,
    ProjectBasicInformationSnapshotReader,
)
from backend.application.project_basic_information_output_identity import (
    fee_form_identity,
)
from backend.application.project_test_plan_matrix_preview_service import (
    ProjectTestPlanMatrixPreviewService,
)
from backend.application.matrix_import_commit_service import (
    MatrixImportCommitService,
)
from backend.application.project_matrix_draft_persistence_service import (
    ProjectMatrixDraftPersistenceService,
)
from backend.application.confirmed_matrix_authority_service import (
    ConfirmedMatrixAuthorityService,
)
from backend.application.confirmed_matrix_runtime_projection_service import (
    ConfirmedMatrixRuntimeProjectionService,
)
from backend.application.confirmed_matrix_test_record_preview_service import (
    ConfirmedMatrixTestRecordPreviewService,
)
from backend.application.confirmed_matrix_llcr_cr_record_generation_service import (
    LlcrCrRecordWorkbookGenerationService,
)
from backend.application.confirmed_matrix_llcr_cr_record_preview_service import (
    LlcrCrRecordWorkbookPreviewService,
)
from backend.application.confirmed_matrix_fee_draft_service import (
    ConfirmedMatrixFeeDraftService,
)
from backend.application.confirmed_matrix_fee_evaluation_export_service import (
    ExportConfirmedMatrixFeeEvaluationCommand,
    ConfirmedMatrixFeeEvaluationExportService,
)
from backend.application.confirmed_matrix_fee_evaluation_export_timeout_service import (
    ConfirmedMatrixFeeEvaluationExportTimeoutService,
)
from backend.application.confirmed_matrix_fee_template_basic_fill_service import (
    ConfirmedMatrixFeeTemplateBasicFillService,
)
from backend.application.confirmed_fee_version_service import (
    ConfirmedFeeVersionService,
)
from backend.application.fee_evaluation_pricing_draft_persistence_service import (
    FeeEvaluationPricingDraftPersistenceService,
    edited_values_from_json,
)
from backend.application.fee_evaluation_template_resource import (
    FeeEvaluationTemplateResourceStore,
    resolve_fee_evaluation_template_path,
)
from backend.application.test_record_template_resource import (
    TestRecordTemplateResourceStore,
    resolve_test_record_template_path,
)
from backend.application.confirmed_matrix_authority_history_service import (
    ConfirmedMatrixAuthorityHistoryService,
)
from backend.application.confirmed_matrix_test_record_document_generation_service import (
    GenerateConfirmedMatrixTestRecordDocumentCommand,
    ConfirmedMatrixTestRecordDocumentGenerationService,
)
from backend.application.matrix_editor_test_record_document_generation_service import (
    MatrixEditorTestRecordDocumentGenerationService,
)
from backend.application.project_section2_sync_service import (
    ProjectSection2SyncService,
)
from backend.application.customer_feedback_form_generation_service import (
    CustomerFeedbackFormGenerationCommand,
    CustomerFeedbackFormGenerationService,
)
from backend.application.customer_feedback_template_discovery import (
    discover_customer_feedback_template,
)
from backend.application.project_folder_required_forms_service import (
    compute_sha256,
    ProjectFolderRequiredFormsService,
)
from backend.application.project_package_preview_service import (
    ProjectPackagePreviewService,
)
from backend.application.official_project_workspace_service import (
    OfficialProjectWorkspaceService,
)
from backend.application.official_project_folder_check_service import (
    OfficialProjectFolderCheckService,
)
from backend.application.public_drive_upload_service import PublicDriveUploadService
from backend.application.public_folder_workflow_service import PublicFolderWorkflowService
from backend.application.project_folder_open_service import ProjectFolderOpenService
from backend.application.public_folder_year_resolver import PublicFolderYearResolver
from backend.application.project_request_material_collection_service import (
    ProjectRequestMaterialCollectionService,
)
from backend.infrastructure.files.llcr_cr_specialized_record_artifact_store import (
    LlcrCrSpecializedRecordArtifactStore,
)
from backend.infrastructure.office.llcr_cr_specialized_record_workbook_gateway import (
    LlcrCrSpecializedRecordWorkbookGateway,
)
from backend.application.project_application_form_write_back_service import (
    ProjectApplicationFormWriteBackService,
)
from backend.application.matrix_revision_flow_service import (
    MatrixRevisionFlowService,
)
from backend.application.matrix_editor_session_service import (
    MatrixEditorSessionService,
    _build_signature_from_project_draft,
)
from backend.application.matrix_fee_pending_rebase_service import (
    DefaultMatrixFeePendingRebaseBuilder,
    MatrixFeePendingRebaseService,
)
from backend.application.matrix_fee_draft_rebase_service import MatrixFeeDraftRebaseService
from backend.application.matrix_fee_rebase_promotion_service import (
    MatrixFeeRebasePromotionService,
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
from backend.application.runtime_projection_read_only_service import (
    RuntimeProjectionReadOnlyService,
)
from backend.infrastructure.files import IntakeStorage
from backend.infrastructure.files.request_material_copy_gateway import (
    RequestMaterialCopyGateway,
)
from backend.infrastructure.files.official_project_folder_repair_gateway import (
    OfficialProjectFolderRepairGateway,
)
from backend.infrastructure.files.public_drive_upload_gateway import (
    PublicDriveUploadGateway,
)
from backend.infrastructure.files.public_folder_workflow_gateway import (
    PublicFolderWorkflowGateway,
)
from backend.infrastructure.files.local_folder_open_gateway import (
    LocalFolderOpenGateway,
)
from backend.infrastructure.files.project_folder_required_forms_gateway import (
    ProjectFolderRequiredFormsFileGateway,
)
from backend.infrastructure.files.application_form_reusable_artifact_store import (
    FileReusableApplicationFormArtifactStore,
)
from backend.infrastructure.files.windows_path_picker import WindowsPathPicker
from backend.infrastructure.office import (
    ExcelComLtrWorkbookReadonlyOpenGateway,
    ExcelComLTRWorkbookGateway,
    FeeEvaluationWorkbookGateway,
    CustomerFeedbackWorkbookGateway,
    TestRecordDocumentGateway,
    LtrWorkbookWriteConfig,
    LtrWorkbookTransactionConfig,
    LtrWorkbookTransactionGateway,
    OfficeFacade,
)
from backend.infrastructure.office.fee_evaluation_export_subprocess_runner import (
    FeeEvaluationExportSubprocessRunner,
)
from backend.infrastructure.storage.database import (
    create_database_engine,
    create_session_factory,
    init_db,
)
from backend.infrastructure.storage.repositories import (
    ApplicationFormRepository,
    ConfirmedFeeAuthorityRepository,
    ConfirmedMatrixAuthorityRepository,
    ExternalResourceRepository,
    FeeEvaluationPricingDraftEditRepository,
    FileAssetRepository,
    FrozenFieldRevisionRequestRepository,
    LtrRecordRepository,
    LtrAssociationEventRepository,
    LtrDuplicateResolutionTokenRepository,
    PrecheckResultRepository,
    ProjectCleanupAuditRecordRepository,
    ProjectBasicInformationRepository,
    ProjectFolderRecordRepository,
    ProjectLifecycleEventRepository,
    ProjectMatrixDraftRepository,
    MatrixFeePendingRebaseRepository,
    ProjectFolderRecordRepository,
    ProjectOfficialWorkspaceRepository,
    ProjectRepository,
    ProjectOutputRecordRepository,
    ProjectTemporaryContextRepository,
    ProjectTestPlanDraftRepository,
    ProjectRequestMaterialCollectionRepository,
    PublicDriveUploadRepository,
    PublicFolderWorkflowRepository,
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
from backend.domain import (
    ExternalResourceType,
    ProjectOutputKind,
    ProjectOutputSource,
    ProjectOutputStatus,
)
from backend.shared.config import OfficialWorkspaceSettings, Settings


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


def _ltr_duplicate_resolution_service(
    session: Session,
    *,
    project_repository: ProjectRepository,
    ltr_repository: LtrRecordRepository,
) -> LocalLtrDuplicateResolutionService:
    """Build the local LTR duplicate resolution service for one request."""
    return LocalLtrDuplicateResolutionService(
        ltr_store=ltr_repository,
        project_store=project_repository,
        token_store=LtrDuplicateResolutionTokenRepository(session),
        event_store=LtrAssociationEventRepository(session),
    )


def get_project_service(session: Session = Depends(get_session)) -> ProjectService:
    """Build a project service for API routes."""
    return ProjectService(
        ProjectRepository(session),
        ProjectTemporaryContextRepository(session),
    )


def get_project_registry_summary_service(
    session: Session = Depends(get_session),
) -> ProjectRegistrySummaryService:
    """Build a read-only Project registry summary service."""
    return ProjectRegistrySummaryService(
        project_store=ProjectRepository(session),
        ltr_store=LtrRecordRepository(session),
        temporary_context_store=ProjectTemporaryContextRepository(session),
        basic_information_store=ProjectBasicInformationRepository(session),
    )


def get_project_basic_information_service(
    session: Session = Depends(get_session),
) -> ProjectBasicInformationService:
    """Build Project Basic Information authority service."""
    return ProjectBasicInformationService(
        project_store=ProjectRepository(session),
        ltr_store=LtrRecordRepository(session),
        application_form_store=ApplicationFormRepository(session),
        sample_store=SampleInfoRepository(session),
        basic_information_store=ProjectBasicInformationRepository(session),
        clock=lambda: datetime.now(timezone.utc).isoformat(),
        lifecycle_write_guard=ProjectLifecycleWriteGuard(ProjectRepository(session)),
    )


def get_project_lifecycle_write_guard(
    session: Session = Depends(get_session),
) -> ProjectLifecycleWriteGuard:
    """Build a lifecycle write guard using Project lifecycle overlay state."""
    return ProjectLifecycleWriteGuard(ProjectRepository(session))


def get_project_lifecycle_management_service(
    session: Session = Depends(get_session),
) -> ProjectLifecycleManagementService:
    """Build project lifecycle stop/delete management service."""
    return ProjectLifecycleManagementService(
        project_store=ProjectRepository(session),
        temporary_context_store=ProjectTemporaryContextRepository(session),
        ltr_store=LtrRecordRepository(session),
        confirmed_matrix_store=ConfirmedMatrixAuthorityRepository(session),
        official_workspace_store=ProjectOfficialWorkspaceRepository(session),
        folder_store=ProjectFolderRecordRepository(session),
        file_asset_store=FileAssetRepository(session),
        output_store=ProjectOutputRecordRepository(session),
        request_material_store=ProjectRequestMaterialCollectionRepository(session),
        confirmed_fee_store=ConfirmedFeeAuthorityRepository(session),
        matrix_draft_store=ProjectMatrixDraftRepository(session),
        audit_store=ProjectCleanupAuditRecordRepository(session),
    )


def get_project_lifecycle_state_service(
    session: Session = Depends(get_session),
) -> ProjectLifecycleStateService:
    """Build TASK_337A project lifecycle overlay service."""
    return ProjectLifecycleStateService(
        project_store=ProjectRepository(session),
        ltr_store=LtrRecordRepository(session),
        event_store=ProjectLifecycleEventRepository(session),
        output_status_service=ProjectOutputRecordService(
            project_store=ProjectRepository(session),
            draft_store=ProjectTestPlanDraftRepository(session),
            output_store=ProjectOutputRecordRepository(session),
        ),
    )


def get_project_test_plan_matrix_preview_service(
    session: Session = Depends(get_session),
) -> ProjectTestPlanMatrixPreviewService:
    """Build the read-only project test-plan Matrix preview service."""
    return ProjectTestPlanMatrixPreviewService(
        basic_information_reader=ProjectBasicInformationSnapshotReader(
            ProjectBasicInformationRepository(session)
        )
    )


def get_matrix_import_commit_service(
    session: Session = Depends(get_session),
) -> MatrixImportCommitService:
    """Build TASK_261 matrix import group-selection commit service."""
    source_store = SourceMatrixImportRepository(session)
    return MatrixImportCommitService(
        project_store=ProjectRepository(session),
        source_store=source_store,
        draft_store=ProjectMatrixDraftRepository(session),
        source_persistence_service=SourceMatrixImportPersistenceService(
            store=source_store
        ),
    )


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


def get_confirmed_matrix_runtime_projection_service(
    session: Session = Depends(get_session),
) -> ConfirmedMatrixRuntimeProjectionService:
    """Build confirmed-authority runtime projection read-only service."""
    return ConfirmedMatrixRuntimeProjectionService(
        confirmed_store=ConfirmedMatrixAuthorityRepository(session),
        runtime_projection_service=RuntimeProjectionReadOnlyService(),
    )


def get_confirmed_matrix_test_record_preview_service(
    session: Session = Depends(get_session),
) -> ConfirmedMatrixTestRecordPreviewService:
    """Build confirmed-authority Test Record preview read-only service."""
    return ConfirmedMatrixTestRecordPreviewService(
        confirmed_store=ConfirmedMatrixAuthorityRepository(session),
    )


def get_confirmed_matrix_fee_draft_service(
    session: Session = Depends(get_session),
) -> ConfirmedMatrixFeeDraftService:
    """Build confirmed-authority Fee Evaluation draft read-only service."""
    return ConfirmedMatrixFeeDraftService(
        confirmed_store=ConfirmedMatrixAuthorityRepository(session),
    )


def get_confirmed_matrix_fee_evaluation_export_service() -> (
    ConfirmedMatrixFeeEvaluationExportTimeoutService
):
    """Build timeout-protected Fee Evaluation workbook export service."""
    return ConfirmedMatrixFeeEvaluationExportTimeoutService(
        runner=FeeEvaluationExportSubprocessRunner()
    )


def get_fee_evaluation_pricing_draft_service(
    session: Session = Depends(get_session),
) -> FeeEvaluationPricingDraftPersistenceService:
    """Build the Fee Evaluation pricing draft persistence service."""
    return FeeEvaluationPricingDraftPersistenceService(
        basic_fill_service=ConfirmedMatrixFeeTemplateBasicFillService(
            confirmed_store=ConfirmedMatrixAuthorityRepository(session),
        ),
        draft_store=FeeEvaluationPricingDraftEditRepository(session),
        lifecycle_write_guard=ProjectLifecycleWriteGuard(ProjectRepository(session)),
    )


def get_confirmed_fee_version_service(
    session: Session = Depends(get_session),
) -> ConfirmedFeeVersionService:
    """Build the Confirmed Fee authority version service."""
    return ConfirmedFeeVersionService(
        pricing_draft_loader=FeeEvaluationPricingDraftPersistenceService(
            basic_fill_service=ConfirmedMatrixFeeTemplateBasicFillService(
                confirmed_store=ConfirmedMatrixAuthorityRepository(session),
            ),
            draft_store=FeeEvaluationPricingDraftEditRepository(session),
            lifecycle_write_guard=ProjectLifecycleWriteGuard(ProjectRepository(session)),
        ),
        confirmed_fee_store=ConfirmedFeeAuthorityRepository(session),
    )


def build_direct_confirmed_matrix_fee_evaluation_export_service(
    session: Session = Depends(get_session),
) -> ConfirmedMatrixFeeEvaluationExportService:
    """Build direct confirmed-authority Fee Evaluation export service."""
    confirmed_store = ConfirmedMatrixAuthorityRepository(session)
    return ConfirmedMatrixFeeEvaluationExportService(
        fee_draft_service=ConfirmedMatrixFeeDraftService(
            confirmed_store=confirmed_store,
        ),
        confirmed_store=confirmed_store,
        project_output_service=ProjectOutputRecordService(
            project_store=ProjectRepository(session),
            draft_store=ProjectTestPlanDraftRepository(session),
            output_store=ProjectOutputRecordRepository(session),
        ),
        workbook_writer=FeeEvaluationWorkbookGateway(),
    )


def get_confirmed_matrix_authority_history_service(
    session: Session = Depends(get_session),
) -> ConfirmedMatrixAuthorityHistoryService:
    """Build confirmed-authority lightweight history read-only service."""
    return ConfirmedMatrixAuthorityHistoryService(
        confirmed_store=ConfirmedMatrixAuthorityRepository(session),
    )


def get_confirmed_matrix_test_record_document_generation_service(
    session: Session = Depends(get_session),
) -> ConfirmedMatrixTestRecordDocumentGenerationService:
    """Build confirmed-authority Test Record Word generation service."""
    return ConfirmedMatrixTestRecordDocumentGenerationService(
        preview_service=ConfirmedMatrixTestRecordPreviewService(
            confirmed_store=ConfirmedMatrixAuthorityRepository(session),
        ),
        project_store=ProjectRepository(session),
        writer=TestRecordDocumentGateway(),
        folder_store=ProjectFolderRecordRepository(session),
        ltr_store=LtrRecordRepository(session),
        intake_case_store=IntakeCaseRepository(session),
        intake_draft_store=IntakeDraftRepository(session),
        application_form_store=ApplicationFormRepository(session),
        basic_information_reader=ProjectBasicInformationSnapshotReader(
            ProjectBasicInformationRepository(session)
        ),
    )


def get_matrix_editor_test_record_document_generation_service(
    session: Session = Depends(get_session),
) -> MatrixEditorTestRecordDocumentGenerationService:
    """Build Matrix-Editor-current-state Test Record preview generation service."""
    return MatrixEditorTestRecordDocumentGenerationService(
        project_store=ProjectRepository(session),
        writer=TestRecordDocumentGateway(),
        ltr_store=LtrRecordRepository(session),
        intake_case_store=IntakeCaseRepository(session),
        intake_draft_store=IntakeDraftRepository(session),
        application_form_store=ApplicationFormRepository(session),
    )


def get_matrix_revision_flow_service(
    session: Session = Depends(get_session),
) -> MatrixRevisionFlowService:
    """Build backend Matrix revision flow service."""
    return MatrixRevisionFlowService(
        project_store=ProjectRepository(session),
        draft_store=ProjectMatrixDraftRepository(session),
        confirmed_store=ConfirmedMatrixAuthorityRepository(session),
    )


def get_matrix_editor_session_service(
    session: Session = Depends(get_session),
) -> MatrixEditorSessionService:
    """Build Matrix Editor temporary session service."""
    confirmed_store = ConfirmedMatrixAuthorityRepository(session)
    matrix_draft_store = ProjectMatrixDraftRepository(session)
    return MatrixEditorSessionService(
        project_store=ProjectRepository(session),
        confirmed_store=confirmed_store,
        source_store=SourceMatrixImportRepository(session),
        draft_store=matrix_draft_store,
        draft_persistence_service=ProjectMatrixDraftPersistenceService(
            project_store=ProjectRepository(session),
            source_store=SourceMatrixImportRepository(session),
            draft_store=matrix_draft_store,
        ),
        matrix_import_commit_service=MatrixImportCommitService(
            project_store=ProjectRepository(session),
            source_store=SourceMatrixImportRepository(session),
            draft_store=matrix_draft_store,
            source_persistence_service=SourceMatrixImportPersistenceService(
                store=SourceMatrixImportRepository(session)
            ),
        ),
        matrix_revision_flow_service=MatrixRevisionFlowService(
            project_store=ProjectRepository(session),
            draft_store=matrix_draft_store,
            confirmed_store=confirmed_store,
        ),
        confirmed_matrix_authority_service=ConfirmedMatrixAuthorityService(
            project_store=ProjectRepository(session),
            draft_store=matrix_draft_store,
            confirmed_store=confirmed_store,
        ),
        pending_fee_rebase_service=MatrixFeePendingRebaseService(
            draft_store=matrix_draft_store,
            pending_store=MatrixFeePendingRebaseRepository(session),
            rebase_builder=DefaultMatrixFeePendingRebaseBuilder(
                basic_fill_service=ConfirmedMatrixFeeTemplateBasicFillService(
                    confirmed_store=confirmed_store,
                ),
                pricing_draft_store=FeeEvaluationPricingDraftEditRepository(session),
            ),
            draft_signature_builder=_build_signature_from_project_draft,
        ),
        fee_rebase_promotion_service=MatrixFeeRebasePromotionService(
            pending_store=MatrixFeePendingRebaseRepository(session),
            pricing_draft_store=FeeEvaluationPricingDraftEditRepository(session),
            confirmed_fee_store=ConfirmedFeeAuthorityRepository(session),
            rebase_service=MatrixFeeDraftRebaseService(),
        ),
        lifecycle_write_guard=ProjectLifecycleWriteGuard(ProjectRepository(session)),
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


def get_project_section2_sync_service(
    session: Session = Depends(get_session),
) -> ProjectSection2SyncService:
    """Build the structured Project Section 2 date sync service."""
    return ProjectSection2SyncService(
        project_store=ProjectRepository(session),
        confirmed_matrix_store=ConfirmedMatrixAuthorityRepository(session),
        application_form_store=ApplicationFormRepository(session),
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


def get_contact_measurement_plan_projection_service(
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
):
    """Compose the task-scoped read boundary without exposing the feature flag to routes."""
    from backend.application.contact_measurement_plan_projection_service import (
        ContactMeasurementPlanProjectionService,
    )
    from backend.infrastructure.storage.repositories.contact_measurement_plan_authority import (
        ContactMeasurementPlanAuthorityRepository,
    )
    return ContactMeasurementPlanProjectionService(
        ContactMeasurementPlanAuthorityRepository(session),
        settings.contact_measurement_plan_authority_enabled,
        ConfirmedMatrixAuthorityRepository(session),
    )


def get_contact_measurement_plan_workspace_read_service(
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
):
    """Compose the narrow TASK_361C read-only operator workspace boundary."""
    from backend.application.contact_measurement_plan_workspace_read_service import (
        ContactMeasurementPlanWorkspaceReadService,
    )
    from backend.infrastructure.storage.repositories.contact_measurement_plan_authority import (
        ContactMeasurementPlanAuthorityRepository,
    )

    return ContactMeasurementPlanWorkspaceReadService(
        repository=ContactMeasurementPlanAuthorityRepository(session),
        confirmed_store=ConfirmedMatrixAuthorityRepository(session),
        enabled=settings.contact_measurement_plan_authority_enabled,
    )


def get_contact_measurement_plan_lifecycle_service(
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
):
    from datetime import datetime, timezone
    from backend.application.contact_measurement_plan_bootstrap_service import ContactMeasurementPlanBootstrapService
    from backend.application.contact_measurement_plan_lifecycle_service import ContactMeasurementPlanLifecycleService
    from backend.infrastructure.storage.repositories import ConfirmedMatrixAuthorityRepository
    from backend.infrastructure.storage.repositories.contact_measurement_plan_authority import ContactMeasurementPlanAuthorityRepository
    repository = ContactMeasurementPlanAuthorityRepository(session)
    clock = lambda: datetime.now(timezone.utc).isoformat()
    return ContactMeasurementPlanLifecycleService(
        repository,
        ConfirmedMatrixAuthorityRepository(session),
        ContactMeasurementPlanBootstrapService(repository, clock),
        clock,
        enabled=settings.contact_measurement_plan_authority_enabled,
    )


def get_llcr_cr_record_workbook_artifact_store(
    settings: Settings = Depends(get_settings),
) -> LlcrCrSpecializedRecordArtifactStore:
    """Build contained local storage for specialized LLCR/CR workbook artifacts."""
    return LlcrCrSpecializedRecordArtifactStore(
        settings.data_dir / "generated_llcr_cr_record_files"
    )


def get_llcr_cr_record_workbook_preview_service(
    session: Session = Depends(get_session),
) -> LlcrCrRecordWorkbookPreviewService:
    """Build no-write preview from active confirmed Matrix contact authority."""
    return LlcrCrRecordWorkbookPreviewService(
        confirmed_store=ConfirmedMatrixAuthorityRepository(session),
    )


def get_llcr_cr_record_workbook_generation_service(
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> LlcrCrRecordWorkbookGenerationService:
    """Build preview-fingerprint-protected specialized workbook generation."""
    return LlcrCrRecordWorkbookGenerationService(
        preview_service=LlcrCrRecordWorkbookPreviewService(
            confirmed_store=ConfirmedMatrixAuthorityRepository(session),
        ),
        workbook_gateway=LlcrCrSpecializedRecordWorkbookGateway(),
        artifact_store=LlcrCrSpecializedRecordArtifactStore(
            settings.data_dir / "generated_llcr_cr_record_files"
        ),
    )


def get_official_project_workspace_service(
    session: Session = Depends(get_session),
) -> OfficialProjectWorkspaceService:
    """Build the official project workspace service for API routes."""
    external_resources = ExternalResourceRepository(session)
    return OfficialProjectWorkspaceService(
        project_repository=ProjectRepository(session),
        workspace_repository=ProjectOfficialWorkspaceRepository(session),
        ltr_repository=LtrRecordRepository(session),
        application_form_repository=ApplicationFormRepository(session),
        settings=_official_workspace_settings_from_registry(
            external_resources,
        ),
    )


def _official_workspace_settings_from_registry(
    resources: ExternalResourceRepository,
) -> OfficialWorkspaceSettings:
    """Return official workspace settings from ordinary Settings locations only."""
    local_workspace_root = _active_resource_path(
        resources,
        ExternalResourceType.PROJECT_OUTPUT_ROOT,
    )
    template_path = _active_resource_path(
        resources,
        ExternalResourceType.PROJECT_FOLDER_TEMPLATE,
    )
    public_drive_root = _active_resource_path(
        resources,
        ExternalResourceType.OFFICIAL_PUBLIC_DRIVE_ROOT,
    )
    return OfficialWorkspaceSettings(
        local_workspace_root=local_workspace_root,
        template_path=template_path,
        public_drive_root=public_drive_root,
    )


def _active_resource_path(
    resources: ExternalResourceRepository,
    resource_type: ExternalResourceType,
):
    """Return an active Settings-page resource path when configured."""
    resource = resources.get_by_type(resource_type)
    if resource is None or not resource.active:
        return None
    return resource.path


def get_customer_feedback_form_generation_service(
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> CustomerFeedbackFormGenerationService:
    """Build the Customer Feedback Form generation service for API routes."""
    return CustomerFeedbackFormGenerationService(
        project_store=ProjectRepository(session),
        external_resource_store=ExternalResourceRepository(session),
        workbook_gateway=CustomerFeedbackWorkbookGateway(),
        generated_root=settings.data_dir / "generated_customer_feedback",
    )


def get_project_package_preview_service(
    session: Session = Depends(get_session),
) -> ProjectPackagePreviewService:
    """Build the read-only project package preview service."""
    return ProjectPackagePreviewService(
        project_store=ProjectRepository(session),
        folder_store=ProjectFolderRecordRepository(session),
        confirmed_matrix_store=ConfirmedMatrixAuthorityRepository(session),
        confirmed_fee_reader=get_confirmed_fee_version_service(session),
        section2_previewer=get_project_section2_sync_service(session),
        external_resource_store=ExternalResourceRepository(session),
        official_workspace_store=ProjectOfficialWorkspaceRepository(session),
    )


def get_project_request_material_collection_service(
    session: Session = Depends(get_session),
) -> ProjectRequestMaterialCollectionService:
    """Build the request-material collection service for Project Folder routes."""
    return ProjectRequestMaterialCollectionService(
        project_repository=ProjectRepository(session),
        workspace_repository=ProjectOfficialWorkspaceRepository(session),
        file_asset_repository=FileAssetRepository(session),
        collection_repository=ProjectRequestMaterialCollectionRepository(session),
        copy_gateway=RequestMaterialCopyGateway(),
    )


def get_project_application_form_write_back_service(
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> ProjectApplicationFormWriteBackService:
    """Build the Project Folder Application Form write-back service."""
    output_service = get_project_output_record_service(session)
    return ProjectApplicationFormWriteBackService(
        project_store=ProjectRepository(session),
        workspace_store=ProjectOfficialWorkspaceRepository(session),
        application_form_store=ApplicationFormRepository(session),
        file_asset_store=FileAssetRepository(session),
        request_material_collection_store=ProjectRequestMaterialCollectionRepository(
            session
        ),
        basic_information_reader=ProjectBasicInformationSnapshotReader(
            ProjectBasicInformationRepository(session)
        ),
        output_record_service=output_service,
        reusable_artifact_store=FileReusableApplicationFormArtifactStore(
            output_service,
            settings.data_dir / "application_form_write_back_cache",
        ),
    )


def get_official_project_folder_check_service(
    session: Session = Depends(get_session),
) -> OfficialProjectFolderCheckService:
    """Build the Official project folder check/repair service."""
    return OfficialProjectFolderCheckService(
        project_repository=ProjectRepository(session),
        workspace_repository=ProjectOfficialWorkspaceRepository(session),
        repair_gateway=OfficialProjectFolderRepairGateway(),
        request_material_service=get_project_request_material_collection_service(session),
        output_status_service=get_project_output_record_service(session),
    )


def get_public_drive_upload_service(
    session: Session = Depends(get_session),
) -> PublicDriveUploadService:
    """Build the public-drive Project Folder upload service."""
    resources = ExternalResourceRepository(session)
    return PublicDriveUploadService(
        project_repository=ProjectRepository(session),
        workspace_repository=ProjectOfficialWorkspaceRepository(session),
        public_drive_root=_active_resource_path(
            resources,
            ExternalResourceType.OFFICIAL_PUBLIC_DRIVE_ROOT,
        ),
        folder_check_service=get_official_project_folder_check_service(session),
        upload_repository=PublicDriveUploadRepository(session),
        gateway=PublicDriveUploadGateway(),
    )


def get_public_folder_workflow_service(
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> PublicFolderWorkflowService:
    """Build the TASK_346C public folder workflow service."""
    resources = ExternalResourceRepository(session)
    project_repository = ProjectRepository(session)
    ltr_repository = LtrRecordRepository(session)
    return PublicFolderWorkflowService(
        project_repository=project_repository,
        workspace_repository=ProjectOfficialWorkspaceRepository(session),
        year_resolver=PublicFolderYearResolver(
            project_repository=project_repository,
            ltr_repository=ltr_repository,
            workbook_lookup=_readonly_ltr_sheet_lookup(settings),
        ),
        workflow_repository=PublicFolderWorkflowRepository(session),
        folder_check_service=get_official_project_folder_check_service(session),
        public_root=_active_resource_path(
            resources,
            ExternalResourceType.OFFICIAL_PUBLIC_DRIVE_ROOT,
        ),
        gateway=PublicFolderWorkflowGateway(),
    )


def get_project_folder_open_service(
    workflow_service: PublicFolderWorkflowService = Depends(
        get_public_folder_workflow_service
    ),
) -> ProjectFolderOpenService:
    """Build the non-mutating local project-folder open service."""
    return ProjectFolderOpenService(
        workflow_service=workflow_service,
        gateway=LocalFolderOpenGateway(),
    )


class _ReadonlyLtrSheetLookup:
    """Adapter for exact DL-to-sheet lookup through read-only workbook sessions."""

    def __init__(self, gateway: ExcelComLTRWorkbookGateway) -> None:
        self._gateway = gateway

    def find_sheet_name(self, ltr_number: str) -> str | None:
        """Return the sheet name containing an exact DL number."""
        with self._gateway.open_read_session() as session:
            row = session.find_ltr_number(ltr_number)
        return row.sheet_name if row else None


def _readonly_ltr_sheet_lookup(settings: Settings):
    """Return optional read-only LTR workbook lookup when configured."""
    if settings.ltr_workbook.path is None:
        return None
    return _ReadonlyLtrSheetLookup(
        ExcelComLTRWorkbookGateway(
            OfficeFacade(),
            LtrWorkbookWriteConfig(
                path=settings.ltr_workbook.path,
                write_enabled=False,
                modify_password=None,
            ),
        )
    )


class _ConfirmedMatrixReader:
    """Adapter exposing active Confirmed Matrix snapshots to Required forms."""

    def __init__(self, store: ConfirmedMatrixAuthorityRepository) -> None:
        self._store = store

    def get_active_snapshot(self, project_id: str):
        """Return active Confirmed Matrix snapshot for one project."""
        return self._store.get_active_by_project(project_id)


class _CustomerFeedbackTemplateReader:
    """Adapter for Customer Feedback template discovery."""

    def __init__(self, resources: ExternalResourceRepository) -> None:
        self._resources = resources

    def preview_template(self, project_id: str) -> Path:
        """Return the unique Customer Feedback template path."""
        resource = self._resources.get_by_type(ExternalResourceType.PROJECT_FOLDER_TEMPLATE)
        if resource is None:
            raise ValueError("Template folder is not configured.")
        return discover_customer_feedback_template(Path(resource.path))


class _NoopProjectOutputService:
    """Output service used by staging generators to avoid final output side effects."""

    def __init__(self, real_service: ProjectOutputRecordService) -> None:
        self._real_service = real_service

    def get_status_summary(self, project_id: str):
        """Return the real active draft context."""
        return self._real_service.get_status_summary(project_id)

    def register_output(self, command):
        """Return a no-op record-like object instead of persisting staging output."""
        class _Record:
            output_record_id = None

        return _Record()


class _ReusableFeeFormArtifactReader:
    """Find safe current generated Fee Form artifacts for Required forms reuse."""

    def __init__(self, output_service: ProjectOutputRecordService) -> None:
        self._output_service = output_service

    def find_current_artifact(
        self,
        *,
        project_id: str,
        source_context_signature: str,
        final_target_path: Path,
    ) -> Path | None:
        """Return a reusable generated Fee Form source path when safe."""
        summary = self._output_service.get_status_summary(project_id)
        for item in summary.items:
            if item.output_kind != ProjectOutputKind.FEE_EVALUATION:
                continue
            if item.status != ProjectOutputStatus.CURRENT:
                return None
            if item.source != ProjectOutputSource.SYSTEM_GENERATED:
                return None
            if item.source_context_signature != source_context_signature:
                return None
            if not item.output_path or not item.output_sha256:
                return None
            path = Path(item.output_path)
            if path == final_target_path:
                return None
            if path.suffix.lower() != ".xls" or not path.is_file():
                return None
            if compute_sha256(path) != item.output_sha256:
                return None
            return path
        return None


class _FeeFormTemplateContextReader:
    """Build Fee Form template identity for Required forms reuse context."""

    def __init__(self, resource_store: FeeEvaluationTemplateResourceStore) -> None:
        self._resource_store = resource_store

    def preview_template_context(self, project_id: str) -> str:
        """Return a stable Fee Form template context token."""
        template = resolve_fee_evaluation_template_path(self._resource_store)
        return _fee_form_template_context(template)


def _fee_form_template_context(template: Path) -> str:
    """Return a stable template identity for Required Forms reuse checks.

    Legacy `.xls` workbooks can have Office/OLE metadata rewritten by Excel even
    when ConnLab only opens them as templates. Using a full-file SHA for those
    files makes every preview look stale. The template filename carries the
    controlled form number/revision, so use path + size as the stable identity
    for `.xls` and keep content hashes for non-legacy workbooks.
    """
    resolved = template.resolve()
    if template.suffix.lower() == ".xls":
        return f"fee-template:{resolved}@legacy-xls-stable:size:{template.stat().st_size}"
    return f"fee-template:{resolved}@sha256:{compute_sha256(template)}"


class _RequiredFormsStagingGenerator:
    """Generate Required forms into controlled staging without final output records."""

    def __init__(
        self,
        *,
        project_id: str | None = None,
        settings: Settings,
        fee_template_resource_store: FeeEvaluationTemplateResourceStore,
        test_record_template_resource_store: TestRecordTemplateResourceStore | None = None,
        test_record_service: ConfirmedMatrixTestRecordDocumentGenerationService,
        fee_export_service: ConfirmedMatrixFeeEvaluationExportService,
        customer_feedback_service: CustomerFeedbackFormGenerationService,
    ) -> None:
        self._project_id = project_id
        self._settings = settings
        self._fee_template_resource_store = fee_template_resource_store
        self._test_record_template_resource_store = (
            test_record_template_resource_store or fee_template_resource_store
        )
        self._test_record_service = test_record_service
        self._fee_export_service = fee_export_service
        self._customer_feedback_service = customer_feedback_service

    def generate(
        self,
        *,
        project_id: str,
        key: str,
        target_name: str,
        basic_information: ConfirmedBasicInformationSnapshot,
        confirmed_fee: object,
    ) -> Path:
        """Generate one Required form into staging and return the staged file path."""
        output_dir = self._settings.data_dir / "staged_required_forms" / project_id
        output_dir.mkdir(parents=True, exist_ok=True)
        if key == "test_record":
            template_path = resolve_test_record_template_path(
                self._test_record_template_resource_store,
                configured_template_path=self._settings.test_record.template_path,
            )
            result = self._test_record_service.generate(
                GenerateConfirmedMatrixTestRecordDocumentCommand(
                    project_id=project_id,
                    output_dir=output_dir,
                    template_path=template_path,
                )
            )
            return _rename_staged_file(result.output_path, target_name)
        if key == "fee_form":
            try:
                edited_values = edited_values_from_json(
                    str(getattr(confirmed_fee, "pricing_snapshot_json"))
                )
            except (AttributeError, KeyError, TypeError, ValueError) as exc:
                raise ValueError(
                    "Confirmed Fee pricing snapshot is not available for Fee Form generation."
                ) from exc
            result = self._fee_export_service.export(
                ExportConfirmedMatrixFeeEvaluationCommand(
                    project_id=project_id,
                    template_path=resolve_fee_evaluation_template_path(
                        self._fee_template_resource_store
                    ),
                    output_dir=output_dir,
                    output_file_name=target_name,
                    overwrite=True,
                    allow_review_required=True,
                    fill_mode="matrix_basic",
                    edited_values=edited_values,
                    basic_information_values=fee_form_identity(
                        basic_information
                    ).as_dict(),
                )
            )
            return result.output_path
        if key == "customer_feedback_form":
            result = self._customer_feedback_service.generate(
                CustomerFeedbackFormGenerationCommand(
                    project_id=project_id,
                    basic_information_values=dict(basic_information.values),
                )
            )
            return _rename_staged_file(result.output_path, target_name)
        raise ValueError(f"Unsupported Required form key: {key}")


def _rename_staged_file(path: Path, target_name: str) -> Path:
    """Rename a staged file to the deterministic target name when needed."""
    target = path.with_name(target_name)
    if path == target:
        return path
    target.unlink(missing_ok=True)
    path.replace(target)
    return target


def get_project_folder_required_forms_service(
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> ProjectFolderRequiredFormsService:
    """Build the Project Folder Required forms service."""
    confirmed_store = ConfirmedMatrixAuthorityRepository(session)
    output_service = ProjectOutputRecordService(
        project_store=ProjectRepository(session),
        draft_store=ProjectTestPlanDraftRepository(session),
        output_store=ProjectOutputRecordRepository(session),
    )
    test_record_service = ConfirmedMatrixTestRecordDocumentGenerationService(
        preview_service=ConfirmedMatrixTestRecordPreviewService(
            confirmed_store=confirmed_store,
        ),
        project_store=ProjectRepository(session),
        writer=TestRecordDocumentGateway(),
        folder_store=None,
        ltr_store=LtrRecordRepository(session),
        intake_case_store=IntakeCaseRepository(session),
        intake_draft_store=IntakeDraftRepository(session),
        application_form_store=ApplicationFormRepository(session),
        basic_information_reader=ProjectBasicInformationSnapshotReader(
            ProjectBasicInformationRepository(session)
        ),
    )
    fee_service = ConfirmedMatrixFeeEvaluationExportService(
        fee_draft_service=ConfirmedMatrixFeeDraftService(
            confirmed_store=confirmed_store,
        ),
        confirmed_store=confirmed_store,
        project_output_service=_NoopProjectOutputService(output_service),
        workbook_writer=FeeEvaluationWorkbookGateway(),
    )
    return ProjectFolderRequiredFormsService(
        workspace_repository=ProjectOfficialWorkspaceRepository(session),
        folder_check_service=get_official_project_folder_check_service(session),
        confirmed_matrix_reader=_ConfirmedMatrixReader(confirmed_store),
        confirmed_fee_reader=get_confirmed_fee_version_service(session),
        basic_information_reader=ProjectBasicInformationSnapshotReader(
            ProjectBasicInformationRepository(session)
        ),
        customer_feedback_template_reader=_CustomerFeedbackTemplateReader(
            ExternalResourceRepository(session)
        ),
        fee_form_template_context_reader=_FeeFormTemplateContextReader(
            ExternalResourceRepository(session)
        ),
        application_form_reader=ApplicationFormRepository(session),
        generator=_RequiredFormsStagingGenerator(
            settings=settings,
            fee_template_resource_store=ExternalResourceRepository(session),
            test_record_service=test_record_service,
            fee_export_service=fee_service,
            customer_feedback_service=get_customer_feedback_form_generation_service(
                session,
                settings,
            ),
        ),
        file_gateway=ProjectFolderRequiredFormsFileGateway(),
        output_status_service=output_service,
        reusable_fee_form_reader=_ReusableFeeFormArtifactReader(output_service),
        lifecycle_write_guard=ProjectLifecycleWriteGuard(ProjectRepository(session)),
    )


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


def get_fee_evaluation_template_resource_store(
    session: Session = Depends(get_session),
) -> FeeEvaluationTemplateResourceStore:
    """Build the resource store used to resolve Fee Evaluation templates."""
    return ExternalResourceRepository(session)


def get_test_record_template_resource_store(
    session: Session = Depends(get_session),
) -> TestRecordTemplateResourceStore:
    """Build the resource store used to resolve Test Record templates."""
    return ExternalResourceRepository(session)


def get_ltr_workbook_local_config_service() -> LtrWorkbookLocalConfigService:
    """Build the local config synchronizer for LTR workbook settings."""
    return LtrWorkbookLocalConfigService()


def get_external_excel_read_service(
    session: Session = Depends(get_session),
) -> ExternalExcelReadService:
    """Build the read-only external Excel structured read service."""
    return ExternalExcelReadService(ExternalResourceRepository(session))


def get_local_path_picker_service() -> LocalPathPickerService:
    """Build the native local path picker service."""
    return LocalPathPickerService(WindowsPathPicker())


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
    ltr_repository = LtrRecordRepository(session)
    return LtrService(
        project_repository=project_repository,
        ltr_repository=ltr_repository,
        lifecycle_guard=ProjectLifecycleService(project_repository),
        duplicate_resolution_service=_ltr_duplicate_resolution_service(
            session,
            project_repository=project_repository,
            ltr_repository=ltr_repository,
        ),
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
    duplicate_resolution_service = _ltr_duplicate_resolution_service(
        session,
        project_repository=project_repository,
        ltr_repository=ltr_repository,
    )
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
            duplicate_resolution_service=duplicate_resolution_service,
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
    duplicate_resolution_service = _ltr_duplicate_resolution_service(
        session,
        project_repository=project_repository,
        ltr_repository=ltr_repository,
    )
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
            backup_retention_count=settings.ltr_workbook.backup_retention_count,
            backup_retention_days=settings.ltr_workbook.backup_retention_days,
            backup_retention_max_mb=settings.ltr_workbook.backup_retention_max_mb,
        ),
    )
    return LtrWorkbookWriteCommitService(
        preview_service=preview_service,
        transaction_gateway=transaction_gateway,
        ltr_service=LtrService(
            project_repository=project_repository,
            ltr_repository=ltr_repository,
            lifecycle_guard=lifecycle_guard,
            duplicate_resolution_service=duplicate_resolution_service,
        ),
        ltr_store=ltr_repository,
        project_store=project_repository,
        duplicate_resolution_service=duplicate_resolution_service,
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


def get_ltr_workbook_basic_information_sync_service(
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> LtrWorkbookBasicInformationSyncService:
    """Build the post-registration LTR workbook Basic Information sync service."""
    transaction_gateway = LtrWorkbookTransactionGateway(
        OfficeFacade(),
        LtrWorkbookTransactionConfig(
            path=settings.ltr_workbook.path,
            write_enabled=settings.ltr_workbook.write_enabled,
            modify_password=settings.ltr_workbook.modify_password,
            lock_dir=settings.ltr_workbook.lock_dir,
            lock_timeout_seconds=settings.ltr_workbook.lock_timeout_seconds,
            backup_dir=settings.ltr_workbook.backup_dir,
            backup_retention_count=settings.ltr_workbook.backup_retention_count,
            backup_retention_days=settings.ltr_workbook.backup_retention_days,
            backup_retention_max_mb=settings.ltr_workbook.backup_retention_max_mb,
        ),
    )
    return LtrWorkbookBasicInformationSyncService(
        ltr_store=LtrRecordRepository(session),
        basic_information_reader=ProjectBasicInformationSnapshotReader(
            ProjectBasicInformationRepository(session)
        ),
        transaction_gateway=transaction_gateway,
        readonly_open_gateway=ExcelComLtrWorkbookReadonlyOpenGateway(
            modify_password=settings.ltr_workbook.modify_password,
        ),
        lifecycle_write_guard=ProjectLifecycleWriteGuard(ProjectRepository(session)),
    )


def get_specified_ltr_workbook_authority_preview_service(
    settings: Settings = Depends(get_settings),
) -> SpecifiedLtrWorkbookAuthorityPreviewService:
    """Build the read-only specified LTR workbook authority preview service."""
    transaction_gateway = LtrWorkbookTransactionGateway(
        OfficeFacade(),
        LtrWorkbookTransactionConfig(
            path=settings.ltr_workbook.path,
            write_enabled=False,
            modify_password=settings.ltr_workbook.modify_password,
            lock_dir=settings.ltr_workbook.lock_dir,
            lock_timeout_seconds=settings.ltr_workbook.lock_timeout_seconds,
            backup_dir=settings.ltr_workbook.backup_dir,
            backup_retention_count=settings.ltr_workbook.backup_retention_count,
            backup_retention_days=settings.ltr_workbook.backup_retention_days,
            backup_retention_max_mb=settings.ltr_workbook.backup_retention_max_mb,
        ),
    )
    return SpecifiedLtrWorkbookAuthorityPreviewService(
        transaction_gateway=transaction_gateway
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
    specified_ltr_preview_service: SpecifiedLtrWorkbookAuthorityPreviewService = Depends(
        get_specified_ltr_workbook_authority_preview_service
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
        application_form_store=ApplicationFormRepository(session),
        confirmation_service=confirmation_service,
        ltr_commit_service=ltr_commit_service,
        specified_ltr_preview_service=specified_ltr_preview_service,
        duplicate_resolution_service=_ltr_duplicate_resolution_service(
            session,
            project_repository=project_repository,
            ltr_repository=ltr_repository,
        ),
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
