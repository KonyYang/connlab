"""Compose existing authorities and generators for the per-file operation protocol."""
from backend.application.project_file_generation_sources import ProjectFileGenerationSources
from backend.application.project_file_generation_staging import RequiredFormsInputContextReader, RequiredFormsStagingGenerator


class _SourceFilesystem:
    from backend.infrastructure.files.generation_journal import fingerprint
    from backend.infrastructure.files.recoverable_output_publisher import file_hash as hash, file_identity as identity, require_safe_output_path as require_safe
    fingerprint = staticmethod(fingerprint)
    hash = staticmethod(hash)
    identity = staticmethod(identity)
    require_safe = staticmethod(require_safe)

    @staticmethod
    def is_dir(path): return path.is_dir()
    @staticmethod
    def is_file(path): return path.is_file()
    @staticmethod
    def is_empty(path): return not any(path.iterdir())
    @staticmethod
    def size(path): return path.stat().st_size


def build_components(session, settings):
    # Keep database/Office construction at the API boundary, outside application rules.
    from backend.api import dependencies as d
    resources = d.ExternalResourceRepository(session)
    confirmed = d.ConfirmedMatrixAuthorityRepository(session)
    projects = d.ProjectRepository(session)
    basic = d.ProjectBasicInformationSnapshotReader(d.ProjectBasicInformationRepository(session))
    schedules = d.get_project_schedule_output_reader(session)
    outputs = d.get_project_output_record_service(session)
    test_record = d.ConfirmedMatrixTestRecordDocumentGenerationService(
        preview_service=d.ConfirmedMatrixTestRecordPreviewService(confirmed_store=confirmed),
        project_store=projects, writer=d.TestRecordDocumentGateway(), folder_store=None,
        ltr_store=d.LtrRecordRepository(session), intake_case_store=d.IntakeCaseRepository(session),
        intake_draft_store=d.IntakeDraftRepository(session), application_form_store=d.ApplicationFormRepository(session),
        basic_information_reader=basic)
    fee_export = d.ConfirmedMatrixFeeEvaluationExportService(
        fee_draft_service=d.ConfirmedMatrixFeeDraftService(confirmed_store=confirmed,
            contact_measurement_adapter=d._confirmed_contact_measurement_consumer_adapter(session,settings),
            contact_point_profile_adapter=d._confirmed_contact_point_profile_consumer_adapter(session)),
        confirmed_store=confirmed, project_output_service=d._NoopProjectOutputService(outputs),
        workbook_writer=d.FeeEvaluationWorkbookGateway())

    def feedback(stage_dir):
        return d.CustomerFeedbackFormGenerationService(project_store=projects,
            external_resource_store=resources, workbook_gateway=d.CustomerFeedbackWorkbookGateway(),
            generated_root=stage_dir, project_schedule_reader=schedules)

    staging = RequiredFormsStagingGenerator(settings=settings, fee_template_resource_store=resources,
        test_record_service=test_record, fee_export_service=fee_export, customer_feedback_service=None,
        customer_feedback_factory=feedback,
        test_status_service=d.ConfirmedMatrixTestStatusWorkbookGenerationService(
            confirmed_store=confirmed,writer=d.TestStatusWorkbookGateway()))
    return ProjectFileGenerationSources(workspaces=d.ProjectOfficialWorkspaceRepository(session),
        basic_workspace=d.get_basic_project_workspace_service(session,settings),
        confirmed=confirmed,basic=basic,fees=d.get_confirmed_fee_version_service(session),
        resources=resources,settings=settings,schedules=schedules,
        input_context=RequiredFormsInputContextReader(resources,settings,schedules,test_record),
        staging=staging,application=d.get_project_application_form_write_back_service(session,settings),
        llcr=d.get_llcr_cr_record_workbook_preview_service(session),
        llcr_writer=d.LlcrCrSpecializedRecordWorkbookGateway(),
        ir=d.get_matrix_editor_ir_dwv_record_generation_service(session,settings),
        outputs=outputs,commit=session.commit,files=_SourceFilesystem(),forms=d.ApplicationFormRepository(session))
