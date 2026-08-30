"""Coordinate safe, region-scoped updates of the current Internal Report."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Protocol

from backend.domain.result_dataset_models import (
    ReportDraftRevision,
    ResultDatasetRevision,
)


class CurrentReportUpdateError(ValueError):
    """Raised when a current report update cannot be performed safely."""


class CurrentReportFileConflictError(RuntimeError):
    """Raised when the current report changed or is locked during publication."""


class OfficialWorkspaceStore(Protocol):
    def get_by_project(self, project_id: str): ...


class CurrentReportStore(Protocol):
    def latest_report_revision(self, project_id: str) -> ReportDraftRevision | None: ...
    def get_dataset(self, dataset_id: str) -> ResultDatasetRevision | None: ...


class ConfirmedMatrixStore(Protocol):
    def get_active_by_project(self, project_id: str): ...


class LlcrReportWriter(Protocol):
    def synchronize_llcr_results(
        self,
        *,
        source_path: Path,
        output_path: Path,
        dataset: ResultDatasetRevision,
    ) -> Path: ...


class CurrentReportFiles(Protocol):
    def discover_internal_reports(
        self,
        *,
        official_folder: Path,
        dl_number: str,
    ) -> tuple[Path, ...]: ...

    def fingerprint(self, path: Path) -> str: ...

    def publish_update(
        self,
        *,
        current_path: Path,
        expected_current_sha256: str,
        history_root: Path,
        update_document: Callable[[Path, Path], Path],
    ) -> "CurrentReportFileUpdateResult": ...


@dataclass(frozen=True, slots=True)
class CurrentReportFileUpdateResult:
    current_path: Path
    current_sha256: str
    changed: bool
    archive_path: Path | None


@dataclass(frozen=True, slots=True)
class CurrentReportArtifact:
    status: str
    mode: str | None
    file_name: str | None
    file_path: Path | None
    file_sha256: str | None
    history_root: Path | None
    report_revision_id: str | None = None
    confirmed_matrix_id: str | None = None


@dataclass(frozen=True, slots=True)
class CurrentReportUpdatePreview:
    project_id: str
    dataset_id: str
    status: str
    current_report: CurrentReportArtifact
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class UpdateCurrentLlcrReportCommand:
    project_id: str
    dataset_id: str
    expected_report_sha256: str
    updated_by: str


@dataclass(frozen=True, slots=True)
class CurrentReportUpdateResult:
    project_id: str
    dataset_id: str
    file_name: str
    mode: str
    changed: bool
    current_sha256: str
    archive_path: Path | None
    updated_by: str


class CurrentReportUpdateService:
    """Resolve one current report and publish an isolated LLCR region update."""

    def __init__(
        self,
        *,
        workspace_store: OfficialWorkspaceStore,
        report_store: CurrentReportStore,
        confirmed_matrix_store: ConfirmedMatrixStore,
        llcr_writer: LlcrReportWriter,
        files: CurrentReportFiles,
    ) -> None:
        self._workspaces = workspace_store
        self._reports = report_store
        self._matrices = confirmed_matrix_store
        self._writer = llcr_writer
        self._files = files

    def preview_llcr_update(
        self,
        *,
        project_id: str,
        dataset_id: str,
    ) -> CurrentReportUpdatePreview:
        dataset = self._require_current_llcr_dataset(project_id, dataset_id)
        report, blockers, warnings = self._resolve_current_report(project_id)
        if (
            report.mode == "managed_draft"
            and report.confirmed_matrix_id != dataset.confirmed_matrix_id
        ):
            blockers = blockers + (
                "The controlled draft was generated from a different Confirmed Matrix. "
                "Create a new initial report before updating LLCR results.",
            )
        return CurrentReportUpdatePreview(
            project_id=project_id,
            dataset_id=dataset.dataset_id,
            status="blocked" if blockers else "ready",
            current_report=report,
            blockers=blockers,
            warnings=warnings,
        )

    def update_llcr(
        self,
        command: UpdateCurrentLlcrReportCommand,
    ) -> CurrentReportUpdateResult:
        preview = self.preview_llcr_update(
            project_id=command.project_id,
            dataset_id=command.dataset_id,
        )
        if preview.blockers:
            raise CurrentReportUpdateError(" ".join(preview.blockers))
        report = preview.current_report
        if (
            report.file_path is None
            or report.file_name is None
            or report.file_sha256 is None
            or report.history_root is None
            or report.mode is None
        ):
            raise CurrentReportUpdateError("The current internal report is unavailable.")
        if command.expected_report_sha256.strip().casefold() != report.file_sha256:
            raise CurrentReportFileConflictError(
                "The current report changed after preview. Preview the update again."
            )
        dataset = self._require_current_llcr_dataset(
            command.project_id,
            command.dataset_id,
        )
        published = self._files.publish_update(
            current_path=report.file_path,
            expected_current_sha256=command.expected_report_sha256,
            history_root=report.history_root,
            update_document=lambda source, output: self._writer.synchronize_llcr_results(
                source_path=source,
                output_path=output,
                dataset=dataset,
            ),
        )
        return CurrentReportUpdateResult(
            project_id=command.project_id,
            dataset_id=command.dataset_id,
            file_name=report.file_name,
            mode=report.mode,
            changed=published.changed,
            current_sha256=published.current_sha256,
            archive_path=published.archive_path,
            updated_by=command.updated_by.strip(),
        )

    def get_current_report(self, project_id: str) -> CurrentReportArtifact:
        report, _, _ = self._resolve_current_report(project_id)
        return report

    def _require_current_llcr_dataset(
        self,
        project_id: str,
        dataset_id: str,
    ) -> ResultDatasetRevision:
        dataset = self._reports.get_dataset(dataset_id)
        if (
            dataset is None
            or dataset.project_id != project_id
            or dataset.dataset_type != "llcr"
            or dataset.validation_status != "confirmed"
        ):
            raise CurrentReportUpdateError(
                "A confirmed LLCR result dataset for this project is required."
            )
        matrix = self._matrices.get_active_by_project(project_id)
        version = getattr(matrix, "version", None)
        if (
            version is None
            or dataset.confirmed_matrix_id != version.confirmed_matrix_id
            or dataset.confirmed_matrix_revision != version.confirmed_revision
        ):
            raise CurrentReportUpdateError(
                "The LLCR result dataset is stale for the Active Confirmed Matrix."
            )
        return dataset

    def _resolve_current_report(
        self,
        project_id: str,
    ) -> tuple[CurrentReportArtifact, tuple[str, ...], tuple[str, ...]]:
        workspace = self._workspaces.get_by_project(project_id)
        if workspace is not None:
            official_folder = Path(workspace.official_folder_path)
            candidates = self._files.discover_internal_reports(
                official_folder=official_folder,
                dl_number=workspace.dl_number,
            )
            if len(candidates) > 1:
                blocker = (
                    "Multiple current internal reports were found in the official project "
                    "folder. Keep exactly one before updating."
                )
                return (
                    CurrentReportArtifact(
                        status="ambiguous",
                        mode="official",
                        file_name=None,
                        file_path=None,
                        file_sha256=None,
                        history_root=Path(workspace.local_workspace_path)
                        / "History"
                        / "Report",
                    ),
                    (blocker,),
                    tuple(),
                )
            if len(candidates) == 1:
                path = candidates[0]
                return (
                    CurrentReportArtifact(
                        status="ready",
                        mode="official",
                        file_name=path.name,
                        file_path=path,
                        file_sha256=self._files.fingerprint(path),
                        history_root=Path(workspace.local_workspace_path)
                        / "History"
                        / "Report",
                    ),
                    tuple(),
                    tuple(),
                )

        managed = self._reports.latest_report_revision(project_id)
        if managed is not None:
            path = Path(managed.file_path)
            if path.is_file():
                warning = (
                    "No official project report is available; the controlled draft will be updated."
                )
                return (
                    CurrentReportArtifact(
                        status="ready",
                        mode="managed_draft",
                        file_name=path.name,
                        file_path=path,
                        file_sha256=self._files.fingerprint(path),
                        history_root=path.parent / "History" / "Report",
                        report_revision_id=managed.report_revision_id,
                        confirmed_matrix_id=managed.confirmed_matrix_id,
                    ),
                    tuple(),
                    (warning,),
                )

        blocker = "No current internal report is available for this project."
        return (
            CurrentReportArtifact(
                status="missing",
                mode=None,
                file_name=None,
                file_path=None,
                file_sha256=None,
                history_root=None,
            ),
            (blocker,),
            tuple(),
        )
