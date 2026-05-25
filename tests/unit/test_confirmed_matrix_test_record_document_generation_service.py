from __future__ import annotations

from pathlib import Path

import pytest

from backend.application.confirmed_matrix_test_record_document_generation_service import (
    ConfirmedMatrixTestRecordDocumentGenerationError,
    ConfirmedMatrixTestRecordDocumentGenerationNotFoundError,
    ConfirmedMatrixTestRecordDocumentGenerationService,
    GenerateConfirmedMatrixTestRecordDocumentCommand,
)
from backend.application.confirmed_matrix_test_record_preview_service import (
    ConfirmedMatrixTestRecordPreview,
    ConfirmedMatrixTestRecordPreviewGroup,
    ConfirmedMatrixTestRecordPreviewNotFoundError,
    ConfirmedMatrixTestRecordPreviewStep,
)


def test_generation_service_writes_preview_groups_to_controlled_output(tmp_path: Path) -> None:
    writer = _Writer()
    service = ConfirmedMatrixTestRecordDocumentGenerationService(
        preview_service=_PreviewService(_preview()),
        project_store=_ProjectStore(),
        writer=writer,
    )

    result = service.generate(
        GenerateConfirmedMatrixTestRecordDocumentCommand(
            project_id="P1",
            output_dir=tmp_path,
        )
    )

    assert result.project_id == "P1"
    assert result.confirmed_matrix_id == "cmv-1"
    assert result.output_path.name == "P1_test_record_draft.docx"
    assert writer.calls[0]["product_description"] == "Connector"
    assert writer.calls[0]["groups"][0].group_label == "Group 1"
    assert writer.calls[0]["groups"][0].sample_quantity_expression == "5"
    assert writer.calls[0]["groups"][0].steps[0].raw_token == "1"


def test_generation_service_uses_active_confirmed_preview_only(tmp_path: Path) -> None:
    service = ConfirmedMatrixTestRecordDocumentGenerationService(
        preview_service=_PreviewService(None),
        project_store=_ProjectStore(),
        writer=_Writer(),
    )

    with pytest.raises(ConfirmedMatrixTestRecordDocumentGenerationNotFoundError):
        service.generate(
            GenerateConfirmedMatrixTestRecordDocumentCommand(
                project_id="P1",
                output_dir=tmp_path,
            )
        )


def test_generation_service_rejects_empty_preview(tmp_path: Path) -> None:
    empty = ConfirmedMatrixTestRecordPreview(
        project_id="P1",
        confirmed_matrix_id="cmv-empty",
        preview_status="empty",
        groups=(),
    )
    service = ConfirmedMatrixTestRecordDocumentGenerationService(
        preview_service=_PreviewService(empty),
        project_store=_ProjectStore(),
        writer=_Writer(),
    )

    with pytest.raises(ConfirmedMatrixTestRecordDocumentGenerationError, match="no previewable"):
        service.generate(
            GenerateConfirmedMatrixTestRecordDocumentCommand(
                project_id="P1",
                output_dir=tmp_path,
            )
        )


class _PreviewService:
    def __init__(self, preview: ConfirmedMatrixTestRecordPreview | None) -> None:
        self.preview = preview

    def build_preview(self, command):
        if self.preview is None:
            raise ConfirmedMatrixTestRecordPreviewNotFoundError("Active confirmed matrix not found.")
        return self.preview


class _Project:
    project_id = "P1"
    product_name = "Connector"
    project_no = "DL-001"


class _ProjectStore:
    def get(self, project_id: str):
        return _Project() if project_id == "P1" else None


class _Writer:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def generate_from_confirmed_matrix(self, **kwargs):
        self.calls.append(kwargs)
        kwargs["output_path"].write_bytes(b"docx")
        return kwargs["output_path"]


def _preview() -> ConfirmedMatrixTestRecordPreview:
    return ConfirmedMatrixTestRecordPreview(
        project_id="P1",
        confirmed_matrix_id="cmv-1",
        preview_status="ready",
        groups=(
            ConfirmedMatrixTestRecordPreviewGroup(
                group_key="g1",
                group_label="Group 1",
                sample_quantity_expression="5",
                step_count=1,
                steps=(
                    ConfirmedMatrixTestRecordPreviewStep(
                        sequence=1,
                        raw_token="1",
                        test_item="Visual",
                        section="6.1",
                        method="EIA-364-18",
                        condition="10x",
                        requirement="No damage",
                    ),
                ),
            ),
        ),
    )
