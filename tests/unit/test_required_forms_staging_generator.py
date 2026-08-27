from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from backend.api.dependencies import _RequiredFormsStagingGenerator
from backend.application.customer_feedback_form_generation_service import (
    CustomerFeedbackFormGenerationCommand,
    CustomerFeedbackFormGenerationResult,
)
from backend.application.fee_evaluation_edited_export_values import (
    FeeEvaluationEditedExportRow,
    FeeEvaluationEditedExportSummary,
    FeeEvaluationEditedExportValues,
)
from backend.application.fee_evaluation_pricing_draft_persistence_service import (
    FeeEvaluationPricingDraftSnapshot,
    edited_values_to_json,
)
from backend.application.confirmed_fee_pricing_snapshot import (
    encode_confirmed_fee_pricing_snapshot,
)
from backend.application.project_basic_information_output import (
    ConfirmedBasicInformationSnapshot,
)
from backend.domain import (
    ExternalResource,
    ExternalResourceType,
    ExternalResourceValidationStatus,
)


def test_staging_generator_passes_raw_basic_information_to_customer_feedback(
    tmp_path: Path,
) -> None:
    feedback_service = _CustomerFeedbackService(tmp_path)
    generator = _RequiredFormsStagingGenerator(
        settings=SimpleNamespace(
            data_dir=tmp_path / "data",
            templates_dir=tmp_path / "templates",
        ),
        fee_template_resource_store=_TemplateFolderStore(tmp_path / "templates"),
        test_record_service=SimpleNamespace(),
        fee_export_service=SimpleNamespace(),
        customer_feedback_service=feedback_service,
    )

    output_path = generator.generate(
        project_id="P1",
        key="customer_feedback_form",
        target_name="DL-001 Customer Feedback Form_Even Yang.xlsx",
        basic_information=_basic_information(),
        confirmed_fee=SimpleNamespace(pricing_snapshot_json="{}"),
    )

    assert output_path.name == "DL-001 Customer Feedback Form_Even Yang.xlsx"
    assert feedback_service.command is not None
    values = feedback_service.command.basic_information_values
    assert values is not None
    assert values["dl_number"] == "DL-001"
    assert values["product_description"] == "Connector from Basic Info"
    assert values["requested_by"] == "Requester BI"
    assert values["location"] == "Dongguan"
    assert values["lab_performing_tests"] == "Dongguan Lab"
    assert "ltr_number" not in values
    assert "product_name" not in values
    assert "requestor" not in values
    assert "lab" not in values


def test_required_forms_fee_form_uses_confirmed_fee_pricing_snapshot_notes(
    tmp_path: Path,
) -> None:
    runtime_templates_dir = tmp_path / "runtime-templates"
    settings_template_folder = tmp_path / "settings-template-folder"
    runtime_templates_dir.mkdir()
    settings_template_folder.mkdir()
    template = settings_template_folder / "FDQF-E-176 Fee Form.xls"
    template.write_bytes(b"template")
    fee_export = _FeeExportService()
    generator = _RequiredFormsStagingGenerator(
        settings=SimpleNamespace(
            data_dir=tmp_path / "data",
            templates_dir=runtime_templates_dir,
        ),
        fee_template_resource_store=_TemplateFolderStore(settings_template_folder),
        test_record_service=SimpleNamespace(),
        fee_export_service=fee_export,
        customer_feedback_service=SimpleNamespace(),
    )

    output = generator.generate(
        project_id="P1",
        key="fee_form",
        target_name="DL-001 Fee Form.xls",
        basic_information=ConfirmedBasicInformationSnapshot(
            project_id="P1",
            version=1,
            values={
                "dl_number": "DL-001",
                "product_description": "Connector",
                "test_item": "Qualification Test",
                "requested_by": "MP Cao",
                "location": "Dongguan",
            },
            source_signature="{}",
            confirmed_at=None,
            confirmed_by=None,
        ),
        confirmed_fee=SimpleNamespace(
            pricing_snapshot_json=_confirmed_v2_pricing_snapshot_json(
                _edited_values_with_notes()
            )
        ),
    )

    assert output.name == "DL-001 Fee Form.xls"
    assert fee_export.command is not None
    assert fee_export.command.edited_values is not None
    assert fee_export.command.edited_values.rows[0].notes == "阿第三方"
    assert fee_export.command.fill_mode == "matrix_basic"
    assert fee_export.command.template_path == template


def _confirmed_v2_pricing_snapshot_json(
    values: FeeEvaluationEditedExportValues,
) -> str:
    return encode_confirmed_fee_pricing_snapshot(
        snapshot=FeeEvaluationPricingDraftSnapshot(
            draft_edit_id="fed-1",
            project_id="P1",
            confirmed_matrix_id="cmv-1",
            confirmed_revision=1,
            fee_rule_version_id="fee_rules_v2026_06_03",
            edited_values=values,
            created_at="2026-07-15T00:00:00+00:00",
            updated_at="2026-07-15T00:00:00+00:00",
            generation=1,
            payload_fingerprint="payload-fingerprint-1",
            source_context_fingerprint="source-fingerprint-1",
            validation_token="validation-token-1",
        ),
        edited_values=values,
    )


