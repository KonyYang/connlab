"""Read-only Excel workbook gateway for Office integration."""

from __future__ import annotations

import re
import zipfile
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree

from backend.infrastructure.office.models import (
    LtrWorkbookFormat,
    LtrWorkbookSnapshot,
)
from backend.modules.ltr import LtrNumberError, parse_ltr_number


class LtrWorkbookGatewayError(ValueError):
    """Base error for read-only LTR workbook snapshot failures."""


class UnsupportedLtrWorkbookError(LtrWorkbookGatewayError):
    """Raised when the workbook format or layout is unsupported."""


class UnreadableLtrWorkbookError(LtrWorkbookGatewayError):
    """Raised when a workbook exists but cannot be read."""


class ExcelWorkbookGateway:
    """Read workbook metadata and LTR numbers without writing."""

    def read_workbook(self, source_path: Path) -> object:
        """Read a generic workbook through the LTR snapshot path."""
        return self.read_ltr_workbook_snapshot(source_path)

    def read_ltr_workbook_snapshot(self, source_path: Path) -> LtrWorkbookSnapshot:
        """Read workbook metadata and existing LTR numbers without writing."""
        path = Path(source_path)
        if not path.is_file():
            raise FileNotFoundError(f"LTR workbook does not exist: {path}")

        workbook_format = _workbook_format(path)
        if workbook_format is LtrWorkbookFormat.XLS:
            raise UnsupportedLtrWorkbookError(
                "Legacy .xls LTR workbook snapshot requires a later adapter task."
            )
        if workbook_format is LtrWorkbookFormat.UNSUPPORTED:
            raise UnsupportedLtrWorkbookError(
                f"Unsupported LTR workbook format: {path.suffix or '<none>'}"
            )

        stat = path.stat()
        sheet_names, sheet_xml_paths = _read_xlsx_workbook_manifest(path)
        ltr_numbers: list[str] = []
        readable_sheets: list[str] = []
        shared_strings = _read_xlsx_shared_strings(path)
        for sheet_name, sheet_xml_path in zip(sheet_names, sheet_xml_paths, strict=True):
            values = _read_xlsx_sheet_values(path, sheet_xml_path, shared_strings)
            readable_sheets.append(sheet_name)
            ltr_numbers.extend(_extract_ltr_numbers(values))

        return LtrWorkbookSnapshot(
            workbook_path=path,
            workbook_format=workbook_format,
            size_bytes=stat.st_size,
            modified_time=datetime.fromtimestamp(stat.st_mtime),
            sheet_names=tuple(sheet_names),
            readable_sheet_names=tuple(readable_sheets),
            sheet_strategy=_sheet_strategy(sheet_names),
            existing_ltr_numbers=tuple(dict.fromkeys(ltr_numbers)),
        )


def _workbook_format(path: Path) -> LtrWorkbookFormat:
    """Return the workbook format from the extension."""
    suffix = path.suffix.lower()
    if suffix == ".xlsx":
        return LtrWorkbookFormat.XLSX
    if suffix == ".xls":
        return LtrWorkbookFormat.XLS
    return LtrWorkbookFormat.UNSUPPORTED


def _read_xlsx_workbook_manifest(path: Path) -> tuple[list[str], list[str]]:
    """Read sheet names and XML paths from an XLSX package."""
    try:
        with zipfile.ZipFile(path) as archive:
            workbook_root = ElementTree.fromstring(archive.read("xl/workbook.xml"))
            rels_root = ElementTree.fromstring(
                archive.read("xl/_rels/workbook.xml.rels")
            )
    except (KeyError, OSError, zipfile.BadZipFile, ElementTree.ParseError) as exc:
        raise UnreadableLtrWorkbookError(f"Unable to read XLSX workbook: {path}") from exc

    relationships = {
        rel.attrib["Id"]: rel.attrib["Target"]
        for rel in rels_root
        if "Id" in rel.attrib and "Target" in rel.attrib
    }
    sheet_names: list[str] = []
    sheet_xml_paths: list[str] = []
    for sheet in workbook_root.findall(".//{*}sheet"):
        name = sheet.attrib.get("name")
        relation_id = sheet.attrib.get(
            "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
        )
        target = relationships.get(relation_id or "")
        if not name or not target:
            continue
        sheet_names.append(name)
        sheet_xml_paths.append(_normalize_xlsx_target(target))
    if not sheet_names:
        raise UnsupportedLtrWorkbookError("XLSX workbook has no readable worksheets.")
    return sheet_names, sheet_xml_paths


def _read_xlsx_shared_strings(path: Path) -> list[str]:
    """Read shared strings from an XLSX package."""
    try:
        with zipfile.ZipFile(path) as archive:
            root = ElementTree.fromstring(archive.read("xl/sharedStrings.xml"))
    except KeyError:
        return []
    except (OSError, zipfile.BadZipFile, ElementTree.ParseError) as exc:
        raise UnreadableLtrWorkbookError(
            f"Unable to read XLSX shared strings: {path}"
        ) from exc
    return [
        "".join(text.text or "" for text in item.findall(".//{*}t"))
        for item in root.findall(".//{*}si")
    ]


def _read_xlsx_sheet_values(
    path: Path,
    sheet_xml_path: str,
    shared_strings: list[str],
) -> list[str]:
    """Read plain cell values from one XLSX worksheet."""
    try:
        with zipfile.ZipFile(path) as archive:
            root = ElementTree.fromstring(archive.read(sheet_xml_path))
    except (KeyError, OSError, zipfile.BadZipFile, ElementTree.ParseError) as exc:
        raise UnreadableLtrWorkbookError(
            f"Unable to read XLSX worksheet: {sheet_xml_path}"
        ) from exc

    values: list[str] = []
    for cell in root.findall(".//{*}c"):
        value_node = cell.find("{*}v")
        inline_node = cell.find("{*}is/{*}t")
        if inline_node is not None and inline_node.text:
            values.append(inline_node.text)
            continue
        if value_node is None or value_node.text is None:
            continue
        if cell.attrib.get("t") == "s":
            index = int(value_node.text)
            if 0 <= index < len(shared_strings):
                values.append(shared_strings[index])
        else:
            values.append(value_node.text)
    return values


def _extract_ltr_numbers(values: list[str]) -> list[str]:
    """Extract supported LTR numbers from worksheet cell values."""
    numbers: list[str] = []
    for value in values:
        for candidate in re.findall(r"\b(?:DL-\d{4}-\d{2}-\d{3}[A-Z0-9]*|W[A-Z0-9]+)\b", value, flags=re.IGNORECASE):
            try:
                numbers.append(parse_ltr_number(candidate).normalized)
            except LtrNumberError:
                continue
    return numbers


def _normalize_xlsx_target(target: str) -> str:
    """Normalize a workbook relationship target into a ZIP path."""
    target = target.lstrip("/")
    if target.startswith("xl/"):
        return target
    return f"xl/{target}"


def _sheet_strategy(sheet_names: list[str]) -> str:
    """Describe the visible workbook sheet strategy."""
    if any(re.fullmatch(r"\d{4}", name) for name in sheet_names):
        return "year_sheets"
    if any(re.fullmatch(r"\d{4}[-_]\d{2}", name) for name in sheet_names):
        return "year_month_sheets"
    return "flat_or_unknown"
