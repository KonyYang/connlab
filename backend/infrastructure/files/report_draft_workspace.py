"""Immutable report working copies, independent of project report authority."""
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import shutil
import time
import logging
from uuid import uuid4

from backend.application.current_report_update_service import CurrentReportArtifact

_OWNER = "connlab-report-working-draft-v1"
_LOGGER = logging.getLogger(__name__)


def _fingerprint(path):
    with path.open("rb") as stream:
        from hashlib import file_digest
        return file_digest(stream, "sha256").hexdigest()


def _safe_path(path):
    if any(item.is_symlink() or (item.exists() and getattr(item.stat(), "st_file_attributes", 0) & 0x400)
           for item in (path, *path.parents)):
        raise ValueError("The report working copy is redirected. Select the Internal Report again.")


class ReportDraftWorkspace:
    def __init__(self, root: Path, *, clock=time.time, retention_seconds=24 * 60 * 60):
        self._root = Path(root).absolute()
        self._clock = clock
        self._retention = retention_seconds

    def _project(self, project_id):
        path = self._root / sha256(project_id.encode("utf-8")).hexdigest()
        _safe_path(path)
        return path

    def latest(self, project_id, dl_number):
        pointer = self._project(project_id) / "current.json"
        if not pointer.exists():
            return None
        _safe_path(pointer)
        try:
            data = json.loads(pointer.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("Invalid draft pointer")
            revision = data["revision"]
            _, metadata = self._record(project_id, revision)
            if metadata["expires_at"] <= self._clock() or metadata["dl_number"].casefold() != dl_number.casefold():
                return None
            return self.read_revision(project_id, revision)
        except (KeyError, OSError, ValueError) as exc:
            raise ValueError("The latest working draft is unavailable. Select the Internal Report again.") from exc

    def _record(self, project_id, revision):
        if not isinstance(revision, str) or not re.fullmatch(r"[a-f0-9]{32}", revision):
            raise ValueError("The draft download is unavailable. Select the Internal Report again.")
        folder = self._project(project_id) / revision
        _safe_path(folder)
        record = folder / "revision.json"
        _safe_path(record)
        metadata = json.loads(record.read_text(encoding="utf-8"))
        if (not isinstance(metadata, dict) or metadata.get("owner") != _OWNER
                or metadata.get("project_id") != project_id
                or not all(isinstance(metadata.get(key), str) for key in ("file_name", "dl_number", "sha256"))
                or not isinstance(metadata.get("expires_at"), (int, float))):
            raise ValueError("The working draft metadata is unavailable. Select the Internal Report again.")
        name = metadata["file_name"]
        if (metadata["project_id"] != project_id or not isinstance(name, str)
                or Path(name).name != name or not name.lower().endswith(".docx")):
            raise ValueError("The draft download does not belong to this project.")
        return folder, metadata

    def read_revision(self, project_id, revision):
        folder, metadata = self._record(project_id, revision)
        if metadata["expires_at"] <= self._clock():
            raise ValueError("The draft download expired. Select the report and update again.")
        name = metadata["file_name"]
        path = folder / name
        _safe_path(path)
        fingerprint = _fingerprint(path)
        if fingerprint != metadata["sha256"]:
            raise ValueError("The working draft changed. Select the Internal Report again.")
        return CurrentReportArtifact("ready", "download_draft", name, path, fingerprint, None,
                                     report_revision_id=revision, confirmed_matrix_id=metadata.get("matrix_id"),
                                     folder_path=folder)

    def _prune(self, project_id, keep):
        project = self._project(project_id)
        if not project.is_dir():
            return
        for folder in project.iterdir():
            if folder == keep or not re.fullmatch(r"[a-f0-9]{32}", folder.name) or not folder.is_dir():
                continue
            try:
                checked, metadata = self._record(project_id, folder.name)
                if metadata["expires_at"] <= self._clock() and checked.resolve().parent == project.resolve():
                    shutil.rmtree(checked)
            except (OSError, ValueError):
                _LOGGER.debug("Retaining an unavailable report cache revision %s", folder.name, exc_info=True)

    def update(self, project_id, dl_number, source, generate, revalidate, *, matrix_id=None):
        source = Path(source)
        _safe_path(source)
        before = _fingerprint(source)
        project = self._project(project_id)
        self._prune(project_id, source.parent)
        revision = uuid4().hex
        folder = project / revision
        folder.mkdir(parents=True, exist_ok=False)
        name = re.sub(r"(?:[ _-]draft)?(?: \(\d+\))?$", "", source.stem, flags=re.IGNORECASE).rstrip()
        if not name.casefold().startswith(dl_number.casefold() + " "):
            name = dl_number + " Internal Report"
        output = folder / (name + "_Draft.docx")
        try:
            generate(source, output)
            _safe_path(output)
            if not output.is_file() or not output.stat().st_size:
                raise ValueError("The updated draft could not be prepared. Retry the update.")
            if _fingerprint(source) != before:
                raise ValueError("The source report changed during the update. Try again.")
            revalidate()
            previous_selection = source.parent / "EquipmentID.docx"
            selection = folder / "EquipmentID.docx"
            if source.parent.parent == project and previous_selection.is_file() and not selection.exists():
                _safe_path(previous_selection)
                shutil.copy2(previous_selection, selection)
            metadata = {"owner": _OWNER, "project_id": project_id, "dl_number": dl_number, "file_name": output.name,
                        "sha256": _fingerprint(output), "matrix_id": matrix_id,
                        "expires_at": self._clock() + self._retention}
            (folder / "revision.json").write_text(json.dumps(metadata), encoding="utf-8")
            result = self.read_revision(project_id, revision)
            pointer = project / (revision + ".json")
            try:
                pointer.write_text(json.dumps({"revision": revision}), encoding="utf-8")
                _safe_path(project / "current.json")
                os.replace(pointer, project / "current.json")
            finally:
                pointer.unlink(missing_ok=True)
            return result
        except Exception:
            # Only this newly created revision is disposable; previous revisions remain immutable.
            if folder.resolve().parent == project.resolve() and not folder.is_symlink():
                shutil.rmtree(folder)
            raise
