from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from backend.application.report_workspace_service import (
    GenerateInitialReportCommand,
    GenerateLlcrReportCommand,
    ReportWorkspaceService,
)
from backend.application.test_report_draft_service import TestReportDraftGenerationResult
from tests.unit.test_result_dataset_repository import _dataset


def test_workspace_records_initial_and_llcr_report_revisions_without_overwrite(tmp_path) -> None:
    repository = _Repository()
    initial_file = tmp_path / "generated" / "P1" / "initial.docx"
    initial_file.parent.mkdir(parents=True)
    initial_service = _InitialService(initial_file)
    writer = _Writer()
    service = ReportWorkspaceService(
        repository=repository,
        initial_report_service=initial_service,
        llcr_writer=writer,
        clock=lambda: "2026-08-29T09:00:00Z",
        id_factory=iter(("report-1", "report-2")).__next__,
    )

    initial = service.generate_initial(
        GenerateInitialReportCommand(
            project_id="P1",
            template_path=tmp_path / "template.docx",
            output_dir=tmp_path / "generated",
            created_by="Even Yang",
        )
    )
    dataset = _dataset("dataset-1", 1)
    repository.datasets.append(dataset)
    synchronized = service.generate_llcr_report(
        GenerateLlcrReportCommand(
            project_id="P1",
            dataset_id="dataset-1",
            output_dir=tmp_path / "generated",
            created_by="Even Yang",
        )
    )

    assert initial.revision == 1
    assert synchronized.revision == 2
    assert synchronized.base_report_revision_id == initial.report_revision_id
    assert synchronized.result_dataset_id == "dataset-1"
    assert Path(initial.file_path).read_bytes() == b"initial"
    assert Path(synchronized.file_path).read_bytes() == b"initial|llcr"
    assert writer.source_path == Path(initial.file_path)
    assert writer.output_path != writer.source_path
    assert repository.reports == [initial, synchronized]
    state = service.get_state("P1")
    assert state.latest_report_revision.revision == 2
    assert state.datasets == (dataset,)


def test_llcr_sync_rejects_stale_active_matrix_before_writing(tmp_path) -> None:
    repository = _Repository()
    initial_file = tmp_path / "generated" / "P1" / "initial.docx"
    initial_file.parent.mkdir(parents=True)
    service = ReportWorkspaceService(
        repository=repository,
        initial_report_service=_InitialService(initial_file),
        llcr_writer=_Writer(),
        clock=lambda: "2026-08-29T09:00:00Z",
        confirmed_matrix_store=_ConfirmedMatrixStore("matrix-2", 4),
    )
    service.generate_initial(
        GenerateInitialReportCommand("P1", tmp_path / "template.docx", tmp_path, "Lab User")
    )
    repository.datasets.append(_dataset("dataset-1", 1))

    with pytest.raises(ValueError, match="stale for the Active Confirmed Matrix"):
        service.generate_llcr_report(
            GenerateLlcrReportCommand("P1", "dataset-1", tmp_path, "Lab User")
        )

    assert len(repository.reports) == 1
    assert list((tmp_path / "P1").glob("*.docx")) == []


def test_failed_revision_persistence_removes_new_file_and_keeps_source(tmp_path) -> None:
    repository = _Repository()
    initial_file = tmp_path / "generated" / "P1" / "initial.docx"
    initial_file.parent.mkdir(parents=True)
    service = ReportWorkspaceService(
        repository=repository,
        initial_report_service=_InitialService(initial_file),
        llcr_writer=_Writer(),
        clock=lambda: "2026-08-29T09:00:00Z",
    )
    initial = service.generate_initial(
        GenerateInitialReportCommand("P1", tmp_path / "template.docx", tmp_path, "Lab User")
    )
    repository.datasets.append(_dataset("dataset-1", 1))
    repository.fail_report_creation = True

    with pytest.raises(RuntimeError, match="database unavailable"):
        service.generate_llcr_report(
            GenerateLlcrReportCommand("P1", "dataset-1", tmp_path, "Lab User")
        )

    assert Path(initial.file_path).read_bytes() == b"initial"
    assert len(repository.reports) == 1
    assert list((tmp_path / "P1").glob("*.docx")) == []


