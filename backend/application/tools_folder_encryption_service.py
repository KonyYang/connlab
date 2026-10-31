"""Batch the existing copy-only Office policy for local siblings and upload compatibility."""
from dataclasses import dataclass
import logging
from pathlib import Path, PurePosixPath
import re
import unicodedata
from typing import Callable, Protocol, Sequence

from backend.application.tools_service import ToolsError, ToolsService

MAX_FOLDER_FILES = 500
SUPPORTED_FOLDER_SUFFIXES = frozenset({".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"})
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class FolderEncryptionEntry:
    relative_path: str
    status: str
    reason: str = ""
    output_path: Path | None = None


class FolderArchivePort(Protocol):
    def write(self, output: Path, entries: Sequence[FolderEncryptionEntry]) -> None: ...


@dataclass(frozen=True)
class LocalFolderCandidate:
    source_path: Path
    relative_path: str
    skip_reason: str = ""


class LocalFolderPort(Protocol):
    root: Path

    def scan(self) -> Sequence[LocalFolderCandidate]: ...

    def create_copy(self, source: Path, encrypt: Callable[..., Path]) -> Path: ...


def local_folder_skip_reason(path: Path) -> str:
    if (path.suffix.lower() not in SUPPORTED_FOLDER_SUFFIXES
        or path.name.startswith(("~$", ".connlab-"))
        or re.search(r"(?i)_secured(?: \(\d+\))?$", path.stem)):
        return "Temporary, already secured, or unsupported file."
    return ""


class ToolsLocalFolderEncryptionService:
    """Apply unchanged Office rules to separate siblings selected on this computer."""

    def __init__(self, *, tools: ToolsService, files: LocalFolderPort):
        self._tools = tools
        self._files = files

    def encrypt(self) -> dict:
        candidates = self._files.scan()
        entries = []
        for candidate in candidates:
            path = candidate.source_path
            reason = candidate.skip_reason or local_folder_skip_reason(path)
            if reason:
                entries.append({"file": candidate.relative_path, "status": "Skipped", "reason": reason})
                continue
            try:
                output = self._files.create_copy(path, self._tools.encrypt_copy)
            except Exception as exc:
                logger.warning("Local folder encryption failed for %s", candidate.relative_path, exc_info=True)
                reason = str(exc) if isinstance(exc, ToolsError) and str(exc).startswith("Excel files must start") else (
                    "Could not save an encrypted copy. Close the file in Office and check its format and folder access.")
                entries.append({"file": candidate.relative_path, "status": "Failed", "reason": reason})
            else:
                entries.append({"file": candidate.relative_path, "status": "Encrypted",
                    "output": str(output.relative_to(self._files.root)), "reason": ""})
        return {"cancelled": False, "folder": str(self._files.root), "entries": entries,
            "summary": {key: sum(entry["status"] == status for entry in entries)
                for key, status in (("succeeded", "Encrypted"), ("failed", "Failed"), ("skipped", "Skipped"))}}


def secured_relative_path(path: PurePosixPath) -> PurePosixPath:
    return path.with_name(f"{path.stem}_Secured{path.suffix}")


def validate_folder_paths(names: object) -> tuple[PurePosixPath, ...]:
    """Validate archive identities before any uploads are written or Office is started."""
    if not isinstance(names, list) or not 1 <= len(names) <= MAX_FOLDER_FILES:
        raise ToolsError(f"Select between 1 and {MAX_FOLDER_FILES} files in one folder.")
    paths = []
    seen = set()
    roots = set()
    for name in names:
        if not isinstance(name, str) or len(name) > 1024 or "\\" in name:
            raise ToolsError("Folder file names must be safe relative paths.")
        parts = name.split("/")
        if len(parts) < 2 or any(
            part in {"", ".", ".."} or len(part) > 240 or part.endswith((" ", "."))
            or re.search(r'[<>:"|?*\x00-\x1f\x7f]', part)
            or re.fullmatch(r"(?i)(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?", part)
            for part in parts
        ):
            raise ToolsError("Folder file names must be safe relative paths.")
        key = unicodedata.normalize("NFC", name).casefold()
        if key in seen:
            raise ToolsError("The folder contains duplicate file paths. Rename them and select it again.")
        seen.add(key)
        roots.add(unicodedata.normalize("NFC", parts[0]).casefold())
        paths.append(PurePosixPath(name))
    if len(roots) != 1:
        raise ToolsError("Select one folder at a time.")
    targets = [secured_relative_path(path) for path in paths
               if path.suffix.lower() in SUPPORTED_FOLDER_SUFFIXES and not path.name.startswith("~$")]
    target_keys = {unicodedata.normalize("NFC", str(path)).casefold() for path in targets}
    if any(unicodedata.normalize("NFC", str(parent)).casefold() in target_keys
           for path in targets for parent in path.parents):
        raise ToolsError("Encrypted file and folder names would conflict. Rename them and select the folder again.")
    return tuple(paths)


class ToolsFolderEncryptionService:
    def __init__(self, *, tools: ToolsService, archives: FolderArchivePort):
        self._tools = tools
        self._archives = archives

    def encrypt(self, sources: Sequence[tuple[Path, PurePosixPath]], *, output: Path) -> dict[str, int]:
        entries = []
        for index, (source, relative) in enumerate(sources):
            if relative.suffix.lower() not in SUPPORTED_FOLDER_SUFFIXES or relative.name.startswith("~$"):
                entries.append(FolderEncryptionEntry(str(relative), "Skipped", "Not a supported Office document or an Office temporary file."))
                continue
            target = output.parent / "encrypted" / str(index) / secured_relative_path(relative).name
            try:
                self._tools.encrypt_copy(source_path=source, output_path=target)
            except Exception as exc:
                logger.warning("Folder encryption failed for item %s", index, exc_info=True)
                reason = str(exc) if isinstance(exc, ToolsError) and str(exc).startswith("Excel files must start") else (
                    "Could not encrypt this file. Close it in Office and check its format or existing protection.")
                entries.append(FolderEncryptionEntry(str(relative), "Failed", reason))
            else:
                entries.append(FolderEncryptionEntry(str(relative), "Encrypted", output_path=target))
        if not any(entry.status != "Skipped" for entry in entries):
            raise ToolsError("No supported Word, Excel or PowerPoint files were found in this folder.")
        self._archives.write(output, entries)
        return {key: sum(entry.status == status for entry in entries)
                for key, status in (("succeeded", "Encrypted"), ("failed", "Failed"), ("skipped", "Skipped"))}
