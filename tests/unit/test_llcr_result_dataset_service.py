from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from pathlib import Path

import pytest

from backend.application.llcr_result_dataset_service import (
    ConfirmLlcrImportCommand,
    InspectLlcrImportCommand,
    LlcrImportConflictError,
    LlcrImportPreviewRegistry,
    LlcrResultDatasetService,
)
from backend.domain.result_dataset_models import (
    LlcrConfirmationDecision,
    LlcrMeasurement,
    LlcrResultEntry,
)
from backend.infrastructure.office.llcr_result_workbook_gateway import (
    LocalLlcrImportSourceStore,
    LlcrWorkbookInspection,
)


def test_inspect_is_non_authoritative_and_confirm_creates_immutable_revision(tmp_path) -> None:
    repository = _Repository()
    service = _service(tmp_path, repository)

    preview = service.inspect(
        InspectLlcrImportCommand("P1", "LLCR Record.xlsx", b"source-bytes", "Even Yang")
    )

    assert preview.can_confirm is True
    assert repository.datasets == []
    dataset = service.confirm(
        ConfirmLlcrImportCommand(
            project_id="P1",
            preview_id=preview.preview_id,
            confirmed_by="Even Yang",
            decisions=(LlcrConfirmationDecision("result-1", "pass"),),
        )
    )
    assert dataset.revision == 1
    assert dataset.source.sha256 == preview.source.sha256
    assert dataset.payload.entries[0].confirmed_outcome == "pass"
    assert repository.datasets == [dataset]

    second = service.inspect(
        InspectLlcrImportCommand("P1", "LLCR Record.xlsx", b"source-bytes", "Even Yang")
    )
    second_dataset = service.confirm(
        ConfirmLlcrImportCommand(
            "P1",
            second.preview_id,
            "Even Yang",
            (LlcrConfirmationDecision("result-1", "pass"),),
        )
    )
    assert second_dataset.revision == 2
    assert repository.datasets[0].dataset_id != repository.datasets[1].dataset_id


def test_confirm_rejects_changed_staged_file_and_manual_override_without_reason(tmp_path) -> None:
    repository = _Repository()
    source_store = LocalLlcrImportSourceStore(tmp_path / "staged")
    registry = LlcrImportPreviewRegistry()
    service = _service(tmp_path, repository, source_store=source_store, registry=registry)
    preview = service.inspect(
        InspectLlcrImportCommand("P1", "LLCR.xlsx", b"source-bytes", "Even Yang")
    )
    pending = registry.get(preview.preview_id)
    Path(pending.source_path).write_bytes(b"changed-after-preview")

    with pytest.raises(LlcrImportConflictError, match="changed after preview"):
        service.confirm(
            ConfirmLlcrImportCommand(
                "P1",
                preview.preview_id,
                "Even Yang",
                (LlcrConfirmationDecision("result-1", "pass"),),
            )
        )


def test_confirm_rejects_changed_llcr_projection_fingerprint(tmp_path) -> None:
    repository = _Repository()
    preview_service = _PreviewService()
    service = _service(tmp_path, repository, preview_service=preview_service)
    preview = service.inspect(
        InspectLlcrImportCommand("P1", "LLCR.xlsx", b"source-bytes", "Even Yang")
    )
    preview_service.fingerprint = "projection-hash-2"

    with pytest.raises(LlcrImportConflictError, match="mapping authority changed"):
        service.confirm(
            ConfirmLlcrImportCommand(
                "P1",
                preview.preview_id,
                "Even Yang",
                (LlcrConfirmationDecision("result-1", "pass"),),
            )
        )

    assert repository.datasets == []


def test_cancel_discards_non_authoritative_preview_and_staged_source(tmp_path) -> None:
    repository = _Repository()
    source_store = LocalLlcrImportSourceStore(tmp_path / "staged")
    registry = LlcrImportPreviewRegistry()
    service = _service(tmp_path, repository, source_store=source_store, registry=registry)
    preview = service.inspect(
        InspectLlcrImportCommand("P1", "LLCR.xlsx", b"source-bytes", "Even Yang")
    )
    staged = Path(registry.get(preview.preview_id).source_path)

    service.cancel(project_id="P1", preview_id=preview.preview_id)

    assert not staged.parent.exists()
    with pytest.raises(LlcrImportConflictError, match="expired or was not found"):
        registry.get(preview.preview_id)
    assert repository.datasets == []


