"""Reviewed relocation of one project's mutable official-folder display name."""

from __future__ import annotations

from dataclasses import dataclass, replace
import os
from pathlib import Path

from backend.application.official_project_workspace_service import (
    OfficialProjectWorkspaceService,
    OfficialWorkspaceCreateError,
    OfficialWorkspaceCreateResult,
    OfficialWorkspaceRecord,
    OfficialWorkspaceRepositoryPort,
)
from backend.infrastructure.files.generation_journal import GenerationJournal, fingerprint
from backend.infrastructure.files.recoverable_output_publisher import file_hash, file_identity
from backend.infrastructure.official_workspace_manifest import (
    OfficialWorkspaceManifest,
    OfficialWorkspaceManifestGateway,
    stable_folder_identity,
)


@dataclass(frozen=True, slots=True)
class OfficialFolderRelocationOption:
    key: str
    label: str
    description: str


@dataclass(frozen=True, slots=True)
class OfficialFolderRelocationPreview:
    status: str
    current_path: Path | None
    suggested_path: Path | None
    candidate_path: Path | None
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    expected_context: str | None
    actions: tuple[OfficialFolderRelocationOption, ...]


_RENAME = OfficialFolderRelocationOption(
    "rename_to_confirmed", "Use confirmed name",
    "Move the existing folder in place and update its indexed paths.",
)
_RELINK_RENAME = OfficialFolderRelocationOption(
    "rebind_and_rename", "Use confirmed name",
    "Relink the unique same-project folder, then use the confirmed name.",
)
_RELINK_CUSTOM = OfficialFolderRelocationOption(
    "rebind_keep_custom", "Keep custom name",
    "Relink the unique same-project folder without renaming it.",
)
_KEEP_CURRENT = OfficialFolderRelocationOption(
    "keep_current_name", "Keep current name",
    "Retain the verified folder name for this confirmed Basic Information version.",
)


