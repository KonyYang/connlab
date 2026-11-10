"""Reusable generation inputs and staging, with an explicit operation directory seam."""
from __future__ import annotations

from pathlib import Path
from backend.application.project_basic_information_output import ConfirmedBasicInformationSnapshot
from backend.domain import ExternalResourceType
from backend.application.customer_feedback_template_discovery import discover_customer_feedback_template
from backend.application.project_folder_required_forms_service import compute_sha256
from backend.application.test_record_template_resource import resolve_test_record_template_path
from backend.application.fee_evaluation_template_resource import resolve_fee_evaluation_template_path
from backend.application.project_basic_information_output_identity import fee_form_identity
from backend.application.fee_evaluation_pricing_draft_persistence_service import edited_values_from_json
from backend.application.confirmed_fee_pricing_snapshot import edited_values_json_from_confirmed_fee_snapshot
from backend.application.confirmed_matrix_fee_evaluation_export_service import ExportConfirmedMatrixFeeEvaluationCommand
from backend.application.confirmed_matrix_test_record_document_generation_service import GenerateConfirmedMatrixTestRecordDocumentCommand
from backend.application.confirmed_matrix_test_status_workbook_generation_service import GenerateConfirmedMatrixTestStatusWorkbookCommand
from backend.application.customer_feedback_form_generation_service import CustomerFeedbackFormGenerationCommand

class RequiredFormsInputContextReader:
    """Bind each form to its own template and additional document inputs."""

    def __init__(self, resources, settings, schedules, test_record):
        self.resources, self.settings = resources, settings
        self.schedules, self.test_record = schedules, test_record

    def context(self, project_id, key):
        import json
        if key == "test_record":
            template = resolve_test_record_template_path(
                self.resources, configured_template_path=self.settings.test_record.template_path)
            inputs = self.test_record.preview_inputs(project_id)
        elif key == "customer_feedback_form":
            resource = self.resources.get_by_type(ExternalResourceType.PROJECT_FOLDER_TEMPLATE)
            if resource is None:
                raise ValueError("Template folder is not configured.")
            template = discover_customer_feedback_template(Path(resource.path))
            schedule = self.schedules.get_latest_confirmed(project_id)
            if schedule is None:
                raise ValueError("Confirm Matrix plan dates before generating Customer Feedback.")
            inputs = {"schedule": schedule.context_signature}
        else:
            raise ValueError("Unsupported form input context.")
        return f"template:{template.resolve()}@sha256:{compute_sha256(template)}|{json.dumps(inputs, sort_keys=True)}"


class RequiredFormsStagingGenerator:
    """Generate Required forms into controlled staging without final output records."""

    def __init__(
        self,
        *,
        project_id: str | None = None,
        settings,
        fee_template_resource_store,
        test_record_template_resource_store=None,
        test_record_service,
        fee_export_service,
        customer_feedback_service,
        test_status_service=None,
        customer_feedback_factory=None,
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
        self._test_status_service = test_status_service
        self._customer_feedback_factory = customer_feedback_factory

    def generate(
        self,
        *,
        project_id: str,
        key: str,
        target_name: str,
        basic_information: ConfirmedBasicInformationSnapshot | None,
        confirmed_fee: object,
        stage_dir: Path | None = None,
    ) -> Path:
        """Generate one Required form into staging and return the staged file path."""
        output_dir = stage_dir if stage_dir is not None else self._settings.data_dir / "staged_required_forms" / project_id
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
        if key == "test_status":
            if self._test_status_service is None:
                raise ValueError("Test Status generation is not configured.")
            return self._test_status_service.generate(
                GenerateConfirmedMatrixTestStatusWorkbookCommand(
                    project_id=project_id,
                    output_dir=output_dir,
                    target_name=target_name,
                )
            )
        if key == "fee_form":
            try:
                edited_values = edited_values_from_json(
                    edited_values_json_from_confirmed_fee_snapshot(
                        str(getattr(confirmed_fee, "pricing_snapshot_json"))
                    )
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
            feedback = (self._customer_feedback_factory(output_dir)
                        if stage_dir is not None and self._customer_feedback_factory is not None
                        else self._customer_feedback_service)
            result = feedback.generate(
                CustomerFeedbackFormGenerationCommand(
                    project_id=project_id,
                    output_dir=output_dir if stage_dir is not None else None,
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

