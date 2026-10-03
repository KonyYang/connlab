"""Initialize or explicitly archive and rebuild the current Internal Report."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path
import tempfile
from typing import Callable, Protocol

from backend.application.current_report_update_service import CurrentReportArtifact, CurrentReportFileUpdateResult
from backend.application.test_report_draft_service import PreparedTestReportDraft, TestReportDraftService, TestReportDraftGenerationError


class InternalReportGenerationError(ValueError):
    """Generation needs a fresh preview or an actionable prerequisite."""


@dataclass(frozen=True, slots=True)
class InternalReportGenerationSnapshot:
    prepared: PreparedTestReportDraft
    current_report: CurrentReportArtifact
    target_dir: Path
    history_root: Path
    mode: str
    authority_signature: str


@dataclass(frozen=True, slots=True)
class InternalReportGenerationPreview:
    project_id: str
    status: str
    preview_token: str | None
    requires_confirmation: bool
    mode: str | None
    current_path: Path | None
    target_path: Path | None
    blockers: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class GenerateInternalReportCommand:
    project_id: str
    preview_token: str
    archive_and_regenerate: bool = False
    created_by: str = "Lab User"


@dataclass(frozen=True, slots=True)
class InternalReportGenerationResult:
    project_id: str
    mode: str
    file_name: str
    file_path: Path
    file_sha256: str
    archive_path: Path | None


class InternalReportGenerationFiles(Protocol):
    def fingerprint(self, path: Path) -> str: ...
    def publish_regenerated_current(self, **kwargs) -> CurrentReportFileUpdateResult: ...


class InternalReportGenerationService:
    """Bind explicit approval to authority, template, workspace and current report.

    ``read_snapshot`` must use fresh persisted reads on every call. A latest report
    revision in that signature also makes successful byte-identical requests stale.
    All document work completes in owned temporary storage before retiring the old
    file. The publication boundary acknowledges metadata or restores the old file.
    """

    def __init__(self, *, read_snapshot: Callable[[str], InternalReportGenerationSnapshot],
                 drafts: TestReportDraftService, files: InternalReportGenerationFiles,
                 persist: Callable[..., None], staging_root: Path):
        self._read = read_snapshot
        self._drafts = drafts
        self._files = files
        self._persist = persist
        self._staging_root = Path(staging_root)

    def preview(self, project_id: str) -> InternalReportGenerationPreview:
        try:
            snapshot = self._read(project_id)
            self._require_snapshot(snapshot)
        except (ValueError, LookupError, OSError) as exc:
            return InternalReportGenerationPreview(project_id, "blocked", None, False, None, None, None, (str(exc),))
        return InternalReportGenerationPreview(
            project_id, "ready", self._token(snapshot),
            snapshot.current_report.status == "ready", snapshot.mode,
            snapshot.current_report.file_path,
            snapshot.target_dir / snapshot.prepared.file_name,
        )

    def generate(self, command: GenerateInternalReportCommand) -> InternalReportGenerationResult:
        snapshot = self._read(command.project_id)
        self._require_snapshot(snapshot)
        self._require_token(snapshot, command.preview_token)
        current = snapshot.current_report
        if current.status == "ready" and not command.archive_and_regenerate:
            raise InternalReportGenerationError("Explicitly confirm Archive and regenerate to preserve the old report in History/Report.")
        if current.status != "ready" and command.archive_and_regenerate:
            raise InternalReportGenerationError("The current report is missing. Preview generation again before creating a new report.")

        def revalidate() -> None:
            latest = self._read(command.project_id)
            self._require_snapshot(latest)
            self._require_token(latest, command.preview_token)

        self._staging_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="internal-report-", dir=self._staging_root) as temporary:
            try:
                generated = self._drafts.generate_staged(snapshot.prepared, output_path=Path(temporary) / "report.docx")
            except TestReportDraftGenerationError as exc:
                raise InternalReportGenerationError("Internal Report generation failed before publication. Check the approved template, close Word and preview again; check generation logs if the problem persists.") from exc
            revalidate()
            snapshot.target_dir.mkdir(parents=True, exist_ok=True)
            target = snapshot.target_dir / generated.file_name

            def persist(result: CurrentReportFileUpdateResult) -> None:
                self._persist(
                    project_id=command.project_id,
                    path=result.current_path,
                    confirmed_matrix_id=generated.confirmed_matrix_id,
                    created_by=command.created_by,
                    previous_path=current.file_path,
                    archive_path=result.archive_path,
                )

            published = self._files.publish_regenerated_current(
                source_path=generated.output_path,
                expected_source_sha256=self._files.fingerprint(generated.output_path),
                current_path=current.file_path,
                expected_current_sha256=current.file_sha256,
                target_path=target,
                history_root=snapshot.history_root,
                pre_publish=revalidate,
                persist=persist,
            )
        return InternalReportGenerationResult(command.project_id, snapshot.mode, published.current_path.name,
                                              published.current_path, published.current_sha256, published.archive_path)

    @staticmethod
    def _require_snapshot(snapshot: InternalReportGenerationSnapshot) -> None:
        if snapshot.current_report.status == "ambiguous":
            raise InternalReportGenerationError("Multiple current Internal Reports were found. Keep exactly one in the project folder and preview again.")
        target = snapshot.target_dir / snapshot.prepared.file_name
        if target.exists() and target != snapshot.current_report.file_path:
            raise InternalReportGenerationError("A file already occupies the new report destination. Resolve that conflict and preview again.")

    @staticmethod
    def _token(snapshot: InternalReportGenerationSnapshot) -> str:
        payload = {"operation": "internal_report_archive_regenerate" if snapshot.current_report.status == "ready" else "internal_report_initialize",
                   "snapshot": asdict(snapshot)}
        return sha256(json.dumps(payload, default=str, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()

    def _require_token(self, snapshot: InternalReportGenerationSnapshot, expected: str) -> None:
        if not expected or expected != self._token(snapshot):
            raise InternalReportGenerationError("The report, confirmed authority, template or project folder changed. Preview generation again.")