def test_required_forms_test_record_uses_settings_template_folder(
    tmp_path: Path,
) -> None:
    settings_template_folder = tmp_path / "settings-template-folder"
    settings_template_folder.mkdir()
    template = settings_template_folder / "FDQF-E-036 Test Record Template-Even.docx"
    template.write_bytes(b"template")
    test_record_service = _TestRecordService()
    generator = _RequiredFormsStagingGenerator(
        settings=SimpleNamespace(
            data_dir=tmp_path / "data",
            templates_dir=tmp_path / "runtime-templates",
            test_record=SimpleNamespace(template_path=None),
        ),
        fee_template_resource_store=_TemplateFolderStore(settings_template_folder),
        test_record_service=test_record_service,
        fee_export_service=SimpleNamespace(),
        customer_feedback_service=SimpleNamespace(),
    )

    output = generator.generate(
        project_id="P1",
        key="test_record",
        target_name="DL-001 Test Record.docx",
        basic_information=_basic_information(),
        confirmed_fee=SimpleNamespace(pricing_snapshot_json="{}"),
    )

    assert output.name == "DL-001 Test Record.docx"
    assert test_record_service.command is not None
    assert test_record_service.command.template_path == template


def test_required_forms_test_status_uses_confirmed_matrix_generator(tmp_path: Path) -> None:
    test_status_service = _TestStatusService()
    generator = _RequiredFormsStagingGenerator(
        settings=SimpleNamespace(
            data_dir=tmp_path / "data",
            templates_dir=tmp_path / "templates",
        ),
        fee_template_resource_store=_TemplateFolderStore(tmp_path / "templates"),
        test_record_service=SimpleNamespace(),
        fee_export_service=SimpleNamespace(),
        customer_feedback_service=SimpleNamespace(),
        test_status_service=test_status_service,
    )

    output = generator.generate(
        project_id="P1",
        key="test_status",
        target_name="DL-001 test status.xlsx",
        basic_information=_basic_information(),
        confirmed_fee=SimpleNamespace(pricing_snapshot_json="{}"),
    )

    assert output.name == "DL-001 test status.xlsx"
    assert test_status_service.command is not None
    assert test_status_service.command.project_id == "P1"


class _TestStatusService:
    def __init__(self) -> None:
        self.command = None

    def generate(self, command):
        self.command = command
        output = command.output_dir / command.target_name
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(b"test status")
        return output


class _FeeExportService:
    def __init__(self) -> None:
        self.command = None

    def export(self, command):
        self.command = command
        output = command.output_dir / command.output_file_name
        output.write_bytes(b"fee")
        return SimpleNamespace(output_path=output)


class _TestRecordService:
    def __init__(self) -> None:
        self.command = None

    def generate(self, command):
        self.command = command
        output = command.output_dir / "generated-test-record.docx"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(b"test record")
        return SimpleNamespace(output_path=output)


class _CustomerFeedbackService:
    def __init__(self, tmp_path: Path) -> None:
        self.output_path = tmp_path / "generated" / "customer-feedback.xlsx"
        self.command: CustomerFeedbackFormGenerationCommand | None = None

    def generate(
        self,
        command: CustomerFeedbackFormGenerationCommand,
    ) -> CustomerFeedbackFormGenerationResult:
        self.command = command
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.output_path.write_bytes(b"generated")
        return CustomerFeedbackFormGenerationResult(
            project_id=command.project_id,
            template_path=Path("template.xlsx"),
            output_path=self.output_path,
            output_file_name=self.output_path.name,
        )


class _TemplateFolderStore:
    def __init__(self, template_folder: Path) -> None:
        self.template_folder = template_folder

    def get_by_type(
        self,
        resource_type: ExternalResourceType,
    ) -> ExternalResource | None:
        if resource_type is not ExternalResourceType.PROJECT_FOLDER_TEMPLATE:
            return None
        return ExternalResource(
            resource_id="template-folder",
            resource_type=ExternalResourceType.PROJECT_FOLDER_TEMPLATE,
            path=self.template_folder,
            active=True,
            validation_status=ExternalResourceValidationStatus.VALID,
        )


def _basic_information() -> ConfirmedBasicInformationSnapshot:
    return ConfirmedBasicInformationSnapshot(
        project_id="P1",
        version=2,
        values={
            "dl_number": "DL-001",
            "product_description": "Connector from Basic Info",
            "test_item": "Qualification Test",
            "requested_by": "Requester BI",
            "location": "Dongguan",
            "lab_performing_tests": "Dongguan Lab",
            "phone": "123456",
            "requestor_email": "requester@example.test",
            "project_leader": "Even Yang",
            "date_lab_received_samples": "20 Jun 2026",
            "estimated_completion_date": "25 Jun 2026",
        },
        source_signature='{"dl_number":"DL-001"}',
        confirmed_at="2026-06-20T00:00:00+00:00",
        confirmed_by="Lab User",
    )


def _edited_values_with_notes() -> FeeEvaluationEditedExportValues:
    return FeeEvaluationEditedExportValues(
        rows=(
            FeeEvaluationEditedExportRow(
                source_line_id="line-1",
                confirmed_group_id="group-1",
                confirmed_row_id="row-1",
                step_token="2",
                step_index=2,
                spend_time="0",
                unit_price="0",
                unit_type="per reading",
                units="1",
                base_fee="0",
                discount="0%",
                testing_fee="0",
                notes="阿第三方",
            ),
        ),
        summary=FeeEvaluationEditedExportSummary(
            condition_confirmation_spend_time="0",
            external_cost="0",
            external_cost_note="",
            lab_manpower_hourly_rate="200",
        ),
    )
