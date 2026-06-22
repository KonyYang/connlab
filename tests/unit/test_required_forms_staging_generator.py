from __future__ import annotations

from pathlib import Path

from backend.api.dependencies import _RequiredFormsStagingGenerator
from backend.application.customer_feedback_form_generation_service import (
    CustomerFeedbackFormGenerationCommand,
    CustomerFeedbackFormGenerationResult,
)
from backend.application.project_basic_information_output import (
    ConfirmedBasicInformationSnapshot,
)
from backend.shared.config import Settings


def test_staging_generator_passes_raw_basic_information_to_customer_feedback(
    tmp_path: Path,
) -> None:
    feedback_service = _CustomerFeedbackService(tmp_path)
    generator = _RequiredFormsStagingGenerator(
        settings=Settings(
            data_dir=tmp_path / "data",
            projects_dir=tmp_path / "projects",
            templates_dir=tmp_path / "templates",
            database_path=tmp_path / "connlab.sqlite3",
        ),
        test_record_service=object(),
        fee_export_service=object(),
        customer_feedback_service=feedback_service,
    )

    output_path = generator.generate(
        project_id="P1",
        key="customer_feedback_form",
        target_name="DL-001 Customer Feedback Form_Even Yang.xlsx",
        basic_information=_basic_information(),
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
