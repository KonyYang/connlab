"""Read-only Excel workbook gateway for Office integration."""

from __future__ import annotations

import re
import zipfile
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree

from backend.infrastructure.office.models import (
    ExcelTabularReadResult,
    ExcelStructureProbeResult,
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

    def probe_structure(
        self,
        source_path: Path,
        *,
        expected_headers: tuple[str, ...],
        expected_date_headers: tuple[str, ...] = (),
        expected_sheet_names: tuple[str, ...] = (),
        expected_sheet_name_patterns: tuple[str, ...] = (),
    ) -> ExcelStructureProbeResult:
        """Probe workbook sheets and headers without writing."""
        path = Path(source_path)
        if not path.is_file():
            raise FileNotFoundError(f"Excel workbook does not exist: {path}")
        if _workbook_format(path) is not LtrWorkbookFormat.XLSX:
            raise UnsupportedLtrWorkbookError(
                f"Excel structure probe supports .xlsx only: {path.suffix or '<none>'}"
            )
        sheet_names, sheet_xml_paths = _read_xlsx_workbook_manifest(path)
        matched_pairs = _matching_sheets(
            sheet_names,
            sheet_xml_paths,
            expected_sheet_names,
            expected_sheet_name_patterns,
        )
        shared_strings = _read_xlsx_shared_strings(path)
        observed_headers: list[str] = []
        for _sheet_name, sheet_xml_path in matched_pairs:
            rows = _read_xlsx_sheet_rows(path, sheet_xml_path, shared_strings)
            observed_headers.extend(_first_non_empty_row(rows))
        normalized_observed = {_normalize_header(value) for value in observed_headers}
        missing_headers = tuple(
            header
            for header in expected_headers
            if _normalize_header(header) not in normalized_observed
        )
        missing_date_headers = tuple(
            header
            for header in expected_date_headers
            if _normalize_header(header) not in normalized_observed
        )
        failure = _probe_failure(matched_pairs, missing_headers, missing_date_headers)
        return ExcelStructureProbeResult(
            workbook_path=path,
            sheet_names=tuple(sheet_names),
            matched_sheet_names=tuple(name for name, _xml_path in matched_pairs),
            observed_headers=tuple(dict.fromkeys(observed_headers)),
            missing_headers=missing_headers,
            missing_date_headers=missing_date_headers,
            valid=failure is None,
            failure_reason=failure,
        )

    def read_tabular_rows(
        self,
        source_path: Path,
        *,
        expected_headers: tuple[str, ...],
        expected_sheet_names: tuple[str, ...] = (),
        expected_sheet_name_patterns: tuple[str, ...] = (),
    ) -> ExcelTabularReadResult:
        """Read header-aligned worksheet rows from matching worksheets."""
        path = Path(source_path)
        if not path.is_file():
            raise FileNotFoundError(f"Excel workbook does not exist: {path}")
        if _workbook_format(path) is not LtrWorkbookFormat.XLSX:
            raise UnsupportedLtrWorkbookError(
                f"Excel tabular read supports .xlsx only: {path.suffix or '<none>'}"
            )
        sheet_names, sheet_xml_paths = _read_xlsx_workbook_manifest(path)
        matched_pairs = _matching_sheets(
            sheet_names,
            sheet_xml_paths,
            expected_sheet_names,
            expected_sheet_name_patterns,
        )
        if not matched_pairs:
            raise UnsupportedLtrWorkbookError(
                "No worksheet matched the expected sheet rules."
            )
        shared_strings = _read_xlsx_shared_strings(path)
        canonical_headers = tuple(expected_headers)
        normalized_canonical = [_normalize_header(value) for value in canonical_headers]
        collected_rows: list[dict[str, str]] = []
        matched_sheet_names: list[str] = []
        for sheet_name, sheet_xml_path in matched_pairs:
            rows = _read_xlsx_sheet_rows(path, sheet_xml_path, shared_strings)
            header_row = _first_non_empty_row(rows)
            if not header_row:
                continue
            index_map = _header_index_map(
                header_row,
                canonical_headers,
                normalized_canonical,
            )
            if index_map is None:
                continue
            matched_sheet_names.append(sheet_name)
            for raw_row in rows:
                row = [_normalize_cell(value) for value in raw_row]
                if not any(row):
                    continue
                # Skip the header row itself.
                if _row_is_header(row, header_row):
                    continue
                mapped: dict[str, str] = {}
                has_value = False
                for header, index in zip(canonical_headers, index_map, strict=True):
                    value = row[index] if index < len(row) else ""
                    mapped[header] = value
                    has_value = has_value or bool(value)
                if has_value:
                    mapped["__sheet_name"] = sheet_name
                    collected_rows.append(mapped)
        if not matched_sheet_names:
            raise UnsupportedLtrWorkbookError("Expected headers were not found.")
        return ExcelTabularReadResult(
            workbook_path=path,
            matched_sheet_names=tuple(matched_sheet_names),
            headers=canonical_headers,
            rows=tuple(collected_rows),
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


def _read_xlsx_sheet_rows(
    path: Path,
    sheet_xml_path: str,
    shared_strings: list[str],
) -> list[list[str]]:
    """Read plain worksheet rows from one XLSX sheet."""
    try:
        with zipfile.ZipFile(path) as archive:
            root = ElementTree.fromstring(archive.read(sheet_xml_path))
    except (KeyError, OSError, zipfile.BadZipFile, ElementTree.ParseError) as exc:
        raise UnreadableLtrWorkbookError(
            f"Unable to read XLSX worksheet: {sheet_xml_path}"
        ) from exc
    rows: list[list[str]] = []
    for row in root.findall(".//{*}row"):
        rows.append([_cell_text(cell, shared_strings) for cell in row.findall("{*}c")])
    return rows


def _cell_text(cell: ElementTree.Element, shared_strings: list[str]) -> str:
    """Return a string value from one XLSX cell node."""
    inline_node = cell.find("{*}is/{*}t")
    if inline_node is not None and inline_node.text:
        return inline_node.text.strip()
    value_node = cell.find("{*}v")
    if value_node is None or value_node.text is None:
        return ""
    if cell.attrib.get("t") == "s":
        index = int(value_node.text)
        if 0 <= index < len(shared_strings):
            return shared_strings[index].strip()
        return ""
    return value_node.text.strip()


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


def _matching_sheets(
    sheet_names: list[str],
    sheet_xml_paths: list[str],
    expected_sheet_names: tuple[str, ...],
    expected_sheet_name_patterns: tuple[str, ...],
) -> list[tuple[str, str]]:
    """Return sheet names and paths matching probe rules."""
    if not expected_sheet_names and not expected_sheet_name_patterns:
        return list(zip(sheet_names, sheet_xml_paths, strict=True))
    exact = {name.lower() for name in expected_sheet_names}
    patterns = [
        re.compile(pattern, flags=re.IGNORECASE)
        for pattern in expected_sheet_name_patterns
    ]
    matched: list[tuple[str, str]] = []
    for sheet_name, sheet_xml_path in zip(sheet_names, sheet_xml_paths, strict=True):
        if sheet_name.lower() in exact or any(
            pattern.fullmatch(sheet_name) for pattern in patterns
        ):
            matched.append((sheet_name, sheet_xml_path))
    return matched


def _first_non_empty_row(rows: list[list[str]]) -> list[str]:
    """Return the first row with at least one non-empty value."""
    for row in rows:
        cleaned = [value.strip() for value in row if value.strip()]
        if cleaned:
            return cleaned
    return []


def _normalize_header(value: str) -> str:
    """Normalize a workbook header for comparison."""
    return re.sub(r"\s+", " ", value.strip().lower())


def _probe_failure(
    matched_pairs: list[tuple[str, str]],
    missing_headers: tuple[str, ...],
    missing_date_headers: tuple[str, ...],
) -> str | None:
    """Return a probe failure reason, or None when structure is acceptable."""
    if not matched_pairs:
        return "No worksheet matched the expected sheet rules."
    if missing_headers:
        return f"Missing required headers: {', '.join(missing_headers)}"
    if missing_date_headers:
        return f"Missing required date headers: {', '.join(missing_date_headers)}"
    return None


def _header_index_map(
    header_row: list[str],
    canonical_headers: tuple[str, ...],
    normalized_canonical: list[str],
) -> tuple[int, ...] | None:
    """Return canonical header indexes for one sheet header row."""
    normalized_header = [_normalize_header(value) for value in header_row]
    indexes: list[int] = []
    for normalized_name in normalized_canonical:
        try:
            indexes.append(normalized_header.index(normalized_name))
        except ValueError:
            return None
    return tuple(indexes)


def _normalize_cell(value: str) -> str:
    """Return stripped cell text."""
    return value.strip()


def _row_is_header(row: list[str], header_row: list[str]) -> bool:
    """Return whether a row equals the header row after trimming."""
    if len(row) < len(header_row):
        return False
    return all(
        _normalize_cell(row[index]) == _normalize_cell(header_row[index])
        for index in range(len(header_row))
    )


def _sheet_strategy(sheet_names: list[str]) -> str:
    """Describe the visible workbook sheet strategy."""
    if any(re.fullmatch(r"\d{4}", name) for name in sheet_names):
        return "year_sheets"
    if any(re.fullmatch(r"\d{4}[-_]\d{2}", name) for name in sheet_names):
        return "year_month_sheets"
    return "flat_or_unknown"
