from pathlib import Path

import pytest

from backend.application.tools_customer_report_job_service import (
    ToolsCustomerReportJobService,
)


class _Generator:
    def __init__(self) -> None:
        self.calls: list[tuple[Path, Path, Path]] = []

    def generate_customer_report(
        self,
        *,
        source_path: Path,
        template_path: Path,
        output_path: Path,
        progress,
    ) -> Path:
        self.calls.append((source_path, template_path, output_path))
        progress("copying_content")
        progress("formatting_document")
        output_path.write_bytes(b"customer")
        return output_path


def test_customer_report_job_reports_progress_and_completes(tmp_path: Path) -> None:
    source = tmp_path / "source.docx"
    template = tmp_path / "template.docx"
    output = tmp_path / "customer.docx"
    source.write_bytes(b"source")
    template.write_bytes(b"template")
    queued = []
    clock_value = [10.0]
    generator = _Generator()
    jobs = ToolsCustomerReportJobService(
        generator=generator,
        dispatch=queued.append,
        clock=lambda: clock_value[0],
    )

    started = jobs.start(
        root=tmp_path,
        source_path=source,
        template_path=template,
        output_path=output,
    )

    assert started["status"] == "queued"
    assert started["stage"] == "queued"
    assert len(queued) == 1

    clock_value[0] = 13.25
    queued.pop()()
    completed = jobs.read(started["operation_id"])

    assert completed["status"] == "completed"
    assert completed["stage"] == "completed"
    assert completed["elapsed_seconds"] == 3.25
    assert jobs.output_path(started["operation_id"]) == output


def test_customer_report_job_keeps_actionable_failure_after_cleaning_temp_files(
    tmp_path: Path,
) -> None:
    class _FailingGenerator:
        def generate_customer_report(self, **_kwargs):
            raise ValueError("Word could not copy the report body.")

    root = tmp_path / "operation"
    root.mkdir()
    source = root / "source.docx"
    template = tmp_path / "template.docx"
    source.write_bytes(b"source")
    template.write_bytes(b"template")
    queued = []
    jobs = ToolsCustomerReportJobService(
        generator=_FailingGenerator(),
        dispatch=queued.append,
    )

    started = jobs.start(
        root=root,
        source_path=source,
        template_path=template,
        output_path=root / "customer.docx",
    )
    queued.pop()()
    failed = jobs.read(started["operation_id"])

    assert failed["status"] == "failed"
    assert failed["stage"] == "failed"
    assert failed["message"] == "Word could not copy the report body."
    assert not root.exists()


def test_customer_report_job_removes_an_undownloaded_result_after_retention(
    tmp_path: Path,
) -> None:
    root = tmp_path / "operation"
    root.mkdir()
    source = root / "source.docx"
    template = tmp_path / "template.docx"
    output = root / "customer.docx"
    source.write_bytes(b"source")
    template.write_bytes(b"template")
    queued = []
    clock_value = [10.0]
    jobs = ToolsCustomerReportJobService(
        generator=_Generator(),
        dispatch=queued.append,
        clock=lambda: clock_value[0],
        retention_seconds=60,
    )
    started = jobs.start(
        root=root,
        source_path=source,
        template_path=template,
        output_path=output,
    )
    clock_value[0] = 12.0
    queued.pop()()

    clock_value[0] = 72.0
    with pytest.raises(LookupError, match="not found"):
        jobs.read(started["operation_id"])

    assert not root.exists()
