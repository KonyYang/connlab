"""Confirmed full-LTR public directory associations, independent of file sync."""

import json
from dataclasses import replace
from pathlib import Path
from uuid import uuid4
from datetime import UTC, datetime

from backend.infrastructure.files.generation_journal import fingerprint
from backend.infrastructure.files.recoverable_output_publisher import file_identity, require_safe_output_path
from backend.modules.ltr import parse_ltr_number


class PublicFolderBinding:
    def __init__(self, *, repository, workspaces, year_resolver, path_resolver, public_root, commit):
        self.repository, self.workspaces = repository, workspaces
        self.years, self.paths, self.root, self.commit = year_resolver, path_resolver, public_root, commit

    def _inputs(self, project_id):
        workspace = self.workspaces.get_by_project(project_id)
        if workspace is None:
            raise ValueError("Create the local project folder before choosing its public folder.")
        number = parse_ltr_number(workspace.dl_number).normalized
        year = self.years.resolve(project_id)
        if year.blockers:
            raise ValueError(year.blockers[0])
        paths = self.paths.resolve(public_root=self.root, year=year.year,
            project_folder_name=workspace.official_folder_path.name, check_open=False, check_closed=False)
        require_safe_output_path(paths.public_root)
        return workspace, number, paths

    @staticmethod
    def _read(state):
        if not state.binding_json:
            return None
        try:
            value = json.loads(state.binding_json)
            if (not isinstance(value, dict) or value.get("version") != 1
                    or value.get("location") not in {"open", "closed"}
                    or not isinstance(value.get("path"), str)
                    or not isinstance(value.get("identity"), list) or len(value["identity"]) != 2
                    or not all(isinstance(i, int) for i in value["identity"])
                    or (value.get("pending_submit") is not None and not isinstance(value["pending_submit"], dict))):
                raise ValueError()
            return value
        except (TypeError, KeyError, ValueError) as exc:
            raise ValueError("Saved public folder association is unreadable. Review it before syncing.") from exc

    @staticmethod
    def _number(path):
        try:
            return parse_ltr_number(path.name.split(maxsplit=1)[0]).normalized
        except (ValueError, IndexError):
            return None

    @staticmethod
    def _require_year(year):
        for path in (year.parent, year):
            require_safe_output_path(path)
            if not path.is_dir():
                raise ValueError(f"Required public directory is missing or not a folder: {path}. Check or create it manually.")

    def verified(self, project_id, paths):
        state = self.repository.get_state(project_id)
        binding = self._read(state)
        if binding is None:
            raise ValueError("Choose and confirm the public project folder before syncing.")
        if binding.get("requires_review"):
            raise ValueError("Imported public folder association requires confirmation on this installation.")
        workspace = self.workspaces.get_by_project(project_id)
        number = parse_ltr_number(workspace.dl_number).normalized
        path = Path(binding["path"])
        parent = paths.closed_year_path if binding["location"] == "closed" else paths.open_year_path
        if (binding.get("project_id") != project_id or binding.get("full_ltr_number") != number
                or binding.get("root") != str(paths.public_root) or binding.get("year") != paths.year
                or path.parent != parent or self._number(path) != number):
            raise ValueError("Public folder settings or project identity changed. Review the public folder association.")
        if binding.get("pending_submit") and self.pending_moved(project_id, paths=paths):
            return replace(paths, project_folder_name=path.name,
                           public_open_path=paths.open_year_path / path.name,
                           public_closed_path=paths.closed_year_path / path.name)
        self._require_year(parent)
        require_safe_output_path(path)
        if (not path.is_dir() or file_identity(path) != binding["identity"]
                or file_identity(parent) != binding.get("year_identity")):
            raise ValueError("The associated public folder is missing or changed. Review its association.")
        return replace(paths, project_folder_name=path.name,
                       public_open_path=paths.open_year_path / path.name,
                       public_closed_path=paths.closed_year_path / path.name)

    def preview(self, project_id):
        result = dict(project_id=project_id, status="review_required", public_folder_year=None,
                      full_ltr_number=None, current_path=None, proposed_path=None,
                      candidates=[], can_create=False, blockers=[])
        try:
            workspace, number, paths = self._inputs(project_id)
            result.update(public_folder_year=paths.year, full_ltr_number=number,
                          proposed_path=str(paths.public_open_path))
            state = self.repository.get_state(project_id)
            saved = None
            try:
                saved = self._read(state)
                if saved:
                    result["current_path"] = saved["path"]
                    verified = self.verified(project_id, paths)
                    current = str(verified.public_closed_path) if self.pending_moved(project_id, paths=paths) else saved["path"]
                    result.update(status="bound", current_path=current, proposed_path=str(verified.public_open_path))
                    return {**result, "expected_context": fingerprint(result)}
            except ValueError:
                # Discovery is evidence for a new explicit review, never silent repair.
                pass
            if saved and saved.get("pending_submit"):
                raise ValueError("An approval move needs recovery. Retain both public locations and resume Submit before uploading.")
            if state.sync_locked:
                raise ValueError("Sync is locked after Submit. Review the retained Closed folder association before further work.")
            self._require_year(paths.open_year_path)
            result["year_identity"] = file_identity(paths.open_year_path)
            # Do not use exists()/glob() to treat an inaccessible share as an empty result.
            for path in sorted(paths.open_year_path.iterdir(), key=lambda item: item.name.casefold()):
                path.stat(follow_symlinks=False)
                if self._number(path) != number:
                    continue
                require_safe_output_path(path)
                if not path.is_dir():
                    raise ValueError(f"Same-LTR public path is not a directory: {path}")
                identity = file_identity(path)
                result["candidates"].append({"candidate_id": fingerprint([str(path), identity]),
                                             "path": str(path), "identity": identity})
            result["can_create"] = not result["candidates"]
        except (OSError, ValueError) as exc:
            result.update(status="blocked", can_create=False, candidates=[], blockers=[str(exc)])
        return {**result, "expected_context": fingerprint(result)}

    def confirm(self, project_id, expected_context, candidate_id):
        preview = self.preview(project_id)
        if preview["expected_context"] != expected_context or preview["status"] != "review_required":
            raise ValueError("Public folder choices changed. Review them again before confirming.")
        _, number, paths = self._inputs(project_id)
        self._require_year(paths.open_year_path)
        if file_identity(paths.open_year_path) != preview["year_identity"]:
            raise ValueError("The public year directory changed. Review the destination again.")
        if candidate_id == "create" and preview["can_create"]:
            target = paths.public_open_path
            require_safe_output_path(target)
            # A failed database commit retains this folder for explicit candidate review.
            target.mkdir(exist_ok=False)
            identity = file_identity(target)
        else:
            choice = next((item for item in preview["candidates"] if item["candidate_id"] == candidate_id), None)
            if choice is None:
                raise ValueError("Select a reviewed public project folder.")
            target, identity = Path(choice["path"]), choice["identity"]
        require_safe_output_path(target)
        if not target.is_dir() or file_identity(target) != identity:
            raise ValueError("The selected public directory changed before confirmation.")
        state = self.repository.get_state(project_id)
        try:
            previous = self._read(state)
        except ValueError:
            previous = None
        binding = dict(version=1, project_id=project_id, full_ltr_number=number,
                       root=str(paths.public_root), year=paths.year, location="open", path=str(target),
                       identity=identity, year_identity=file_identity(paths.open_year_path))
        if (previous and previous.get("project_id") == project_id
                and previous.get("full_ltr_number") == number and previous.get("identity") == identity
                and previous.get("path") != str(target)):
            self.repository.rebase_files(project_id=project_id, old_root=Path(previous["path"]),
                new_root=target, operation_id=uuid4().hex, updated_at=datetime.now(UTC).isoformat())
        self.repository.save_state(replace(state, binding_json=json.dumps(binding, ensure_ascii=False)))
        self.commit()  # Must complete before returning authority for any later file copy.
        return self.preview(project_id)

    def after_submit(self, project_id, closed_path):
        state = self.repository.get_state(project_id)
        binding = self._read(state)
        if binding is None:
            raise ValueError("Public folder association is missing after Submit.")
        binding.update(location="closed", path=str(closed_path), identity=file_identity(closed_path),
                       year_identity=file_identity(closed_path.parent))
        binding.pop("pending_submit", None)
        return json.dumps(binding, ensure_ascii=False)

    def pending_moved(self, project_id, *, paths=None):
        binding = self._read(self.repository.get_state(project_id))
        if not binding or not binding.get("pending_submit"):
            return False
        if paths is None:
            _, _, paths = self._inputs(project_id)
        intent = binding["pending_submit"]
        source = Path(binding["path"])
        target = paths.closed_year_path / source.name
        if (binding.get("root") != str(paths.public_root) or binding.get("year") != paths.year
                or intent.get("target") != str(target)):
            raise ValueError("Pending approval destination changed; retain files and review recovery.")
        self._require_year(paths.closed_year_path)
        if file_identity(paths.closed_year_path) != intent.get("year_identity"):
            raise ValueError("Pending approval year directory changed; review recovery.")
        require_safe_output_path(source)
        require_safe_output_path(target)
        if target.exists():
            if source.exists() or not target.is_dir() or file_identity(target) != binding["identity"]:
                raise ValueError("Pending approval folder identity changed; review recovery.")
            return True
        if not source.is_dir() or file_identity(source) != binding["identity"]:
            raise ValueError("Pending approval source is missing or changed; review recovery.")
        return False

    def prepare_submit(self, project_id, closed_path):
        _, _, paths = self._inputs(project_id)
        resolved = self.verified(project_id, paths)
        if resolved.public_closed_path != closed_path:
            raise ValueError("Approval target changed before moving the folder.")
        self._require_year(paths.closed_year_path)
        state = self.repository.get_state(project_id)
        binding = self._read(state)
        if binding is None or binding["location"] != "open":
            raise ValueError("A confirmed Open folder association is required before Submit.")
        binding["pending_submit"] = {"target": str(closed_path), "year_identity": file_identity(paths.closed_year_path)}
        self.repository.save_state(replace(state, binding_json=json.dumps(binding, ensure_ascii=False)))
        self.commit()
