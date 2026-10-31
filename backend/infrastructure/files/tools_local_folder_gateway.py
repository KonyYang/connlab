"""Enumerate one native-selected tree and publish verified copies without replacement."""
import os
from pathlib import Path
import shutil
import stat
import tempfile
from typing import Callable

from backend.application.tools_folder_encryption_service import (
    LocalFolderCandidate, MAX_FOLDER_FILES, local_folder_skip_reason,
)
from backend.application.tools_service import ToolsError


def _reparse(path: Path) -> bool:
    value = path.lstat()
    return stat.S_ISLNK(value.st_mode) or bool(getattr(value, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT)


class ToolsLocalFolderGateway:
    def __init__(self, folder: Path):
        folder = Path(folder)
        if not folder.is_absolute() or _reparse(folder) or not folder.is_dir():
            raise ToolsError("Choose an existing folder, not a shortcut or linked folder.")
        self.root = folder.resolve(strict=True)
        self._sources = {}
        self._directories = {self.root: self._directory_identity(self.root)}

    def scan(self) -> list[LocalFolderCandidate]:
        result = []
        pending = [self.root]
        supported = 0
        while pending:
            folder = pending.pop()
            self._check_location(folder)
            with os.scandir(folder) as entries:
                for entry in sorted(entries, key=lambda value: value.name.casefold()):
                    path = Path(entry.path)
                    relative = path.relative_to(self.root).as_posix()
                    if _reparse(path):
                        result.append(LocalFolderCandidate(path, relative, "Linked files and folders are skipped."))
                    elif entry.is_dir(follow_symlinks=False):
                        if not entry.name.startswith(".connlab-"):
                            self._directories[path] = self._directory_identity(path)
                            pending.append(path)
                    elif entry.is_file(follow_symlinks=False):
                        result.append(LocalFolderCandidate(path, relative))
                        self._sources[path] = self._identity(path)
                        if not local_folder_skip_reason(path):
                            supported += 1
        if supported > MAX_FOLDER_FILES:
            raise ToolsError(f"Choose a folder with at most {MAX_FOLDER_FILES} Office files.")
        return result

    def create_copy(self, source: Path, encrypt: Callable[..., Path]) -> Path:
        self._check_source(source)
        # Same-volume staging enables no-replace publication. Windows rename
        # rejects existing targets and also works on volumes without hard links.
        with tempfile.TemporaryDirectory(prefix=".connlab-encryption-", dir=source.parent) as temporary:
            stage = Path(temporary) / source.name
            working_source = Path(temporary) / "source" / source.name
            working_source.parent.mkdir()
            shutil.copyfile(source, working_source)
            self._check_source(source)
            # Office may update legacy input metadata even when SaveChanges=False.
            # Only an owned working copy is ever opened by the Office adapter.
            encrypt(source_path=working_source, output_path=stage)
            self._check_source(source)
            for number in range(10000):
                suffix = f" ({number})" if number else ""
                target = source.with_name(f"{source.stem}_Secured{suffix}{source.suffix}")
                try:
                    if os.name == "nt":
                        os.rename(stage, target)
                    else:
                        os.link(stage, target)
                except FileExistsError:
                    continue
                return target
        raise ToolsError("Too many encrypted copies already exist for this file.")

    @staticmethod
    def _directory_identity(path: Path):
        value = path.stat()
        return value.st_dev, value.st_ino

    @staticmethod
    def _identity(path: Path):
        value = path.stat()
        return value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns

    def _check_location(self, path: Path) -> None:
        if not path.resolve(strict=True).is_relative_to(self.root):
            raise ToolsError("The selected folder changed. Choose it again.")
        current = path
        while current.is_relative_to(self.root):
            if _reparse(current):
                raise ToolsError("Linked files and folders are not processed.")
            if current in self._directories and self._directory_identity(current) != self._directories[current]:
                raise ToolsError("The selected folder changed. Choose it again.")
            if current == self.root:
                break
            current = current.parent

    def _check_source(self, path: Path) -> None:
        self._check_location(path)
        if self._identity(path) != self._sources[path]:
            raise ToolsError("The source file changed while processing. Choose the folder again.")
