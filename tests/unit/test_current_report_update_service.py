from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

import pytest

from backend.application.current_report_update_service import (
    CurrentReportUpdateError,
    CurrentReportUpdateService,
    UpdateCurrentLlcrReportCommand,
)
from backend.domain.result_dataset_models import ReportDraftRevision
from backend.infrastructure.files.report_publication_gateway import (
    ReportPublicationGateway,
)
from tests.unit.test_result_dataset_repository import _dataset


def test_preview_prefers_the_single_official_internal_report(tmp_path: Path) -> None:
    official = tmp_path / "DL-001" / "DL-001 Product Qualification test"
    official.mkdir(parents=True)
    report = official / "DL-001 Product Qualification Testing Report_Rev_A.docx"
    report.write_bytes(b"reviewed-report")
    service = _service(
        tmp_path,
        workspace=_workspace(tmp_path, official),
        reports=(),
    )

    preview = service.preview_llcr_update(project_id="P1", dataset_id="dataset-1")

    assert preview.status == "ready"
    assert preview.current_report.mode == "official"
    assert preview.current_report.file_name == report.name
    assert preview.current_report.file_sha256
    assert preview.blockers == ()


def test_preview_blocks_when_the_official_folder_has_multiple_internal_reports(
    tmp_path: Path,
) -> None:
    official = tmp_path / "official"
    official.mkdir()
    for suffix in ("A", "B"):
        (official / f"DL-001 Product Qualification Testing Report_Rev_{suffix}.docx").write_bytes(
            suffix.encode()
        )
    service = _service(
        tmp_path,
        workspace=_workspace(tmp_path, official),
        reports=(),
    )

    preview = service.preview_llcr_update(project_id="P1", dataset_id="dataset-1")

    assert preview.status == "blocked"
    assert preview.current_report.status == "ambiguous"
    assert "Multiple current internal reports" in preview.blockers[0]


def test_preview_uses_latest_managed_draft_when_no_official_report_exists(
    tmp_path: Path,
) -> None:
    draft = tmp_path / "generated" / "report-r1.docx"
    draft.parent.mkdir()
    draft.write_bytes(b"draft")
    service = _service(
        tmp_path,
        workspace=None,
        reports=(_report_revision(draft),),
    )

    preview = service.preview_llcr_update(project_id="P1", dataset_id="dataset-1")

    assert preview.status == "ready"
    assert preview.current_report.mode == "managed_draft"
    assert preview.current_report.file_name == draft.name
    assert preview.warnings == (
        "No official project report is available; the controlled draft will be updated.",
    )


def test_preview_blocks_a_managed_draft_from_a_different_confirmed_matrix(
    tmp_path: Path,
) -> None:
    draft = tmp_path / "generated" / "report-r1.docx"
    draft.parent.mkdir()
    draft.write_bytes(b"draft")
    stale_report = replace(
        _report_revision(draft),
        confirmed_matrix_id="matrix-old",
    )
    service = _service(
        tmp_path,
        workspace=None,
        reports=(stale_report,),
    )

    preview = service.preview_llcr_update(project_id="P1", dataset_id="dataset-1")

    assert preview.status == "blocked"
    assert "different Confirmed Matrix" in preview.blockers[0]


def test_llcr_update_archives_current_report_and_preserves_unmanaged_content(
    tmp_path: Path,
) -> None:
    official = tmp_path / "official"
    official.mkdir()
    report = official / "DL-001 Product Qualification Testing Report_Rev_A.docx"
    report.write_bytes(b"purpose|conclusion|old-llcr|equipment")
    writer = _Writer()
    service = _service(
        tmp_path,
        workspace=_workspace(tmp_path, official),
        reports=(),
        writer=writer,
    )
    preview = service.preview_llcr_update(project_id="P1", dataset_id="dataset-1")

    result = service.update_llcr(
        UpdateCurrentLlcrReportCommand(
            project_id="P1",
            dataset_id="dataset-1",
            expected_report_sha256=preview.current_report.file_sha256 or "",
            updated_by="Even Yang",
        )
    )

    assert result.changed is True
    assert result.mode == "official"
    assert report.read_bytes() == b"purpose|conclusion|new-llcr|equipment"
    assert result.archive_path is not None
    assert result.archive_path.read_bytes() == b"purpose|conclusion|old-llcr|equipment"
    assert result.archive_path.parent.parent == tmp_path / "History" / "Report"
    assert writer.source_path == report
    assert writer.dataset.dataset_id == "dataset-1"