def test_failed_revision_commit_removes_new_file_and_keeps_source(tmp_path) -> None:
    repository = _Repository()
    initial_file = tmp_path / "generated" / "P1" / "initial.docx"
    initial_file.parent.mkdir(parents=True)
    service = ReportWorkspaceService(
        repository=repository,
        initial_report_service=_InitialService(initial_file),
        llcr_writer=_Writer(),
        clock=lambda: "2026-08-29T09:00:00Z",
    )
    initial = service.generate_initial(
        GenerateInitialReportCommand("P1", tmp_path / "template.docx", tmp_path, "Lab User")
    )
    repository.datasets.append(_dataset("dataset-1", 1))
    repository.fail_commit = True

    with pytest.raises(RuntimeError, match="commit failed"):
        service.generate_llcr_report(
            GenerateLlcrReportCommand("P1", "dataset-1", tmp_path, "Lab User")
        )

    assert Path(initial.file_path).read_bytes() == b"initial"
    assert len(repository.reports) == 1
    assert list((tmp_path / "P1").glob("*.docx")) == []


def test_first_llcr_sync_is_atomic_when_writer_fails_after_initial_generation(tmp_path) -> None:
    repository = _Repository()
    initial_file = tmp_path / "generated" / "P1" / "initial.docx"
    initial_file.parent.mkdir(parents=True)
    service = ReportWorkspaceService(
        repository=repository,
        initial_report_service=_InitialService(initial_file),
        llcr_writer=_FailingWriter(),
        clock=lambda: "2026-08-29T09:00:00Z",
    )
    repository.datasets.append(_dataset("dataset-1", 1))

    with pytest.raises(RuntimeError, match="Word synchronization failed"):
        service.generate_llcr_report(
            GenerateLlcrReportCommand(
                "P1",
                "dataset-1",
                tmp_path / "generated",
                "Lab User",
                tmp_path / "template.docx",
            )
        )

    assert repository.reports == []
    assert not initial_file.exists()
    assert list((tmp_path / "generated" / "P1").glob("*.docx")) == []


def test_first_llcr_sync_commits_initial_and_synchronized_revisions_together(tmp_path) -> None:
    repository = _Repository()
    initial_file = tmp_path / "generated" / "P1" / "initial.docx"
    initial_file.parent.mkdir(parents=True)
    service = ReportWorkspaceService(
        repository=repository,
        initial_report_service=_InitialService(initial_file),
        llcr_writer=_Writer(),
        clock=lambda: "2026-08-29T09:00:00Z",
        id_factory=iter(("report-1", "report-2")).__next__,
    )
    repository.datasets.append(_dataset("dataset-1", 1))

    synchronized = service.generate_llcr_report(
        GenerateLlcrReportCommand(
            "P1",
            "dataset-1",
            tmp_path / "generated",
            "Lab User",
            tmp_path / "template.docx",
        )
    )

    assert [item.revision for item in repository.reports] == [1, 2]
    assert synchronized.revision == 2
    assert repository.commit_count == 1


class _Repository:
    def __init__(self):
        self.datasets = []
        self.reports = []
        self.fail_report_creation = False
        self.fail_commit = False
        self.commit_count = 0
        self.committed_report_count = 0

    def next_report_revision(self, project_id):
        return len(self.reports) + 1

    def create_report_revision(self, report):
        if self.fail_report_creation:
            raise RuntimeError("database unavailable")
        self.reports.append(report)
        return report

    def commit(self):
        if self.fail_commit:
            raise RuntimeError("commit failed")
        self.commit_count += 1
        self.committed_report_count = len(self.reports)

    def rollback(self):
        del self.reports[self.committed_report_count:]

    def latest_report_revision(self, project_id):
        return self.reports[-1] if self.reports else None

    def list_report_revisions(self, project_id):
        return tuple(self.reports)

    def get_dataset(self, dataset_id):
        return next((item for item in self.datasets if item.dataset_id == dataset_id), None)

    def list_datasets(self, project_id):
        return tuple(self.datasets)


class _InitialService:
    def __init__(self, output_path):
        self.output_path = output_path

    def generate(self, command):
        self.output_path.write_bytes(b"initial")
        return TestReportDraftGenerationResult(
            project_id="P1",
            confirmed_matrix_id="matrix-1",
            output_path=self.output_path,
            file_name=self.output_path.name,
            confirmed_basic_information_version=1,
            confirmed_basic_information_source_signature_hash="basic-hash",
        )


class _Writer:
    def synchronize_llcr_results(self, *, source_path, output_path, dataset):
        self.source_path = source_path
        self.output_path = output_path
        output_path.write_bytes(source_path.read_bytes() + b"|llcr")
        return output_path


class _FailingWriter:
    def synchronize_llcr_results(self, *, source_path, output_path, dataset):
        output_path.write_bytes(b"partial")
        raise RuntimeError("Word synchronization failed")


class _ConfirmedMatrixStore:
    def __init__(self, matrix_id, revision):
        self.active = SimpleNamespace(
            version=SimpleNamespace(
                confirmed_matrix_id=matrix_id,
                confirmed_revision=revision,
            )
        )

    def get_active_by_project(self, project_id):
        return self.active
