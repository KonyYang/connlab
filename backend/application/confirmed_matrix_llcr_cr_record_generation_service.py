"""Preview-fingerprint-protected generation for specialized LLCR/CR records."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from contextlib import nullcontext
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Protocol

from backend.application.matrix_editor_llcr_cr_record_generation_service import (
    GenerateMatrixEditorLlcrCrRecordCommand,
)
from backend.application.matrix_editor_llcr_cr_record_projection import (
    build_matrix_editor_llcr_cr_record_projection,
)
from backend.application.matrix_editor_test_record_authority import (
    ConfirmedMatrixTestRecordAuthorityMatcher,
    build_matrix_editor_test_record_signature,
)
from backend.application.matrix_test_points_authority import validate_matrix_test_points
from backend.infrastructure.files.generation_journal import fingerprint
from backend.infrastructure.files.recoverable_output_publisher import file_hash, file_identity
from backend.infrastructure.files.project_folder_required_forms_gateway import RecoverableContactRecordPublisher
from backend.infrastructure.official_workspace_manifest import OfficialWorkspaceManifestGateway
from backend.application.project_output_record_service import RegisterProjectOutputCommand
from backend.domain import ProjectOutputKind, ProjectOutputSource, ProjectOutputStatus

from backend.application.confirmed_matrix_llcr_cr_record_preview_service import (
    LlcrCrRecordWorkbookPreviewService,
)
from backend.application.confirmed_matrix_llcr_cr_record_projection import (
    LlcrCrRecordProjection,
)
from backend.infrastructure.files.llcr_cr_specialized_record_artifact_store import (
    LlcrCrSpecializedRecordArtifactStore,
)


class LlcrCrRecordWorkbookGenerationError(ValueError):
    """Raised when preview state cannot safely create a specialized workbook."""


class LlcrCrRecordWorkbookWriter(Protocol):
    """Workbook write capability held by the Office infrastructure boundary."""

    def write(self, *, output_path: Path, projection: LlcrCrRecordProjection) -> Path:
        """Write one macro-free specialized workbook from a ready projection."""


@dataclass(frozen=True, slots=True)
class GenerateLlcrCrRecordWorkbookCommand:
    """One explicit request to generate a previously previewed workbook."""

    project_id: str
    preview_fingerprint: str
    record_type: str = "llcr"


@dataclass(frozen=True, slots=True)
class LlcrCrRecordWorkbookGenerationResult:
    """Safe generated artifact metadata for route/client download handling."""

    project_id: str
    confirmed_matrix_id: str
    confirmed_revision: int
    artifact_id: str
    file_name: str
    output_path: Path
    record_type: str = "llcr"


class LlcrCrRecordWorkbookGenerationService:
    """Regenerate a confirmed projection and write only after fingerprint match."""

    def __init__(
        self,
        *,
        preview_service: LlcrCrRecordWorkbookPreviewService,
        workbook_gateway: LlcrCrRecordWorkbookWriter,
        artifact_store: LlcrCrSpecializedRecordArtifactStore,
    ) -> None:
        self._preview_service = preview_service
        self._workbook_gateway = workbook_gateway
        self._artifact_store = artifact_store

    def generate(
        self,
        command: GenerateLlcrCrRecordWorkbookCommand,
    ) -> LlcrCrRecordWorkbookGenerationResult:
        """Write one workbook only when the requested preview is still current."""
        projection = self._preview_service.preview(command.project_id, command.record_type)
        if projection.status not in {"ready", "complete", "partial_compatible"} or not projection.preview_fingerprint:
            raise LlcrCrRecordWorkbookGenerationError(
                "LLCR/CR workbook preview requires review before generation."
            )
        if projection.preview_fingerprint != command.preview_fingerprint:
            raise LlcrCrRecordWorkbookGenerationError(
                "Confirmed Matrix contact plan changed. Preview again before generating."
            )
        artifact = self._artifact_store.prepare(
            project_id=projection.project_id,
            confirmed_revision=projection.confirmed_revision,
            record_type=command.record_type,
        )
        try:
            written = self._workbook_gateway.write(
                output_path=artifact.output_path,
                projection=projection,
            )
        except (OSError, ValueError) as exc:
            raise LlcrCrRecordWorkbookGenerationError(
                f"Unable to generate LLCR/CR workbook: {exc}"
            ) from exc
        return LlcrCrRecordWorkbookGenerationResult(
            project_id=projection.project_id,
            confirmed_matrix_id=projection.confirmed_matrix_id,
            confirmed_revision=projection.confirmed_revision,
            artifact_id=artifact.artifact_id,
            file_name=artifact.file_name,
            output_path=written,
            record_type=command.record_type,
        )


@dataclass(frozen=True, slots=True)
class PreviewMatrixEditorLlcrCrPublicationCommand:
    draft: GenerateMatrixEditorLlcrCrRecordCommand
    matrix_has_pending_changes: bool = False


@dataclass(frozen=True, slots=True)
class MatrixEditorLlcrCrPublicationPreview:
    project_id: str
    mode: str
    status: str
    authority_status: str
    target_path: Path | None
    existing_file: bool
    blockers: tuple[str, ...]
    preview_token: str
    target_facts: dict | None = None


@dataclass(frozen=True, slots=True)
class PublishMatrixEditorLlcrCrPublicationCommand:
    draft: GenerateMatrixEditorLlcrCrRecordCommand
    preview_token: str
    conflict_action: str = "none"
    matrix_has_pending_changes: bool = False


@dataclass(frozen=True, slots=True)
class MatrixEditorLlcrCrPublicationResult:
    project_id: str
    file_name: str
    target_path: Path
    archive_path: Path | None


class MatrixEditorLlcrCrRecordPublicationService:
    """Select draft-download or formal-file publication from current Matrix authority."""

    def __init__(
        self, *, confirmed_store, preview_service: LlcrCrRecordWorkbookPreviewService,
        workspace_store, workspace_verifier, journal=None, workbook_gateway=None,
        output_service=None, staging_root: Path | None = None, commit=None,
        folder_generation_journal=None, write_guard=None,
    ) -> None:
        self._confirmed = confirmed_store
        self._preview_service = preview_service
        self._workspaces = workspace_store
        self._workspace_verifier = workspace_verifier
        self._journal = journal
        self._writer = workbook_gateway
        self._outputs = output_service
        self._staging_root = staging_root
        self._commit = commit
        self._folder_journal = folder_generation_journal
        self._write_guard = write_guard

    def preview(
        self, command: PreviewMatrixEditorLlcrCrPublicationCommand,
    ) -> MatrixEditorLlcrCrPublicationPreview:
        draft = command.draft
        if draft.record_type not in {"llcr", "cr"}:
            raise ValueError("Record type must be llcr or cr.")
        profile, overrides = validate_matrix_test_points(draft.point_profile, draft.point_overrides)
        snapshot = self._confirmed.get_active_by_project(draft.project_id)
        matches = False
        if snapshot is not None and snapshot.version.point_profile is not None:
            signature = build_matrix_editor_test_record_signature(
                groups=draft.groups, rows=draft.rows,
                step_text_overrides=draft.step_text_overrides,
            )
            matches = (
                not command.matrix_has_pending_changes
                and ConfirmedMatrixTestRecordAuthorityMatcher(self._confirmed).matches_active_authority(
                    draft.project_id, signature,
                )
                and profile == snapshot.version.point_profile
                and overrides == snapshot.version.point_overrides
                and _sample_notes_match(draft, snapshot)
            )
        workspace = self._workspaces.get_by_project(draft.project_id) if matches else None
        verified = bool(workspace is not None and self._workspace_verifier(workspace))
        official_folder = Path(workspace.official_folder_path) if verified else None
        projection_fingerprint = None
        projection_status = None
        if official_folder is None or not (official_folder / "Test results").is_dir():
            mode, status, target, facts, blockers = "download", "ready", None, None, ()
            try:
                draft_projection = build_matrix_editor_llcr_cr_record_projection(
                    project_id=draft.project_id, record_type=draft.record_type,
                    groups=draft.groups, rows=draft.rows,
                    point_profile=profile, point_overrides=overrides,
                    step_text_overrides=draft.step_text_overrides,
                )
                if draft_projection.status != "ready" or not draft_projection.sections:
                    status = "blocked"
                    blockers = tuple(item.message for item in draft_projection.diagnostics) or (
                        f"Current Matrix draft does not require {draft.record_type.upper()}.",
                    )
            except ValueError as exc:
                status, blockers = "blocked", (str(exc),)
        else:
            dl = "".join(ch if ch.isalnum() or ch in {"-", " "} else " " for ch in workspace.dl_number).strip(" .")
            if not dl:
                mode, status, target, facts, blockers = (
                    "official", "blocked", None, None, ("Official project DL number is missing.",)
                )
            else:
                target = official_folder / "Test results" / f"{dl} {draft.record_type.upper()} Record.xlsx"
                mode, status, facts, blockers = "official", "ready", None, ()
                if (OfficialWorkspaceManifestGateway.first_redirected_path(target, *target.parents) is not None
                        or os.path.lexists(target) and not target.is_file()):
                    status, blockers = "blocked", ("Official contact form is not a regular file.",)
                else:
                    try:
                        sha = file_hash(target)
                        facts = {"sha": sha, "identity": file_identity(target)} if sha is not None else None
                        status = "conflict" if facts is not None else "ready"
                    except (OSError, ValueError):
                        status, blockers = "blocked", ("Official contact form cannot be verified.",)
                projection = self._preview_service.preview(draft.project_id, draft.record_type)
                projection_fingerprint = projection.preview_fingerprint
                projection_status = projection.status
                if projection.status != "ready" or not projection.preview_fingerprint:
                    status = "blocked"
                    blockers = ("Confirmed Matrix contact form requires review before publication.",)
        token = fingerprint({
            "draft": asdict(draft), "pending": command.matrix_has_pending_changes,
            "confirmed_matrix_id": snapshot.version.confirmed_matrix_id if snapshot else None,
            "confirmed_revision": snapshot.version.confirmed_revision if snapshot else None,
            "mode": mode, "status": status, "target": str(target) if target else None,
            "facts": facts, "blockers": blockers,
            "projection_fingerprint": projection_fingerprint,
            "projection_status": projection_status,
            "workspace_path": str(workspace.local_workspace_path) if verified else None,
            "workspace_identity": file_identity(Path(workspace.local_workspace_path)) if verified else None,
            "official_path": str(official_folder) if official_folder else None,
            "official_identity": file_identity(official_folder) if official_folder else None,
            "manifest_path": str(workspace.manifest_path) if verified and hasattr(workspace, "manifest_path") else None,
            "manifest_identity": file_identity(Path(workspace.manifest_path)) if verified and hasattr(workspace, "manifest_path") else None,
            "manifest_sha": file_hash(Path(workspace.manifest_path)) if verified and hasattr(workspace, "manifest_path") else None,
        })
        return MatrixEditorLlcrCrPublicationPreview(
            project_id=draft.project_id, mode=mode, status=status,
            authority_status="confirmed" if matches else "unconfirmed",
            target_path=target, existing_file=facts is not None,
            blockers=blockers, preview_token=token, target_facts=facts,
        )

    def validate_download(
        self, command: PreviewMatrixEditorLlcrCrPublicationCommand, preview_token: str,
    ) -> None:
        current = self.preview(command)
        if current.preview_token != preview_token or current.mode != "download" or current.status != "ready":
            raise ValueError("LLCR/CR download preview changed. Preview again before downloading.")

    def publish(
        self, command: PublishMatrixEditorLlcrCrPublicationCommand,
    ) -> MatrixEditorLlcrCrPublicationResult:
        if self._journal is None or self._writer is None or self._outputs is None or self._staging_root is None:
            raise ValueError("Official LLCR/CR publication is not configured.")
        if command.conflict_action not in {"none", "archive"}:
            raise ValueError("Only explicit archive is supported for an existing LLCR/CR form.")
        project_id = command.draft.project_id
        folder_lock = (self._folder_journal.lock(project_id)
                       if self._folder_journal is not None else nullcontext())
        with folder_lock, self._journal.lock(project_id):
            if self._write_guard is not None:
                self._write_guard(project_id)
            if self._folder_journal is not None:
                folder_state = self._folder_journal.read(project_id)
                if folder_state is not None and folder_state["status"] != "completed":
                    raise ValueError("Project folder generation is unfinished; recover it before publishing a contact form.")
            previous = self._journal.read(project_id)
            if previous is not None and previous["status"] != "completed":
                if previous["context"] != command.preview_token:
                    raise ValueError("Previous contact form publication is unfinished; retry its original preview or recover it first.")
                if previous["strategy"] != command.conflict_action:
                    raise ValueError("Contact form recovery action does not match the pending operation.")
                if previous.get("request_signature") not in (None, self._request_signature(command)):
                    raise ValueError("Contact form recovery request differs from the original reviewed draft.")
                if not previous["effects"]:
                    current = self._require_current_publication_preview(command)
                    workspace = self._workspaces.get_by_project(project_id)
                    projection = self._preview_service.preview(project_id, command.draft.record_type)
                    if "authority" in previous:
                        self._verify_authority(previous)
                    elif previous["status"] == "queued":
                        previous.update(status="running", authority=self._authority_facts(workspace, projection),
                                        request_signature=self._request_signature(command))
                        self._journal.save(previous)
                    else:
                        raise ValueError("Contact form publication authority is missing; manual review is required.")
                    return self._write_and_recover(previous, command, current, workspace, projection)
                return self._recover(previous, command)
            if previous is not None and previous["context"] == command.preview_token:
                if previous["strategy"] != command.conflict_action:
                    raise ValueError("Contact form publication action does not match the completed operation.")
                if previous.get("request_signature") != self._request_signature(command):
                    raise ValueError("Contact form publication request differs from the completed operation.")
                result = self._recover(previous, command)
                return result
            current = self._require_current_publication_preview(command)
            workspace = self._workspaces.get_by_project(project_id)
            projection = self._preview_service.preview(project_id, command.draft.record_type)
            if projection.status != "ready" or not projection.preview_fingerprint:
                raise ValueError("Confirmed Matrix contact form changed; preview again.")
            authority = self._authority_facts(workspace, projection)
            self._staging_root.mkdir(parents=True, exist_ok=True)
            state = self._journal.create(project_id, command.conflict_action, command.preview_token)
            state.update(status="running", authority=authority,
                         request_signature=self._request_signature(command))
            self._journal.save(state)
            return self._write_and_recover(state, command, current, workspace, projection)

    def _require_current_publication_preview(self, command):
        current = self.preview(PreviewMatrixEditorLlcrCrPublicationCommand(
            draft=command.draft, matrix_has_pending_changes=command.matrix_has_pending_changes,
        ))
        if current.preview_token != command.preview_token:
            raise ValueError("LLCR/CR publication target or Matrix changed after preview; preview again.")
        if current.mode != "official" or current.status not in {"ready", "conflict"} or current.target_path is None:
            raise ValueError("LLCR/CR official form is not ready for publication.")
        if current.existing_file and command.conflict_action != "archive":
            raise ValueError("Existing LLCR/CR form requires explicit archive approval.")
        if not current.existing_file and command.conflict_action != "none":
            raise ValueError("Archive was requested, but no existing LLCR/CR form remains.")
        return current

    @staticmethod
    def _request_signature(command: PublishMatrixEditorLlcrCrPublicationCommand) -> str:
        return fingerprint({"draft": asdict(command.draft),
                            "matrix_has_pending_changes": command.matrix_has_pending_changes})

    def _write_and_recover(self, state, command, current, workspace, projection):
        assert current.target_path is not None
        with TemporaryDirectory(dir=self._staging_root) as directory:
            source = Path(directory) / f"{command.draft.record_type}.xlsx"
            self._writer.write(output_path=source, projection=projection)
            record = self._output_command(command, projection, source, current, state, workspace)
            self._publisher(state).publish(command.draft.record_type, source, current.target_path,
                                           current.target_facts, record)
        return self._recover(state, command)

    def _recover(self, state: dict, command: PublishMatrixEditorLlcrCrPublicationCommand) -> MatrixEditorLlcrCrPublicationResult:
        if state["context"] != command.preview_token:
            raise ValueError("Contact form recovery token does not match the pending operation.")
        if state.get("request_signature") != self._request_signature(command):
            raise ValueError("Contact form recovery request differs from the original reviewed draft.")
        effect = state["effects"].get(f"llcr_cr_records:{command.draft.record_type}")
        if effect is None:
            raise ValueError("Contact form publication has no durable stage; manual recovery is required.")
        publisher = self._publisher(state)
        publisher.recover(self._register_once)
        if self._commit is not None:
            self._commit()
        if "llcr_cr_records" not in state["completed_steps"]:
            state["completed_steps"].append("llcr_cr_records")
        state["status"] = "completed"
        self._journal.save(state)
        publisher.verify_completed()
        archive = Path(effect["archive"]) if effect["prior"] is not None else None
        target = Path(effect["target"])
        return MatrixEditorLlcrCrPublicationResult(
            project_id=state["project_id"], file_name=target.name,
            target_path=target, archive_path=archive,
        )

    def _publisher(self, state: dict) -> RecoverableContactRecordPublisher:
        facts = state["authority"]
        workspace = Path(facts["workspace_path"])
        return RecoverableContactRecordPublisher(
            self._journal, state, workspace, lambda: self._verify_authority(state),
        )

    @staticmethod
    def _authority_facts(workspace, projection) -> dict:
        manifest = Path(workspace.manifest_path) if hasattr(workspace, "manifest_path") else None
        return {
            "workspace_path": str(workspace.local_workspace_path),
            "workspace_identity": file_identity(Path(workspace.local_workspace_path)),
            "official_path": str(workspace.official_folder_path),
            "official_identity": file_identity(Path(workspace.official_folder_path)),
            "project_id": workspace.project_id,
            "matrix_id": projection.confirmed_matrix_id,
            "matrix_revision": projection.confirmed_revision,
            "projection_fingerprint": projection.preview_fingerprint,
            "record_type": projection.record_type,
            "manifest_path": str(manifest) if manifest else None,
            "manifest_identity": file_identity(manifest) if manifest else None,
            "manifest_sha": file_hash(manifest) if manifest else None,
        }

    def _verify_authority(self, state: dict) -> None:
        facts = state["authority"]
        workspace = self._workspaces.get_by_project(state["project_id"])
        if (workspace is None or not self._workspace_verifier(workspace)
                or workspace.project_id != facts["project_id"]
                or str(workspace.local_workspace_path) != facts["workspace_path"]
                or str(workspace.official_folder_path) != facts["official_path"]
                or file_identity(Path(workspace.local_workspace_path)) != facts["workspace_identity"]
                or file_identity(Path(workspace.official_folder_path)) != facts["official_identity"]
                or (facts["manifest_path"] is not None and (
                    not hasattr(workspace, "manifest_path")
                    or str(workspace.manifest_path) != facts["manifest_path"]
                    or file_identity(Path(workspace.manifest_path)) != facts["manifest_identity"]
                    or file_hash(Path(workspace.manifest_path)) != facts["manifest_sha"]
                ))):
            raise ValueError("Official workspace identity changed; contact form publication stopped.")
        projection = self._preview_service.preview(state["project_id"], facts["record_type"])
        if (projection.confirmed_matrix_id != facts["matrix_id"]
                or projection.confirmed_revision != facts["matrix_revision"]
                or projection.preview_fingerprint != facts["projection_fingerprint"]):
            raise ValueError("Confirmed Matrix contact form changed; publication stopped.")

    def _output_command(self, command, projection, source, current, state, workspace):
        target = current.target_path
        assert target is not None
        summary = self._outputs.get_status_summary(command.draft.project_id)
        archive = (Path(workspace.local_workspace_path) / "History" / "Test results"
                   / f"{target.stem} {state['operation_id']}{target.suffix}")
        return RegisterProjectOutputCommand(
            project_id=command.draft.project_id,
            output_kind=(ProjectOutputKind.LLCR_RECORD_FORM if command.draft.record_type == "llcr"
                         else ProjectOutputKind.CR_RECORD_FORM),
            status=ProjectOutputStatus.CURRENT,
            source=ProjectOutputSource.SYSTEM_GENERATED,
            output_path=str(target), draft_id=summary.active_draft_id,
            output_sha256=file_hash(source), output_size_bytes=source.stat().st_size,
            source_context_signature=(f"contact-record:{command.draft.record_type}|matrix:"
                                      f"{projection.confirmed_matrix_id}@{projection.confirmed_revision}|"
                                      f"{projection.preview_fingerprint}"),
            note=(f"Previous form preserved at {archive}; sha256={current.target_facts['sha']}."
                  if current.target_facts is not None else None),
        )

    def _register_once(self, payload: dict) -> None:
        data = dict(payload)
        data["output_kind"] = ProjectOutputKind(data["output_kind"])
        data["status"] = ProjectOutputStatus(data["status"])
        data["source"] = ProjectOutputSource(data["source"])
        command = RegisterProjectOutputCommand(**data)
        for record in self._outputs.list_records(command.project_id):
            if all(getattr(record, key) == getattr(command, key) for key in (
                "output_kind", "output_path", "source", "status", "draft_id",
                "output_sha256", "output_size_bytes", "source_context_signature",
            )):
                return
        self._outputs.register_output(command)


def _sample_notes_match(draft, snapshot) -> bool:
    return tuple((group.sample_note or "").strip() for group in draft.groups) == tuple(
        (group.sample_note or "").strip() for group in snapshot.groups
    )