def test_llcr_update_does_not_create_history_when_report_is_already_current(
    tmp_path: Path,
) -> None:
    official = tmp_path / "official"
    official.mkdir()
    report = official / "DL-001 Product Qualification Testing Report_Rev_A.docx"
    report.write_bytes(b"purpose|new-llcr|equipment")
    service = _service(
        tmp_path,
        workspace=_workspace(tmp_path, official),
        reports=(),
    )
    preview = service.preview_llcr_update(project_id="P1", dataset_id="dataset-1")

    result = service.update_llcr(
        UpdateCurrentLlcrReportCommand(
            project_id="P1",
            dataset_id="dataset-1",
            expected_report_sha256=preview.current_report.file_sha256 or "",
            updated_by="Even Yang",
        )
    )

    assert result.changed is False
    assert result.archive_path is None
    assert not (tmp_path / "History").exists()


def test_llcr_update_rejects_dataset_stale_for_active_matrix(tmp_path: Path) -> None:
    draft = tmp_path / "report.docx"
    draft.write_bytes(b"draft")
    service = _service(
        tmp_path,
        workspace=None,
        reports=(_report_revision(draft),),
        matrix_id="matrix-2",
        matrix_revision=4,
    )

    with pytest.raises(CurrentReportUpdateError, match="stale"):
        service.preview_llcr_update(project_id="P1", dataset_id="dataset-1")


def _service(
    tmp_path: Path,
    *,
    workspace,
    reports: tuple[ReportDraftRevision, ...],
    writer=None,
    matrix_id: str = "matrix-1",
    matrix_revision: int = 3,
) -> CurrentReportUpdateService:
    return CurrentReportUpdateService(
        workspace_store=_WorkspaceStore(workspace),
        report_store=_ReportStore(reports, (_dataset("dataset-1", 1),)),
        confirmed_matrix_store=_MatrixStore(matrix_id, matrix_revision),
        llcr_writer=writer or _Writer(),
        files=ReportPublicationGateway(
            clock=lambda: datetime(2026, 8, 30, 14, 35, 22)
        ),
    )


def _workspace(tmp_path: Path, official: Path):
    return SimpleNamespace(
        project_id="P1",
        dl_number="DL-001",
        local_workspace_path=tmp_path,
        official_folder_path=official,
    )


def _report_revision(path: Path) -> ReportDraftRevision:
    return ReportDraftRevision(
        report_revision_id="report-1",
        project_id="P1",
        revision=1,
        file_name=path.name,
        file_path=str(path),
        file_sha256="unused",
        size_bytes=path.stat().st_size,
        confirmed_matrix_id="matrix-1",
        result_dataset_id=None,
        base_report_revision_id=None,
        created_at="2026-08-30T10:00:00Z",
        created_by="Even Yang",
    )


class _WorkspaceStore:
    def __init__(self, workspace):
        self.workspace = workspace

    def get_by_project(self, project_id):
        return self.workspace


class _ReportStore:
    def __init__(self, reports, datasets):
        self.reports = reports
        self.datasets = datasets

    def latest_report_revision(self, project_id):
        return self.reports[-1] if self.reports else None

    def get_dataset(self, dataset_id):
        return next((item for item in self.datasets if item.dataset_id == dataset_id), None)


class _MatrixStore:
    def __init__(self, matrix_id, revision):
        self.active = SimpleNamespace(
            version=SimpleNamespace(
                confirmed_matrix_id=matrix_id,
                confirmed_revision=revision,
            )
        )

    def get_active_by_project(self, project_id):
        return self.active


class _Writer:
    def synchronize_llcr_results(self, *, source_path, output_path, dataset):
        self.source_path = source_path
        self.dataset = dataset
        output_path.write_bytes(
            source_path.read_bytes().replace(b"old-llcr", b"new-llcr")
        )
        return output_path