def test_confirm_commit_failure_keeps_preview_retryable_and_creates_no_revision(tmp_path) -> None:
    repository = _Repository()
    repository.fail_commit = True
    source_store = LocalLlcrImportSourceStore(tmp_path / "staged")
    registry = LlcrImportPreviewRegistry()
    service = _service(tmp_path, repository, source_store=source_store, registry=registry)
    preview = service.inspect(
        InspectLlcrImportCommand("P1", "LLCR.xlsx", b"source-bytes", "Even Yang")
    )

    with pytest.raises(RuntimeError, match="commit failed"):
        service.confirm(
            ConfirmLlcrImportCommand(
                "P1",
                preview.preview_id,
                "Even Yang",
                (LlcrConfirmationDecision("result-1", "pass"),),
            )
        )

    assert repository.datasets == []
    assert Path(registry.get(preview.preview_id).source_path).is_file()

    clean = service.inspect(
        InspectLlcrImportCommand("P1", "LLCR.xlsx", b"source-bytes", "Even Yang")
    )
    with pytest.raises(ValueError, match="override requires a reason"):
        service.confirm(
            ConfirmLlcrImportCommand(
                "P1",
                clean.preview_id,
                "Even Yang",
                (LlcrConfirmationDecision("result-1", "fail"),),
            )
        )


def test_confirm_remains_successful_when_post_commit_staging_cleanup_fails(tmp_path) -> None:
    repository = _Repository()
    source_store = _CleanupFailingSourceStore(tmp_path / "staged")
    registry = LlcrImportPreviewRegistry()
    service = _service(
        tmp_path,
        repository,
        source_store=source_store,
        registry=registry,
    )
    preview = service.inspect(
        InspectLlcrImportCommand("P1", "LLCR.xlsx", b"source-bytes", "Even Yang")
    )

    dataset = service.confirm(
        ConfirmLlcrImportCommand(
            "P1",
            preview.preview_id,
            "Even Yang",
            (LlcrConfirmationDecision("result-1", "pass"),),
        )
    )

    assert dataset.revision == 1
    assert repository.datasets == [dataset]
    with pytest.raises(LlcrImportConflictError, match="expired or was not found"):
        registry.get(preview.preview_id)


def _service(
    tmp_path,
    repository,
    *,
    source_store=None,
    registry=None,
    preview_service=None,
):
    return LlcrResultDatasetService(
        preview_service=preview_service or _PreviewService(),
        workbook_gateway=_WorkbookGateway(),
        source_store=source_store or LocalLlcrImportSourceStore(tmp_path / "staged"),
        preview_registry=registry or LlcrImportPreviewRegistry(),
        repository=repository,
        clock=lambda: "2026-08-29T08:00:00Z",
        id_factory=iter(("preview-1", "dataset-1", "preview-2", "dataset-2", "preview-3")).__next__,
    )


class _PreviewService:
    def __init__(self):
        self.fingerprint = "projection-hash-1"

    def preview(self, project_id: str, record_type: str):
        return _Projection(project_id, self.fingerprint)


class _Projection:
    def __init__(self, project_id: str, fingerprint: str):
        self.project_id = project_id
        self.confirmed_matrix_id = "matrix-1"
        self.confirmed_revision = 3
        self.preview_fingerprint = fingerprint


class _WorkbookGateway:
    def inspect(self, *, source_path, projection):
        measurement = LlcrMeasurement(
            1, "SIG1", Decimal("0.198"), "mΩ", "SIG", "K10",
            Decimal("0.248"), "mΩ", "D10",
        )
        return LlcrWorkbookInspection(
            parser_profile_version="connlab-llcr-macro-v1",
            detected_sheets=("Summary", "SIG"),
            entries=(
                LlcrResultEntry(
                    result_id="result-1",
                    confirmed_group_id="group-1",
                    group_label="1",
                    confirmed_row_id="row-1",
                    matrix_step_sequence=2,
                    matrix_step_token="2",
                    stage="initial",
                    stage_label="Initial LLCR",
                    requirement="≤0.25mΩ",
                    requirement_comparator="<=",
                    requirement_limit=Decimal("0.25"),
                    requirement_unit="mΩ",
                    measurements=(measurement,),
                    summary_min=Decimal("0.198"),
                    summary_max=Decimal("0.198"),
                    summary_average=Decimal("0.198"),
                    provisional_outcome="pass",
                    source_range="SIG!K10:K10",
                ),
            ),
            diagnostics=(),
        )


class _Repository:
    def __init__(self):
        self.datasets = []
        self.fail_commit = False

    def next_dataset_revision(self, project_id, dataset_type):
        return len(self.datasets) + 1

    def create_dataset(self, dataset):
        self.datasets.append(dataset)
        return dataset

    def commit(self):
        if self.fail_commit:
            raise RuntimeError("commit failed")

    def rollback(self):
        self.datasets.clear()


class _CleanupFailingSourceStore(LocalLlcrImportSourceStore):
    def remove(self, preview_id):
        raise OSError("staged workbook is temporarily locked")
