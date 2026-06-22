from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

from backend.application.customer_feedback_form_generation_service import (
    CustomerFeedbackFormGenerationCommand,
    CustomerFeedbackFormGenerationService,
    CustomerFeedbackReadinessError,
    CustomerFeedbackTemplateAmbiguousError,
)
from backend.domain import ExternalResource, ExternalResourceType, Project, ProjectStatus


def test_customer_feedback_generation_uses_unique_e4243_template(tmp_path: Path) -> None:
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    template = template_dir / "E-4243_D Customer Feedback Form.xlsx"
    template.write_bytes(b"template")
    gateway = FakeCustomerFeedbackGateway()
    service = _service(tmp_path, template_dir=template_dir, gateway=gateway)

    result = service.generate(CustomerFeedbackFormGenerationCommand(project_id="P1"))

    assert result.template_path == template
    assert result.output_path != template
    assert result.output_path.name == "DL-2026-05-003_customer_feedback_E-4243.xlsx"
    assert result.output_path.parent == tmp_path / "data" / "generated_customer_feedback" / "P1"
    assert result.warnings == ("filled LTR Number", "filled Requestor")
    assert gateway.calls == [
        CustomerFeedbackGatewayCall(
            template_path=template,
            output_path=result.output_path,
            identity={"ltr_number": "DL-2026-05-003", "requestor": "MP Cao", "product_name": "Coolpower"},
        )
    ]


def test_customer_feedback_generation_uses_basic_information_identity(
    tmp_path: Path,
) -> None:
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    template = template_dir / "E-4243_D Customer Feedback Form.xlsx"
    template.write_bytes(b"template")
    gateway = FakeCustomerFeedbackGateway()
    service = _service(tmp_path, template_dir=template_dir, gateway=gateway)

    service.generate(
        CustomerFeedbackFormGenerationCommand(
            project_id="P1",
            basic_information_values={
                "dl_number": "DL-BI",
                "product_description": "Connector from Basic Information",
                "test_item": "Qualification test",
                "requested_by": "Requester BI",
                "phone": "12345",
                "requestor_email": "requester@example.test",
                "location": "Dongguan",
                "project_leader": "Even Yang",
                "lab_performing_tests": "Dongguan",
                "date_lab_received_samples": "20 Jun 2026",
                "estimated_completion_date": "02 Jul 2026",
            },
        )
    )

    assert gateway.calls == [
        CustomerFeedbackGatewayCall(
            template_path=template,
            output_path=(
                tmp_path
                / "data"
                / "generated_customer_feedback"
                / "P1"
                / "DL-2026-05-003_customer_feedback_E-4243.xlsx"
            ),
            identity={
                "ltr_number": "DL-BI",
                "product_name": "Connector from Basic Information",
                "test_item": "Qualification test",
                "requestor": "Requester BI",
                "phone": "12345",
                "email": "requester@example.test",
                "location": "Dongguan",
                "project_leader": "Even Yang",
                "lab": "Dongguan",
                "received_date": "20 Jun 2026",
                "estimated_completion_date": "02 Jul 2026",
            },
        )
    ]


def test_customer_feedback_generation_rejects_missing_template_folder_resource(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path, template_dir=None)

    with pytest.raises(CustomerFeedbackReadinessError, match="Template folder is not configured"):
        service.generate(CustomerFeedbackFormGenerationCommand(project_id="P1"))


def test_customer_feedback_generation_avoids_overwriting_existing_output(
    tmp_path: Path,
) -> None:
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    (template_dir / "E-4243_D Customer Feedback Form.xlsx").write_bytes(b"template")
    output_dir = tmp_path / "data" / "generated_customer_feedback" / "P1"
    output_dir.mkdir(parents=True)
    (output_dir / "DL-2026-05-003_customer_feedback_E-4243.xlsx").write_bytes(b"old")
    service = _service(tmp_path, template_dir=template_dir)

    result = service.generate(CustomerFeedbackFormGenerationCommand(project_id="P1"))

    assert result.output_file_name == "DL-2026-05-003_customer_feedback_E-4243_2.xlsx"
    assert (output_dir / "DL-2026-05-003_customer_feedback_E-4243.xlsx").read_bytes() == b"old"