class OfficialFolderRelocationService:
    """Keep folder display names mutable without weakening project identity."""

    def __init__(
        self,
        *,
        workspace_service: OfficialProjectWorkspaceService,
        workspace_repository: OfficialWorkspaceRepositoryPort,
        journal: GenerationJournal,
        manifest_gateway: OfficialWorkspaceManifestGateway | None = None,
    ) -> None:
        self._workspaces = workspace_service
        self._repository = workspace_repository
        self._journal = journal
        self._manifests = manifest_gateway or OfficialWorkspaceManifestGateway()

    def preview(self, project_id: str) -> OfficialFolderRelocationPreview:
        """Return one explicit, identity-checked action or a review blocker."""
        operation = self._journal.read(project_id)
        if operation and operation["status"] != "completed":
            effect = operation.get("effects", {}).get("relocation", {})
            if not effect:
                return OfficialFolderRelocationPreview(
                    "interrupted", None, None, None, (),
                    ("An earlier relocation stopped before any folder move; resume to clear it.",),
                    operation["context"],
                    (OfficialFolderRelocationOption("resume", "Clear interrupted attempt",
                        "No folder move was recorded; finish the empty attempt."),),
                )
            return OfficialFolderRelocationPreview(
                status="interrupted", current_path=Path(effect["source"]) if effect else None,
                suggested_path=Path(effect["target"]) if effect else None,
                candidate_path=None, blockers=(),
                warnings=("An earlier folder relocation needs recovery before another action.",),
                expected_context=operation["context"],
                actions=(OfficialFolderRelocationOption("resume", "Resume relocation",
                        "Verify the saved folder move and finish its identity and index updates."),),
            )
        workspace = self._workspaces.preview(project_id)
        record = self._repository.get_by_project(project_id)
        suggested = workspace.suggested_folder_path
        current = record.official_folder_path if record else workspace.official_folder_path
        if (workspace.status == "inconsistent" and record is not None
                and suggested is not None and not current.exists()):
            return self._preview_manual_relink(record, suggested, workspace.warnings)
        if workspace.status != "completed" or record is None or suggested is None:
            return OfficialFolderRelocationPreview(
                "blocked" if workspace.blockers else "not_needed", current, suggested, None,
                workspace.blockers, workspace.warnings, None, (),
            )
        if current == suggested:
            return OfficialFolderRelocationPreview(
                "not_needed", current, suggested, None, (), workspace.warnings, None, (),
            )
        try:
            manifest_payload = self._manifests.read(record.manifest_path)
        except (OSError, ValueError):
            manifest_payload = None
        if (isinstance(manifest_payload, dict)
                and manifest_payload.get("project_id") == record.project_id
                and manifest_payload.get("dl_number") == record.dl_number
                and manifest_payload.get("official_project_folder_path") == str(current)
                and manifest_payload.get("retained_confirmed_folder_name") == suggested.name):
            return OfficialFolderRelocationPreview(
                "not_needed", current, suggested, None, (), workspace.warnings, None, (),
            )
        workspace_path = record.local_workspace_path
        try:
            children = sorted(
                child for child in workspace_path.iterdir()
                if child.name.startswith(f"{record.dl_number} ")
            )
        except OSError as exc:
            raise OfficialWorkspaceCreateError("Cannot inspect the LTR workspace for folder relocation.") from exc
        if (children != [current] or suggested.exists() or suggested.is_symlink()
                or self._manifests.first_redirected_path(
                    workspace_path, current, suggested, record.manifest_path
                ) is not None):
            return OfficialFolderRelocationPreview(
                "blocked", current, suggested, None,
                ("The LTR workspace has multiple, redirected, or conflicting active folders; review manually.",),
                workspace.warnings, None, (),
            )
        token = fingerprint({
            "project_id": project_id,
            "source": str(current), "target": str(suggested),
            "directory_identity": file_identity(current),
            "manifest_hash": file_hash(record.manifest_path),
            "active_children": [child.name for child in children],
        })
        return OfficialFolderRelocationPreview(
            "rename_available", current, suggested, None, (), workspace.warnings,
            token, (_RENAME, _KEEP_CURRENT),
        )

    def abandon_unmoved_for_rebuild(self, project_id: str, expected_source: Path) -> None:
        """Retire only an unexecuted rename after a separate archive/rebuild is approved."""
        with self._journal.lock(project_id):
            operation = self._journal.read(project_id)
            if operation is None or operation["status"] == "completed":
                return
            if operation.get("strategy") not in {
                "rename_to_confirmed", "keep_current_name", "rebind_and_rename", "rebind_keep_custom",
            }:
                raise OfficialWorkspaceCreateError("Unknown folder relocation needs manual recovery.")
            effect = operation.get("effects", {}).get("relocation")
            if set(operation.get("effects", {})) - {"relocation"}:
                raise OfficialWorkspaceCreateError("Folder relocation has other effects; resume recovery first.")
            if effect and (effect.get("moved") or effect.get("manifest_updated")):
                raise OfficialWorkspaceCreateError("Folder relocation already recorded a move; resume recovery first.")
            record = self._repository.get_by_project(project_id)
            preview = self._workspaces.preview(project_id)
            if (record is None or preview.status != "completed"
                    or record.official_folder_path != expected_source
                    or expected_source.parent != record.local_workspace_path
                    or not expected_source.name.startswith(f"{record.dl_number} ")
                    or self._manifests.first_redirected_path(
                        record.local_workspace_path, record.source_book_path,
                        expected_source, record.manifest_path,
                    ) is not None):
                raise OfficialWorkspaceCreateError("Current official folder identity needs review before rebuild.")
            try:
                manifest = self._manifests.read(record.manifest_path)
                active = [child for child in record.local_workspace_path.iterdir()
                          if child.name.startswith(f"{record.dl_number} ")]
            except (OSError, ValueError) as exc:
                raise OfficialWorkspaceCreateError("Cannot verify the current official folder before rebuild.") from exc
            identity = file_identity(expected_source)
            if (active != [expected_source] or not isinstance(manifest, dict)
                    or manifest.get("project_id") != project_id
                    or manifest.get("dl_number") != record.dl_number
                    or manifest.get("official_project_folder_path") != str(expected_source)
                    or manifest.get("official_folder_identity") not in (None, identity)):
                raise OfficialWorkspaceCreateError("Current official folder identity changed; review before rebuild.")
            if effect:
                saved = effect.get("record")
                if (not isinstance(saved, dict)
                        or saved.get("project_id") != record.project_id
                        or saved.get("dl_number") != record.dl_number
                        or saved.get("official_folder_path") != str(expected_source)
                        or saved.get("local_workspace_path") != str(record.local_workspace_path)
                        or effect.get("source") != str(expected_source)
                        or effect.get("directory_identity") != identity):
                    raise OfficialWorkspaceCreateError("Saved folder relocation identity changed; resume recovery first.")
                target = Path(effect["target"])
                if (target.parent != record.local_workspace_path
                        or not target.name.startswith(f"{record.dl_number} ")
                        or target != expected_source and os.path.lexists(target)):
                    raise OfficialWorkspaceCreateError("Saved folder move target changed; resume recovery first.")
            operation.update(status="completed", message="Unmoved relocation superseded by a reviewed archive/rebuild.")
            self._journal.save(operation)

    def _preview_manual_relink(
        self, record: OfficialWorkspaceRecord, suggested: Path,
        warnings: tuple[str, ...],
    ) -> OfficialFolderRelocationPreview:
        workspace, manifest_path = record.local_workspace_path, record.manifest_path
        blocker = "The manually renamed folder cannot be uniquely verified as this project."
        try:
            payload = self._manifests.read(manifest_path)
            children = sorted(
                child for child in workspace.iterdir()
                if child.name.startswith(f"{record.dl_number} ")
            )
        except (OSError, ValueError):
            payload, children = None, []
        if (
            not isinstance(payload, dict)
            or payload.get("project_id") != record.project_id
            or payload.get("dl_number") != record.dl_number
            or payload.get("official_project_folder_path") != str(record.official_folder_path)
            or record.official_folder_path.parent != workspace
            or record.source_book_path != workspace / "Source Book"
            or record.manifest_path != workspace / ".connlab" / "manifest.json"
            or not record.source_book_path.is_dir()
            or len(children) != 1
            or not children[0].is_dir()
            or children[0] == record.official_folder_path
            or self._manifests.first_redirected_path(
                workspace, record.source_book_path, children[0], manifest_path,
            ) is not None
            or suggested.exists() and suggested != children[0]
        ):
            return OfficialFolderRelocationPreview(
                "blocked", record.official_folder_path, suggested, None,
                (blocker,), warnings, None, (),
            )
        candidate = children[0]
        try:
            candidate_identity = stable_folder_identity(candidate)
        except OSError:
            candidate_identity = None
        if candidate_identity is None or payload.get("official_folder_identity") != candidate_identity:
            return OfficialFolderRelocationPreview(
                "blocked", record.official_folder_path, suggested, candidate,
                ("Manual folder relink needs a matching registered filesystem identity; legacy or replaced folders require operator review.",),
                warnings, None, (),
            )
        token = fingerprint({
            "project_id": record.project_id, "recorded": str(record.official_folder_path),
            "source": str(candidate), "target": str(suggested),
            "directory_identity": file_identity(candidate),
            "manifest_hash": file_hash(manifest_path),
            "active_children": [candidate.name],
        })
        return OfficialFolderRelocationPreview(
            "manual_relink_available", record.official_folder_path, suggested,
            candidate, (), warnings, token, (_RELINK_RENAME, _RELINK_CUSTOM),
        )

    def apply(
        self, project_id: str, action: str, expected_context: str
    ) -> OfficialWorkspaceCreateResult:
        """Resume a reviewed move; never claim a folder merely from its display name."""
        with self._journal.lock(project_id):
            self._workspaces.require_write_allowed(project_id)
            operation = self._journal.read(project_id)
            if operation and operation["status"] != "completed":
                if action != "resume" or expected_context != operation["context"]:
                    raise OfficialWorkspaceCreateError("Resume the previous folder relocation first.")
            else:
                preview = self.preview(project_id)
                allowed = {option.key for option in preview.actions}
                if action not in allowed or expected_context != preview.expected_context:
                    raise OfficialWorkspaceCreateError("Folder relocation preview changed. Review again.")
                assert preview.current_path is not None and preview.suggested_path is not None
                record = self._repository.get_by_project(project_id)
                if record is None:
                    raise OfficialWorkspaceCreateError("Official workspace index is missing.")
                source = preview.candidate_path or preview.current_path
                target = (
                    source if action in {"rebind_keep_custom", "keep_current_name"}
                    else preview.suggested_path
                )
                directory_identity = file_identity(source)
                operation = self._journal.create(project_id, action, expected_context)
                operation["effects"]["relocation"] = {
                    "source": str(source),
                    "target": str(target),
                    "suggested": str(preview.suggested_path),
                    "directory_identity": directory_identity,
                    "record": record,
                }
                self._journal.save(operation)
            if not operation.get("effects", {}).get("relocation"):
                record = self._repository.get_by_project(project_id)
                if record is None:
                    raise OfficialWorkspaceCreateError("Official workspace index is missing.")
                operation["status"] = "completed"
                self._journal.save(operation)
                return OfficialWorkspaceCreateResult(record, (), ("No folder move was recorded.",))
            return self._recover(operation)

    def _recover(self, operation: dict) -> OfficialWorkspaceCreateResult:
        effect = operation["effects"]["relocation"]
        source, target = Path(effect["source"]), Path(effect["target"])
        record_payload = effect["record"]
        if isinstance(record_payload, dict):
            record = OfficialWorkspaceRecord(**{
                **record_payload,
                **{key: Path(record_payload[key]) for key in (
                    "local_workspace_path", "source_book_path", "official_folder_path",
                    "manifest_path", "template_source_path",
                )},
            })
        else:
            record = record_payload
        if (source.parent != target.parent
                or record.official_folder_path.parent != source.parent
                or not source.name.startswith(f"{record.dl_number} ")
                or not target.name.startswith(f"{record.dl_number} ")):
            raise OfficialWorkspaceCreateError("Relocation journal does not match the indexed LTR folder.")
        if source != target and source.is_dir():
            _require_relocation_path_capacity(source, target)
        if source.is_dir():
            self._repository.preflight_placed_materials(record, source=source)
        updated = replace(record, official_folder_path=target)
        self._manifests.move_and_write_relocation(
            record.manifest_path, source=source, target=target,
            old_folder_path=record.official_folder_path,
            expected_identity=effect["directory_identity"],
            manifest=OfficialWorkspaceManifest(
                schema_version=1, project_id=record.project_id, dl_number=record.dl_number,
                local_workspace_path=str(record.local_workspace_path),
                source_book_path=str(record.source_book_path),
                official_project_folder_path=str(target),
                template_source_path=str(record.template_source_path),
                created_at=record.created_at,
                official_folder_identity=effect["directory_identity"],
                retained_confirmed_folder_name=(
                    Path(effect["suggested"]).name
                    if operation["strategy"] in {"rebind_keep_custom", "keep_current_name"}
                    else None
                ),
            ),
        )
        effect["moved"] = True
        self._journal.save(operation)
        effect["manifest_updated"] = True
        self._journal.save(operation)
        saved = self._repository.publish_relocation(
            updated, source=record.official_folder_path, target=target,
            operation_id=operation["operation_id"],
            expected_identity=effect["directory_identity"],
        )
        operation["status"] = "completed"
        self._journal.save(operation)
        return OfficialWorkspaceCreateResult(saved, (target,), ())


def _require_relocation_path_capacity(source: Path, target: Path) -> None:
    """Reject a destination tree unusable by legacy Win32 APIs before any move."""
    if os.name != "nt":
        return
    message = (
        "Official folder relocation path is too long for portable Windows access. "
        "Choose a shorter project save location or confirmed description."
    )
    if len(str(target)) >= 248:
        raise OfficialWorkspaceCreateError(message)
    try:
        for item in source.rglob("*"):
            destination = target / item.relative_to(source)
            if len(str(destination)) >= (248 if item.is_dir() else 260):
                raise OfficialWorkspaceCreateError(message)
    except OSError as exc:
        raise OfficialWorkspaceCreateError(
            "Cannot verify every relocated path before moving the official folder."
        ) from exc
