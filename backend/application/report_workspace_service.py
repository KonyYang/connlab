"""Coordinate Internal Report draft revisions and LLCR synchronization."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import re
from typing import Callable, Protocol
from uuid import uuid4

from backend.application.test_report_draft_service import (
    GenerateTestReportDraftCommand,
    TestReportDraftService,
)
from backend.domain.result_dataset_models import (
    ReportDraftRevision,
    ResultDatasetRevision,
)


class ReportWorkspaceError(ValueError):
    """Raised when a report revision cannot be created safely."""


class ReportRevisionStore(Protocol):
    def next_report_revision(self, project_id: str) -> int: ...
    def create_report_revision(self, revision: ReportDraftRevision) -> ReportDraftRevision: ...
    def latest_report_revision(self, project_id: str) -> ReportDraftRevision | None: ...
    def list_report_revisions(self, project_id: str) -> tuple[ReportDraftRevision, ...]: ...
    def get_report_revision(self, report_revision_id: str) -> ReportDraftRevision | None: ...
    def get_dataset(self, dataset_id: str) -> ResultDatasetRevision | None: ...
    def list_datasets(self, project_id: str) -> tuple[ResultDatasetRevision, ...]: ...
    def commit(self) -> None: ...
    def rollback(self) -> None: ...


class LlcrReportWriter(Protocol):
    def synchronize_llcr_results(
        self,
        *,
        source_path: Path,
        output_path: Path,
        dataset: ResultDatasetRevision,
    ) -> Path: ...


@dataclass(frozen=True, slots=True)
class GenerateInitialReportCommand:
    project_id: str
    template_path: Path
    output_dir: Path
    created_by: str


@dataclass(frozen=True, slots=True)
class GenerateLlcrReportCommand:
    project_id: str
    dataset_id: str
    output_dir: Path
    created_by: str
    template_path: Path | None = None


@dataclass(frozen=True, slots=True)
class ReportWorkspaceState:
    project_id: str
    basic_information_status: str
    confirmed_basic_information_version: int | None
    active_confirmed_matrix_id: str | None
    active_confirmed_matrix_revision: int | None
    datasets: tuple[ResultDatasetRevision, ...]
    report_revisions: tuple[ReportDraftRevision, ...]
    latest_report_revision: ReportDraftRevision | None


class ReportWorkspaceService:
    """Deep module for append-only report draft history."""

    def __init__(
        self,
        *,
        repository: ReportRevisionStore,
        initial_report_service: TestReportDraftService,
        llcr_writer: LlcrReportWriter,
        clock: Callable[[], str],
        id_factory: Callable[[], str] = lambda: uuid4().hex,
        basic_information_reader=None,
        confirmed_matrix_store=None,
    ) -> None:
        self._repository = repository
        self._initial = initial_report_service
        self._writer = llcr_writer
        self._clock = clock
        self._ids = id_factory
        self._basic_information = basic_information_reader
        self._confirmed_matrix = confirmed_matrix_store

    def get_state(self, project_id: str) -> ReportWorkspaceState:
        reports = self._repository.list_report_revisions(project_id)
        basic_information = (
            self._basic_information.get_latest_confirmed(project_id)
            if self._basic_information is not None
            else None
        )
        matrix = (
            self._confirmed_matrix.get_active_by_project(project_id)
            if self._confirmed_matrix is not None
            else None
        )
        return ReportWorkspaceState(
            project_id=project_id,
            basic_information_status="confirmed" if basic_information is not None else "missing",
            confirmed_basic_information_version=(
                basic_information.version if basic_information is not None else None
            ),
            active_confirmed_matrix_id=(
                matrix.version.confirmed_matrix_id if matrix is not None else None
            ),
            active_confirmed_matrix_revision=(
                matrix.version.confirmed_revision if matrix is not None else None
            ),
            datasets=self._repository.list_datasets(project_id),
            report_revisions=reports,
            latest_report_revision=reports[-1] if reports else None,
        )

    def get_report_revision(
        self,
        project_id: str,
        report_revision_id: str,
    ) -> ReportDraftRevision:
        revision = self._repository.get_report_revision(report_revision_id)
        if revision is None or revision.project_id != project_id:
            raise LookupError("Report draft revision not found.")
        if not Path(revision.file_path).is_file():
            raise FileNotFoundError("Report draft revision file is missing.")
        return revision

    def generate_initial(
        self,
        command: GenerateInitialReportCommand,
    ) -> ReportDraftRevision:
        generated = self._initial.generate(
            GenerateTestReportDraftCommand(
                project_id=command.project_id,
                template_path=command.template_path,
                output_dir=command.output_dir,
            )
        )
        path = Path(generated.output_path)
        revision = self._build_report_revision(
            project_id=command.project_id,
            path=path,
            confirmed_matrix_id=generated.confirmed_matrix_id,
            dataset_id=None,
            base_report_id=None,
            created_by=command.created_by,
        )
        try:
            created = self._repository.create_report_revision(revision)
            self._repository.commit()
            return created
        except Exception:
            self._repository.rollback()
            path.unlink(missing_ok=True)
            raise

    def generate_llcr_report(
        self,
        command: GenerateLlcrReportCommand,
    ) -> ReportDraftRevision:
        dataset = self._repository.get_dataset(command.dataset_id)
        if dataset is None or dataset.project_id != command.project_id:
            raise ReportWorkspaceError("Confirmed LLCR ResultDataset revision not found.")
        if self._confirmed_matrix is not None:
            active_matrix = self._confirmed_matrix.get_active_by_project(command.project_id)
            if active_matrix is None or (
                active_matrix.version.confirmed_matrix_id != dataset.confirmed_matrix_id
                or active_matrix.version.confirmed_revision != dataset.confirmed_matrix_revision
            ):
                raise ReportWorkspaceError(
                    "The LLCR dataset is stale for the Active Confirmed Matrix."
                )
        latest = self._repository.latest_report_revision(command.project_id)
        generated_initial_path: Path | None = None
        target: Path | None = None
        try:
            if latest is None:
                if command.template_path is None:
                    raise ReportWorkspaceError("Generate an initial report draft first.")
                latest, generated_initial_path = self._generate_initial_uncommitted(command)
            if latest.confirmed_matrix_id != dataset.confirmed_matrix_id:
                raise ReportWorkspaceError(
                    "The LLCR dataset and latest report use different Confirmed Matrix revisions."
                )
            source = Path(latest.file_path)
            if not source.is_file():
                raise ReportWorkspaceError("Latest report draft file is missing.")
            revision_number = self._repository.next_report_revision(command.project_id)
            folder = Path(command.output_dir) / _safe_component(command.project_id)
            folder.mkdir(parents=True, exist_ok=True)
            target = _reserve_path(
                folder / f"{source.stem} (LLCR Sync {revision_number}){source.suffix}"
            )
            written = self._writer.synchronize_llcr_results(
                source_path=source,
                output_path=target,
                dataset=dataset,
            )
            if Path(written) != target or not target.is_file():
                raise ReportWorkspaceError("LLCR report writer did not produce the reserved draft.")
            revision = self._build_report_revision(
                project_id=command.project_id,
                path=target,
                confirmed_matrix_id=dataset.confirmed_matrix_id,
                dataset_id=dataset.dataset_id,
                base_report_id=latest.report_revision_id,
                created_by=command.created_by,
                revision=revision_number,
            )
            created = self._repository.create_report_revision(revision)
            self._repository.commit()
            return created
        except Exception:
            self._repository.rollback()
            if target is not None:
                target.unlink(missing_ok=True)
            if generated_initial_path is not None:
                generated_initial_path.unlink(missing_ok=True)
            raise

    def _generate_initial_uncommitted(
        self,
        command: GenerateLlcrReportCommand,
    ) -> tuple[ReportDraftRevision, Path]:
        generated = self._initial.generate(
            GenerateTestReportDraftCommand(
                project_id=command.project_id,
                template_path=command.template_path,
                output_dir=command.output_dir,
            )
        )
        path = Path(generated.output_path)
        try:
            revision = self._build_report_revision(
                project_id=command.project_id,
                path=path,
                confirmed_matrix_id=generated.confirmed_matrix_id,
                dataset_id=None,
                base_report_id=None,
                created_by=command.created_by,
            )
            return self._repository.create_report_revision(revision), path
        except Exception:
            path.unlink(missing_ok=True)
            raise

    def _build_report_revision(
        self,
        *,
        project_id: str,
        path: Path,
        confirmed_matrix_id: str,
        dataset_id: str | None,
        base_report_id: str | None,
        created_by: str,
        revision: int | None = None,
    ) -> ReportDraftRevision:
        content = path.read_bytes()
        return ReportDraftRevision(
            report_revision_id=f"report-draft-{self._ids()}",
            project_id=project_id,
            revision=revision or self._repository.next_report_revision(project_id),
            file_name=path.name,
            file_path=str(path),
            file_sha256=sha256(content).hexdigest(),
            size_bytes=len(content),
            confirmed_matrix_id=confirmed_matrix_id,
            result_dataset_id=dataset_id,
            base_report_revision_id=base_report_id,
            created_at=self._clock(),
            created_by=created_by.strip() or "Lab User",
        )


def _safe_component(value: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip()).strip("._")
    return safe or "project"


def _reserve_path(path: Path) -> Path:
    if not path.exists():
        return path
    for suffix in range(2, 10_000):
        candidate = path.with_name(f"{path.stem} ({suffix}){path.suffix}")
        if not candidate.exists():
            return candidate
    raise ReportWorkspaceError("Unable to reserve a non-overwriting report draft name.")
