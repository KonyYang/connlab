"""Initialize missing browser-release templates without replacing site-owned files."""

from __future__ import annotations

import hashlib
import json
import os
import stat
import tempfile
from contextlib import ExitStack, contextmanager
from pathlib import Path, PureWindowsPath
from zipfile import BadZipFile, ZipFile

from backend.application.generation_template_names import matches_generation_template
from backend.application.official_project_workspace_service import REQUIRED_TEMPLATE_PATHS
from backend.infrastructure.files.recoverable_output_publisher import require_safe_output_path


_PURPOSES = {
    "internal_report": "Internal report",
    "customer_feedback": "Customer feedback",
    "customer_report": "Customer report",
    "ir_dwv": "IR/DWV record",
    "test_record": "Test record",
    "fee_evaluation": "Fee evaluation",
}


def _safe_relative(name: str) -> PureWindowsPath:
    path = PureWindowsPath(name)
    if not path.parts or path.anchor or ".." in path.parts or any(
        part.endswith((" ", ".")) or PureWindowsPath(part).is_reserved()
        or any(ch in part for ch in '<>:"|?*') for part in path.parts
    ):
        raise ValueError(f"Invalid relative path in template package: {name}")
    return path


def _read_bundle(bundle: Path):
    with ZipFile(bundle) as archive:
        manifest = json.loads(archive.read("manifest.json"))
        files = manifest["files"]
        if set(files) != set(_PURPOSES):
            raise ValueError("Package must include exactly the six generation template purposes.")
        templates = {}
        for purpose, spec in files.items():
            name = spec["name"]
            if _safe_relative(name).name != name or not matches_generation_template(Path(name), purpose):
                raise ValueError(f"Wrong filename for {purpose}: {name}")
            payload = archive.read(name)
            if hashlib.sha256(payload).hexdigest() != spec["sha256"]:
                raise ValueError(f"Template checksum differs: {name}")
            templates[purpose] = (name, payload)
        directories = [Path(*_safe_relative(n).parts) for n in manifest["directories"]]
    return templates, directories


def _check_folder(folder: Path, identity: os.stat_result) -> None:
    require_safe_output_path(folder)
    if not os.path.samestat(identity, folder.stat()):
        raise OSError(f"Registered template folder changed during initialization: {folder}")


@contextmanager
def _pinned_directory(folder: Path):
    """Keep Windows from renaming a destination ancestor between check and publication."""
    with ExitStack() as handles:
        if os.name == "nt":
            import pywintypes
            import win32con
            import win32file

            for parent in (*reversed(folder.parents), folder):
                if parent == parent.parent:
                    continue
                try:
                    handle = win32file.CreateFile(
                        str(parent), 0, win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,
                        None, win32con.OPEN_EXISTING,
                        win32con.FILE_FLAG_BACKUP_SEMANTICS | 0x00200000, None,  # OPEN_REPARSE_POINT
                    )
                except pywintypes.error as exc:
                    raise OSError(f"Cannot protect template directory {parent}: {exc.strerror}") from exc
                handles.callback(handle.Close)
                require_safe_output_path(parent)
        require_safe_output_path(folder)
        yield


def _install_missing(folder: Path, target: Path, payload: bytes, identity: os.stat_result) -> None:
    # Windows rename is no-clobber; on POSIX link atomically creates a new name.
    # A crash while writing leaves at most an ignored .tmp, never a partial Office document.
    _check_folder(folder, identity)
    stream = tempfile.NamedTemporaryFile(dir=folder, prefix=".connlab-seed-", suffix=".tmp", delete=False)
    stage = Path(stream.name)
    owned = os.fstat(stream.fileno())
    try:
        with stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        _check_folder(folder, identity)
        require_safe_output_path(stage)
        if not os.path.samestat(owned, stage.stat()):
            raise OSError(f"Staging file was replaced: {stage}")
        if os.name == "nt":
            os.rename(stage, target)
        else:
            os.link(stage, target)
    finally:
        _check_folder(folder, identity)
        if stage.exists() and os.path.samestat(owned, stage.lstat()):
            stage.unlink()