def test_customer_feedback_generation_rejects_output_dir_outside_generated_root(
    tmp_path: Path,
) -> None:
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    (template_dir / "E-4243_D Customer Feedback Form.xlsx").write_bytes(b"template")
    service = _service(tmp_path, template_dir=template_dir)

    with pytest.raises(CustomerFeedbackReadinessError, match="controlled generated output"):
        service.generate(
            CustomerFeedbackFormGenerationCommand(
                project_id="P1",
                output_dir=tmp_path / "public-drive",
            )
        )


def test_customer_feedback_generation_rejects_missing_e4243_template(tmp_path: Path) -> None:
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    (template_dir / "Other.xlsx").write_bytes(b"template")
    service = _service(tmp_path, template_dir=template_dir)

    with pytest.raises(CustomerFeedbackReadinessError, match="E-4243"):
        service.generate(CustomerFeedbackFormGenerationCommand(project_id="P1"))


def test_customer_feedback_generation_rejects_ambiguous_e4243_templates(
    tmp_path: Path,
) -> None:
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    (template_dir / "E-4243_D Customer Feedback Form.xlsx").write_bytes(b"one")
    (template_dir / "copy E-4243 customer feedback.xlsx").write_bytes(b"two")
    service = _service(tmp_path, template_dir=template_dir)

    with pytest.raises(CustomerFeedbackTemplateAmbiguousError, match="Multiple"):
        service.generate(CustomerFeedbackFormGenerationCommand(project_id="P1"))


def test_customer_feedback_generation_rejects_missing_project(tmp_path: Path) -> None:
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    (template_dir / "E-4243_D Customer Feedback Form.xlsx").write_bytes(b"template")
    service = _service(tmp_path, template_dir=template_dir, project=None)

    with pytest.raises(CustomerFeedbackReadinessError, match="Project was not found"):
        service.generate(CustomerFeedbackFormGenerationCommand(project_id="P1"))


@dataclass(frozen=True, slots=True)
class CustomerFeedbackGatewayCall:
    template_path: Path
    output_path: Path
    identity: dict[str, str]


class FakeCustomerFeedbackGateway:
    def __init__(self) -> None:
        self.calls: list[CustomerFeedbackGatewayCall] = []

    def generate(
        self,
        *,
        template_path: Path,
        output_path: Path,
        identity: dict[str, str],
    ) -> tuple[Path, tuple[str, ...]]:
        self.calls.append(
            CustomerFeedbackGatewayCall(
                template_path=template_path,
                output_path=output_path,
                identity=identity,
            )
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(b"generated")
        return output_path, ("filled LTR Number", "filled Requestor")


class FakeProjectStore:
    def __init__(self, project: Project | None) -> None:
        self._project = project

    def get(self, project_id: str) -> Project | None:
        return self._project if self._project and self._project.project_id == project_id else None


class FakeExternalResourceStore:
    def __init__(self, template_dir: Path | None) -> None:
        self._template_dir = template_dir

    def get_by_type(self, resource_type: ExternalResourceType) -> ExternalResource | None:
        if self._template_dir is None:
            return None
        return ExternalResource(
            resource_id="R1",
            resource_type=resource_type,
            path=self._template_dir,
        )


def _service(
    tmp_path: Path,
    *,
    template_dir: Path | None,
    project: Project | None = Project(
        project_id="P1",
        project_no="DL-2026-05-003",
        product_name="Coolpower",
        requestor="MP Cao",
        status=ProjectStatus.LTR_REGISTERED,
    ),
    gateway: FakeCustomerFeedbackGateway | None = None,
) -> CustomerFeedbackFormGenerationService:
    return CustomerFeedbackFormGenerationService(
        project_store=FakeProjectStore(project),
        external_resource_store=FakeExternalResourceStore(template_dir),
        workbook_gateway=gateway or FakeCustomerFeedbackGateway(),
        generated_root=tmp_path / "data" / "generated_customer_feedback",
    )
