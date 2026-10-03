"""Read equipment references from a project EquipmentID.docx without mutation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import re
import stat
import tempfile
from zipfile import BadZipFile

from docx import Document
from docx.opc.exceptions import PackageNotFoundError
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph
from lxml.etree import XMLSyntaxError

from backend.application.equipment_report_update_service import equipment_reference_key
from backend.infrastructure.office.office_protected_document_gateway import (
    ProtectedWordPackageGateway,
)


@dataclass(frozen=True, slots=True)
class EquipmentIdDocumentReadResult:
    source_path: Path
    references: tuple[str, ...]


class EquipmentIdDocumentReader:
    """Extract ordered, case-insensitively unique equipment references."""

    def __init__(self, *, protected_package_gateway=None) -> None:
        self._protected_package_gateway = (
            protected_package_gateway or ProtectedWordPackageGateway()
        )

    def read(self, source_path: Path) -> EquipmentIdDocumentReadResult:
        path = Path(source_path)
        self.validate_path(path)
        if path.suffix.casefold() != ".docx" or not path.is_file():
            raise FileNotFoundError(f"EquipmentID.docx does not exist: {path}")
        with self._protected_package_gateway.readable_copy(path) as readable_path:
            try:
                document = Document(readable_path)
            except (BadZipFile, PackageNotFoundError, KeyError, ValueError, XMLSyntaxError) as exc:
                raise ValueError("Equipment selection document cannot be read. Choose a valid .docx.") from exc
            candidates: list[str] = []
            for block in document.element.body:
                if block.tag == qn("w:p"):
                    candidates.append(Paragraph(block, document).text)
                elif block.tag == qn("w:tbl"):
                    candidates.extend(cell.text for row in Table(block, document).rows for cell in row.cells)
        references = _unique_references(candidates)
        if not references:
            raise ValueError("EquipmentID.docx does not contain equipment references.")
        return EquipmentIdDocumentReadResult(path, references)

    def validate_path(self, path: Path) -> None:
        _checked_parent_identity(path.parent)
        try:
            info = path.lstat()
        except FileNotFoundError:
            return
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT:
            raise OSError("EquipmentID.docx must not redirect to another file.")

    def save_missing(
        self, source_path: Path, *, content: bytes | None = None,
        references_text: str | None = None,
    ) -> EquipmentIdDocumentReadResult:
        """Publish a validated, complete selection without replacing any existing path."""
        path = Path(source_path)
        if path.name != "EquipmentID.docx":
            raise ValueError("Equipment selection must use EquipmentID.docx.")
        if (content is None) == (references_text is None):
            raise ValueError("Choose a document or paste equipment IDs, not both.")
        parent_identity = _checked_parent_identity(path.parent)
        try:
            path.lstat()
        except FileNotFoundError:
            pass
        else:
            raise FileExistsError("EquipmentID.docx now exists. Retry without importing.")
        descriptor, name = tempfile.mkstemp(prefix=".equipment-selection-", suffix=".docx", dir=path.parent)
        staged = Path(name)
        try:
            with os.fdopen(descriptor, "wb") as stream:
                if content is not None:
                    stream.write(content)
                else:
                    references = _unique_references((references_text or "",))
                    if not references:
                        raise ValueError("Enter at least one equipment ID.")
                    document = Document()
                    for reference in references:
                        document.add_paragraph(reference)
                    document.save(stream)
                stream.flush()
                os.fsync(stream.fileno())
            try:
                selection = self.read(staged)
            except Exception as exc:
                raise ValueError("Equipment selection document cannot be read. Choose a valid .docx.") from exc
            if _checked_parent_identity(path.parent) != parent_identity:
                raise OSError("The project folder changed during equipment selection import.")
            # A hard link exposes the already-complete package atomically and fails on collision.
            os.link(staged, path)
            return EquipmentIdDocumentReadResult(path, selection.references)
        finally:
            if _checked_parent_identity(path.parent) != parent_identity:
                raise OSError("The project folder changed. Retain equipment import temporary files for review.")
            staged.unlink(missing_ok=True)


def _unique_references(candidates) -> tuple[str, ...]:
    references: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        for part in re.split(r"[\r\n,;，；]+", candidate):
            value = _clean_reference(part)
            if not value:
                continue
            key = equipment_reference_key(value)
            if key in seen:
                continue
            seen.add(key)
            references.append(value)
    return tuple(references)


def _checked_parent_identity(parent: Path) -> tuple[int, int]:
    for directory in (parent, *parent.parents):
        info = directory.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT:
            raise OSError("The project folder must not redirect to another directory.")
    if not parent.is_dir():
        raise FileNotFoundError("The registered project folder is unavailable.")
    info = parent.stat()
    return info.st_dev, info.st_ino


def _clean_reference(value: str) -> str:
    return re.sub(r"\s+", " ", value.replace("\x07", " ").strip())