def _check_office_file(file: Path, purpose: str) -> None:
    require_safe_output_path(file)
    if not stat.S_ISREG(file.stat().st_mode):
        raise ValueError(f"Expected a regular template file: {file.name}")
    if purpose == "ir_dwv":
        from backend.infrastructure.office.ir_dwv_record_workbook_gateway import IrDwvRecordWorkbookGateway

        IrDwvRecordWorkbookGateway(file).template_fingerprint()
    else:
        # Check the primary OOXML part without Office automation or editing.
        part = "word/document.xml" if purpose in {"internal_report", "customer_report", "test_record"} else "xl/workbook.xml"
        with ZipFile(file) as document:
            document.read(part)


def _seed_file(folder: Path, purpose: str, name: str, data: bytes, identity: os.stat_result) -> None:
    def matches() -> list[Path]:
        return sorted(p for p in folder.iterdir() if matches_generation_template(p, purpose))

    candidates = matches()
    if not candidates:
        try:
            with _pinned_directory(folder):
                _install_missing(folder, folder / name, data, identity)
        except FileExistsError:
            pass  # A second start or the user published first. Inspect what actually exists.
        candidates = matches()
    if len(candidates) != 1:
        names = ", ".join(p.name for p in candidates)
        raise ValueError(f"Keep one template for this purpose. Found {len(candidates)}: {names}")
    try:
        _check_office_file(candidates[0], purpose)
    except (OSError, BadZipFile, KeyError, RuntimeError, ValueError) as exc:
        raise ValueError(f"Check the existing file {candidates[0].name}: {exc}") from exc


def _seed_layout(folder: Path, directories: list[Path], identity: os.stat_result) -> None:
    # The project generator recognizes a template root up to two levels below Settings.
    # Do not add a second skeleton beside a complete or partially customized site layout.
    candidates = []
    level = [folder]
    for depth in range(3):
        next_level = []
        for parent in level:
            require_safe_output_path(parent)
            found = []
            for expected in REQUIRED_TEMPLATE_PATHS:
                child = parent / expected
                require_safe_output_path(child)
                if child.is_dir():
                    found.append(expected)
            if found:
                candidates.append((parent, len(found) == len(REQUIRED_TEMPLATE_PATHS)))
            elif depth < 2:
                next_level.extend(p for p in parent.iterdir() if p.is_dir())
        level = next_level
    if len(candidates) > 1:
        raise ValueError("Multiple project layouts. Review: " + ", ".join(str(p) for p, _ in candidates))
    if candidates:
        existing, complete = candidates[0]
        if existing == folder or not any(existing in (folder / rel).parents for rel in directories):
            if not complete:
                raise ValueError(f"Existing layout is incomplete. Restore missing project subfolders in {existing}.")
            return
    for rel in directories:
        parent = folder
        for part in rel.parts:
            dest = parent / part
            with _pinned_directory(parent):
                _check_folder(folder, identity)
                require_safe_output_path(dest)
                dest.mkdir(exist_ok=True)
            parent = dest


def seed_browser_templates(template_dir: Path, bundle: Path, *,
                           overrides: dict[str, Path] | None = None) -> list[str]:
    """Return actionable setup warnings; retain all previously registered destinations."""
    try:
        require_safe_output_path(template_dir)
        identity = template_dir.stat()
        if not stat.S_ISDIR(identity.st_mode):
            raise NotADirectoryError(template_dir)
    except (OSError, ValueError) as exc:
        return [f"Restore access to the registered Template folder {template_dir}: {exc}"]
    try:
        templates, directories = _read_bundle(bundle)
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, BadZipFile) as exc:
        return [f"Check the template package at {bundle}: {exc}"]

    warnings = []
    for purpose, (name, data) in templates.items():
        override = (overrides or {}).get(purpose)
        if override is not None:
            try:
                _check_office_file(override, purpose)
            except (OSError, BadZipFile, KeyError, RuntimeError, ValueError) as exc:
                warnings.append(f"{_PURPOSES[purpose]}: check the configured template {override}: {exc}")
            continue
        try:
            _check_folder(template_dir, identity)
            _seed_file(template_dir, purpose, name, data, identity)
        except (OSError, ValueError) as exc:
            warnings.append(f"{_PURPOSES[purpose]} in {template_dir}: {exc}")
    try:
        _seed_layout(template_dir, directories, identity)
    except (OSError, ValueError) as exc:
        warnings.append(f"Project folder layout in {template_dir}: {exc}")
    return warnings
